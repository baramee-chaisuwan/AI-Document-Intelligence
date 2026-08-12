from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.database.database import get_db
from app.database.models import User
from app.models.notification_model import (
    NotificationListResponse,
    NotificationReadAllResponse,
    NotificationResponse
)
from app.services import notification_service


router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"]
)


@router.get(
    "",
    response_model=NotificationListResponse,
    summary="Get current user's notifications"
)
def get_notifications(
    limit: int = Query(default=20, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    return notification_service.list_notifications(
        db,
        current_user.id,
        limit
    )


@router.patch(
    "/read-all",
    response_model=NotificationReadAllResponse,
    summary="Mark all current user's notifications as read"
)
def mark_all_notifications_read(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    return notification_service.mark_all_notifications_read(
        db,
        current_user.id
    )


@router.patch(
    "/{notification_id:int}/read",
    response_model=NotificationResponse,
    summary="Mark one current user's notification as read"
)
def mark_notification_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    return notification_service.mark_notification_read(
        db,
        notification_id,
        current_user.id
    )
