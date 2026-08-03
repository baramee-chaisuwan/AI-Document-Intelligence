from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import (
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from app.core.exceptions import (
    AuthenticationError,
    ConflictError
)
from app.core.security import (
    create_access_token,
    hash_password,
    verify_password
)
from app.database.models import User
from app.models.auth_model import (
    AccessTokenResponse,
    UserLoginRequest,
    UserRegisterRequest,
    UserRole
)
from app.repositories import user_repository


def register_user(
    db: Session,
    data: UserRegisterRequest
):

    if user_repository.get_user_by_email(
        db,
        data.email
    ):

        raise ConflictError(
            "A user with this email already exists"
        )

    user = User(
        email=data.email,
        full_name=data.full_name,
        hashed_password=hash_password(
            data.password
        ),
        role=UserRole.RECRUITER.value,
        is_active=True
    )

    try:

        return user_repository.create_user(
            db,
            user
        )

    except IntegrityError as error:

        db.rollback()

        raise ConflictError(
            "A user with this email already exists"
        ) from error


def authenticate_user(
    db: Session,
    data: UserLoginRequest
):

    user = user_repository.get_user_by_email(
        db,
        data.email
    )

    if (
        not user
        or not verify_password(
            data.password,
            user.hashed_password
        )
    ):

        raise AuthenticationError(
            "Invalid email or password"
        )

    if not user.is_active:

        raise AuthenticationError(
            "User account is inactive"
        )

    return AccessTokenResponse(
        access_token=create_access_token(
            user.id
        ),
        expires_in=(
            ACCESS_TOKEN_EXPIRE_MINUTES
            * 60
        )
    )
