from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.database.models import Notification


def create_notification(
    db: Session,
    notification: Notification
) -> Notification:

    db.add(notification)
    db.commit()
    db.refresh(notification)

    return notification


def get_notification_for_user(
    db: Session,
    notification_id: int,
    user_id: int
) -> Notification | None:

    return (
        db.query(Notification)
        .filter(
            Notification.id == notification_id,
            Notification.user_id == user_id
        )
        .first()
    )


def get_notification_by_event_key(
    db: Session,
    event_key: str
) -> Notification | None:

    return (
        db.query(Notification)
        .filter(Notification.event_key == event_key)
        .first()
    )


def list_notifications(
    db: Session,
    user_id: int,
    limit: int
) -> list[Notification]:

    return (
        db.query(Notification)
        .filter(Notification.user_id == user_id)
        .order_by(
            desc(Notification.created_at),
            desc(Notification.id)
        )
        .limit(limit)
        .all()
    )


def count_unread_notifications(
    db: Session,
    user_id: int
) -> int:

    return (
        db.query(Notification)
        .filter(
            Notification.user_id == user_id,
            Notification.is_read.is_(False)
        )
        .count()
    )


def mark_notification_read(
    db: Session,
    notification: Notification
) -> Notification:

    if not notification.is_read:
        notification.is_read = True
        db.add(notification)
        db.commit()
        db.refresh(notification)

    return notification


def mark_all_notifications_read(
    db: Session,
    user_id: int
) -> int:

    marked_read = (
        db.query(Notification)
        .filter(
            Notification.user_id == user_id,
            Notification.is_read.is_(False)
        )
        .update(
            {Notification.is_read: True},
            synchronize_session=False
        )
    )
    db.commit()

    return marked_read
