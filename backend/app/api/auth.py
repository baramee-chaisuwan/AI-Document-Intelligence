from fastapi import (
    APIRouter,
    Depends,
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
    ForgotPasswordRequest,
    MessageResponse,
    PasswordResetTokenResponse,
    ResetPasswordRequest,
    UserLoginRequest,
    UserRegisterRequest,
    UserResponse,
    VerifyResetOTPRequest
)
from app.services import (
    auth_service,
    password_reset_service
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
