import logging

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.database.models import User
from app.models.auth_model import (
    ChangePasswordRequest,
    UserProfileUpdateRequest,
)
from app.repositories import user_repository
from app.services import gcs_storage_service
from app.services.observability_service import emit_event


logger = logging.getLogger(__name__)


class ProfileError(RuntimeError):
    """Safe account-profile operation error."""


class ProfileValidationError(ProfileError):
    """Profile input is invalid."""


class ProfileStorageError(ProfileError):
    """Profile image storage is unavailable."""


def update_profile(
    db: Session,
    user: User,
    data: UserProfileUpdateRequest
) -> User:
    user.full_name = data.full_name
    return user_repository.save_user(db, user)


def change_password(
    db: Session,
    user: User,
    data: ChangePasswordRequest
) -> None:
    if not verify_password(
        data.current_password,
        user.hashed_password
    ):
        raise ProfileValidationError(
            "Current password is incorrect"
        )

    user.hashed_password = hash_password(data.new_password)
    user.token_version += 1
    user_repository.save_user(db, user)


def upload_profile_image(
    db: Session,
    user: User,
    content: bytes,
    content_type: str | None
) -> User:
    previous_key = user.profile_image_key

    try:
        stored = gcs_storage_service.put_profile_image(
            user_id=user.id,
            content=content,
            content_type=content_type
        )
    except gcs_storage_service.GCSValidationError as error:
        raise ProfileValidationError(str(error)) from error
    except gcs_storage_service.GCSStorageError as error:
        _storage_failure("profile_image_upload", error)
        raise ProfileStorageError(
            "Profile image storage is unavailable"
        ) from error

    user.profile_image_key = stored.key

    try:
        saved_user = user_repository.save_user(db, user)
    except SQLAlchemyError:
        db.rollback()
        _delete_after_failure(stored.key, user.id)
        raise

    if previous_key and previous_key != stored.key:
        _delete_after_success(previous_key, user.id)

    return saved_user


def remove_profile_image(
    db: Session,
    user: User
) -> User:
    previous_key = user.profile_image_key
    if not previous_key:
        return user

    user.profile_image_key = None
    saved_user = user_repository.save_user(db, user)
    _delete_after_success(previous_key, user.id)
    return saved_user


def load_profile_image(user: User) -> tuple[bytes, str]:
    if not user.profile_image_key:
        raise ProfileValidationError(
            "Profile image is not available"
        )

    try:
        return gcs_storage_service.get_profile_image(
            user.profile_image_key,
            user.id
        )
    except gcs_storage_service.GCSValidationError as error:
        raise ProfileValidationError(
            "Profile image is not available"
        ) from error
    except gcs_storage_service.GCSStorageError as error:
        _storage_failure("profile_image_download", error)
        raise ProfileStorageError(
            "Profile image storage is unavailable"
        ) from error


def _delete_after_success(object_key: str, user_id: int) -> None:
    try:
        gcs_storage_service.delete_profile_image(
            object_key,
            user_id
        )
    except gcs_storage_service.GCSStorageError as error:
        _storage_failure("profile_image_cleanup", error)


def _delete_after_failure(object_key: str, user_id: int) -> None:
    try:
        gcs_storage_service.delete_profile_image(
            object_key,
            user_id
        )
    except gcs_storage_service.GCSStorageError as error:
        _storage_failure("profile_image_compensation", error)


def _storage_failure(operation: str, error: Exception) -> None:
    emit_event(
        "profile_storage_failure",
        severity="ERROR",
        operation=operation,
        outcome="failure",
        error_category=type(error).__name__
    )
