from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    Response,
    UploadFile,
    status
)
from sqlalchemy.orm import Session

from app.api.dependencies import (
    get_current_user
)
from app.database.database import get_db
from app.database.models import User
from app.models.auth_model import (
    AccessTokenResponse,
    ChangePasswordRequest,
    ForgotPasswordRequest,
    MessageResponse,
    PasswordResetTokenResponse,
    ResetPasswordRequest,
    UserLoginRequest,
    UserRegisterRequest,
    UserResponse,
    UserProfileUpdateRequest,
    VerifyResetOTPRequest
)
from app.services import (
    auth_service,
    password_reset_service,
    profile_service
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def register(
    data: UserRegisterRequest,
    db: Session = Depends(get_db)
):

    return auth_service.register_user(
        db,
        data
    )


@router.post(
    "/login",
    response_model=AccessTokenResponse
)
def login(
    data: UserLoginRequest,
    db: Session = Depends(get_db)
):

    return auth_service.authenticate_user(
        db,
        data
    )


@router.post(
    "/forgot-password",
    response_model=MessageResponse
)
def forgot_password(
    data: ForgotPasswordRequest,
    db: Session = Depends(get_db)
):

    return password_reset_service.request_password_reset(
        db,
        data
    )


@router.post(
    "/verify-reset-otp",
    response_model=PasswordResetTokenResponse
)
def verify_reset_otp(
    data: VerifyResetOTPRequest,
    db: Session = Depends(get_db)
):

    return password_reset_service.verify_reset_otp(
        db,
        data
    )


@router.post(
    "/reset-password",
    response_model=MessageResponse
)
def reset_password(
    data: ResetPasswordRequest,
    db: Session = Depends(get_db)
):

    return password_reset_service.reset_password(
        db,
        data
    )


@router.get(
    "/me",
    response_model=UserResponse
)
def me(
    current_user: User = Depends(
        get_current_user
    )
):

    return current_user


@router.patch(
    "/me",
    response_model=UserResponse
)
def update_me(
    data: UserProfileUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return profile_service.update_profile(
        db,
        current_user,
        data
    )


@router.post(
    "/me/profile-photo",
    response_model=UserResponse
)
async def upload_profile_photo(
    photo: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    content = await photo.read(
        5 * 1024 * 1024 + 1
    )
    return _profile_call(
        profile_service.upload_profile_image,
        db,
        current_user,
        content,
        photo.content_type
    )


@router.get("/me/profile-photo")
def get_profile_photo(
    current_user: User = Depends(get_current_user)
):
    content, content_type = _profile_call(
        profile_service.load_profile_image,
        current_user
    )
    return Response(
        content=content,
        media_type=content_type,
        headers={"Cache-Control": "private, no-store"}
    )


@router.delete(
    "/me/profile-photo",
    response_model=UserResponse
)
def delete_profile_photo(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return _profile_call(
        profile_service.remove_profile_image,
        db,
        current_user
    )


@router.post(
    "/change-password",
    response_model=MessageResponse
)
def change_password(
    data: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    _profile_call(
        profile_service.change_password,
        db,
        current_user,
        data
    )
    return MessageResponse(
        message="Password changed. Please sign in again."
    )


def _profile_call(operation, *args):
    try:
        return operation(*args)
    except profile_service.ProfileValidationError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error)
        ) from error
    except profile_service.ProfileStorageError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(error)
        ) from error
