from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.database.models import Notification
from app.models.notification_type import NotificationType
from app.repositories import notification_repository
from app.services.observability_service import emit_event


def list_notifications(
    db: Session,
    user_id: int,
    limit: int
) -> dict:

    return {
        "notifications": (
            notification_repository.list_notifications(
                db,
                user_id,
                limit
            )
        ),
        "unread_count": (
            notification_repository.count_unread_notifications(
                db,
                user_id
            )
        )
    }


def mark_notification_read(
    db: Session,
    notification_id: int,
    user_id: int
) -> Notification:

    notification = (
        notification_repository.get_notification_for_user(
            db,
            notification_id,
            user_id
        )
    )

    if notification is None:
        raise NotFoundError("Notification not found")

    return notification_repository.mark_notification_read(
        db,
        notification
    )


def mark_all_notifications_read(
    db: Session,
    user_id: int
) -> dict:

    return {
        "marked_read": (
            notification_repository.mark_all_notifications_read(
                db,
                user_id
            )
        )
    }


def notify_resume_completed_safely(
    db: Session,
    *,
    user_id: int | None,
    processing_job_id: int,
    candidate_id: int | None
) -> Notification | None:

    if user_id is None:
        return None

    return create_notification_safely(
        db,
        user_id=user_id,
        notification_type=(
            NotificationType.RESUME_PROCESSING_COMPLETED
        ),
        title="Resume processing completed",
        message=(
            "The resume was processed successfully and the candidate "
            "is ready for review."
        ),
        candidate_id=candidate_id,
        event_key=f"resume-processing:{processing_job_id}:completed"
    )


def notify_resume_failed_safely(
    db: Session,
    *,
    user_id: int | None,
    processing_job_id: int
) -> Notification | None:

    if user_id is None:
        return None

    return create_notification_safely(
        db,
        user_id=user_id,
        notification_type=(
            NotificationType.RESUME_PROCESSING_FAILED
        ),
        title="Resume processing failed",
        message=(
            "The resume could not be processed. Please review the file "
            "and try again."
        ),
        candidate_id=None,
        event_key=f"resume-processing:{processing_job_id}:failed"
    )


def notify_candidate_stage_changed_safely(
    db: Session,
    *,
    user_id: int,
    candidate_id: int,
    candidate_name: str,
    candidate_stage: str
) -> Notification | None:

    return create_notification_safely(
        db,
        user_id=user_id,
        notification_type=(
            NotificationType.CANDIDATE_STAGE_CHANGED
        ),
        title="Candidate stage updated",
        message=(
            f"{candidate_name} moved to "
            f"{candidate_stage.replace('_', ' ').title()}."
        ),
        candidate_id=candidate_id,
        event_key=None
    )


def create_notification_safely(
    db: Session,
    *,
    user_id: int,
    notification_type: NotificationType,
    title: str,
    message: str,
    candidate_id: int | None,
    event_key: str | None
) -> Notification | None:

    notification = Notification(
        user_id=user_id,
        type=notification_type.value,
        title=title,
        message=message,
        candidate_id=candidate_id,
        event_key=event_key
    )

    try:
        return notification_repository.create_notification(
            db,
            notification
        )
    except IntegrityError as error:
        _rollback_safely(db)

        if event_key:
            try:
                if notification_repository.get_notification_by_event_key(
                    db,
                    event_key
                ) is not None:
                    return None
            except Exception:
                pass

        _emit_notification_failure(notification_type, error)
        return None
    except Exception as error:
        _rollback_safely(db)
        _emit_notification_failure(notification_type, error)
        return None


def _emit_notification_failure(
    notification_type: NotificationType,
    error: Exception
) -> None:

    try:
        emit_event(
            "notification_creation_failed",
            severity="ERROR",
            operation="notification_creation",
            outcome="failure",
            notification_type=notification_type.value,
            error_category=type(error).__name__
        )
    except Exception:
        pass


def _rollback_safely(db: Session) -> None:

    try:
        db.rollback()
    except Exception:
        pass
