from datetime import datetime

from sqlalchemy.orm import Session

from app.core.exceptions import (
    ConflictError,
    NotFoundError
)
from app.database.models import ResumeProcessingJob, utc_now
from app.models.processing_job_status import (
    ProcessingJobStatus
)
from app.repositories import processing_job_repository


DEFAULT_PROCESSING_ERROR = "Resume processing failed"
MAX_SAFE_ERROR_LENGTH = 500

VALID_TRANSITIONS = {
    ProcessingJobStatus.PENDING: {
        ProcessingJobStatus.PROCESSING
    },
    ProcessingJobStatus.PROCESSING: {
        ProcessingJobStatus.COMPLETED,
        ProcessingJobStatus.FAILED
    },
}


def create_processing_job(
    db: Session,
    candidate_id: int | None = None
) -> ResumeProcessingJob:

    return processing_job_repository.create_processing_job(
        db,
        candidate_id
    )


def get_processing_job(
    db: Session,
    job_id: int
) -> ResumeProcessingJob:

    job = (
        processing_job_repository
        .get_processing_job_by_id(
            db,
            job_id
        )
    )

    if not job:
        raise NotFoundError(
            "Processing job not found"
        )

    return job


def delete_pending_processing_job(
    db: Session,
    job_id: int
) -> bool:

    return (
        processing_job_repository
        .delete_pending_processing_job(
            db,
            job_id
        )
    )


def transition_processing_job(
    db: Session,
    job_id: int,
    next_status: ProcessingJobStatus,
    error_message: str | None = None,
    transitioned_at: datetime | None = None
) -> ResumeProcessingJob:

    job = get_processing_job(
        db,
        job_id
    )
    current_status = ProcessingJobStatus(
        job.status
    )

    if next_status not in VALID_TRANSITIONS.get(
        current_status,
        set()
    ):
        raise ConflictError(
            "Invalid processing job status transition"
        )

    transition_time = transitioned_at or utc_now()
    started_at = (
        transition_time
        if next_status
        == ProcessingJobStatus.PROCESSING
        else None
    )
    completed_at = (
        transition_time
        if next_status in {
            ProcessingJobStatus.COMPLETED,
            ProcessingJobStatus.FAILED
        }
        else None
    )
    safe_error = (
        sanitize_error_message(error_message)
        if next_status == ProcessingJobStatus.FAILED
        else None
    )

    updated_job = (
        processing_job_repository
        .transition_processing_job(
            db=db,
            job_id=job_id,
            expected_status=current_status.value,
            next_status=next_status.value,
            transitioned_at=transition_time,
            started_at=started_at,
            completed_at=completed_at,
            error_message=safe_error
        )
    )

    if not updated_job:
        raise ConflictError(
            "Processing job status changed concurrently"
        )

    return updated_job


def sanitize_error_message(
    error_message: str | None
) -> str:

    if not error_message:
        return DEFAULT_PROCESSING_ERROR

    if "\n" in error_message or "\r" in error_message:
        return DEFAULT_PROCESSING_ERROR

    normalized = " ".join(
        error_message.split()
    )
    lowered = normalized.casefold()
    sensitive_markers = (
        "traceback",
        "password",
        "secret",
        "api_key",
        "api key",
        "database_url",
        "authorization:"
    )

    if (
        not normalized
        or any(
            marker in lowered
            for marker in sensitive_markers
        )
    ):
        return DEFAULT_PROCESSING_ERROR

    return normalized[:MAX_SAFE_ERROR_LENGTH]
