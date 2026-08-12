from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.notification_type import NotificationType


class NotificationResponse(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    id: int
    type: NotificationType
    title: str
    message: str
    candidate_id: int | None
    is_read: bool
    created_at: datetime


class NotificationListResponse(BaseModel):

    notifications: list[NotificationResponse]
    unread_count: int = Field(ge=0)


class NotificationReadAllResponse(BaseModel):

    marked_read: int = Field(ge=0)
