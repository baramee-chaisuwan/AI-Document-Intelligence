from enum import Enum


class NotificationType(str, Enum):

    RESUME_PROCESSING_COMPLETED = "RESUME_PROCESSING_COMPLETED"
    RESUME_PROCESSING_FAILED = "RESUME_PROCESSING_FAILED"
    CANDIDATE_STAGE_CHANGED = "CANDIDATE_STAGE_CHANGED"


NOTIFICATION_TYPE_CHECK_SQL = (
    "type IN ("
    + ", ".join(
        f"'{notification_type.value}'"
        for notification_type in NotificationType
    )
    + ")"
)
