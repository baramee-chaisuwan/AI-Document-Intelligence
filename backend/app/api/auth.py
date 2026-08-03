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
    UserLoginRequest,
    UserRegisterRequest,
    UserResponse
)
from app.services import auth_service


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
