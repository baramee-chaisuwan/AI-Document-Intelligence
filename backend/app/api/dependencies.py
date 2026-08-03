from fastapi import (
    Depends,
    HTTPException,
    status
)
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer
)
from sqlalchemy.orm import Session

from app.core.security import (
    InvalidTokenError,
    decode_access_token
)
from app.database.database import get_db
from app.database.models import User
from app.models.auth_model import UserRole
from app.repositories import user_repository


bearer_scheme = HTTPBearer(
    auto_error=False
)


def _credentials_exception():

    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={
            "WWW-Authenticate": "Bearer"
        }
    )


def get_current_user(
    credentials: HTTPAuthorizationCredentials
    | None = Depends(bearer_scheme),
    db: Session = Depends(get_db)
) -> User:

    if (
        credentials is None
        or credentials.scheme.lower()
        != "bearer"
    ):

        raise _credentials_exception()

    try:

        user_id = decode_access_token(
            credentials.credentials
        )

    except (
        InvalidTokenError,
        RuntimeError
    ):

        raise _credentials_exception()

    user = user_repository.get_user_by_id(
        db,
        user_id
    )

    if not user or not user.is_active:

        raise _credentials_exception()

    return user


def get_current_admin_user(
    current_user: User = Depends(
        get_current_user
    )
) -> User:

    if current_user.role != UserRole.ADMIN.value:

        raise HTTPException(
            status_code=(
                status.HTTP_403_FORBIDDEN
            ),
            detail="Admin access required"
        )

    return current_user


require_admin = get_current_admin_user
