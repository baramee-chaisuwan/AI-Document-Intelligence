from enum import Enum


class ProcessingJobStatus(str, Enum):

    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


PROCESSING_JOB_STATUS_CHECK_SQL = (
    "status IN ("
    + ", ".join(
        f"'{status.value}'"
        for status in ProcessingJobStatus
    )
    + ")"
)
