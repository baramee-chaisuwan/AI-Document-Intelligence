import logging
import time
import uuid

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.resume_processing_message import (
    ResumeProcessingMessageError,
    validate_resume_processing_message
)
from app.services import (
    gcs_storage_service,
    processing_job_service,
    pubsub_publisher_service
)
from app.services.resume_fingerprint_service import (
    DuplicateResumeError,
    ResumeFingerprintReservationError,
    calculate_resume_sha256,
    release_resume_fingerprint,
    reserve_resume_fingerprint
)
from app.services.gcs_storage_service import (
    GCSStorageError,
    StoredGCSObject
)
from app.services.pubsub_publisher_service import (
    PubSubPublisherError
)
from app.services.observability_service import (
    duration_ms,
    emit_event
)


logger = logging.getLogger(__name__)


class AsyncResumeSubmissionError(RuntimeError):
    """Raised when an async resume cannot be safely queued."""


def submit_resume(
    db: Session,
    filename: str,
    content: bytes
):

    started_at = time.perf_counter()
    submission_id = f"async-{uuid.uuid4().hex}"
    resume_sha256 = calculate_resume_sha256(
        content
    )

    try:
        processing_job = reserve_resume_fingerprint(
            db,
            resume_sha256
        )
    except DuplicateResumeError as error:
        emit_event(
            "async_resume_duplicate",
            operation="async_resume_submission",
            outcome="duplicate",
            duration_ms=duration_ms(started_at),
            candidate_id=error.candidate_id
        )
        raise
    except (
        SQLAlchemyError,
        ResumeFingerprintReservationError
    ) as error:
        db.rollback()
        emit_event(
            "async_resume_submission_failed",
            severity="ERROR",
            operation="fingerprint_reservation",
            outcome="failure",
            duration_ms=duration_ms(started_at),
            error_category=type(error).__name__
        )
        raise AsyncResumeSubmissionError(
            "Async resume submission is unavailable"
        ) from error

    try:
        stored_resume = gcs_storage_service.put_object(
            document_id=submission_id,
            filename=filename,
            content=content
        )
    except GCSStorageError as error:
        emit_event(
            "async_resume_submission_failed",
            severity="ERROR",
            operation="gcs_resume_upload",
            outcome="failure",
            duration_ms=duration_ms(started_at),
            processing_job_id=processing_job.id,
            error_category=type(error).__name__
        )
        _release_reservation_safely(
            db,
            processing_job.id,
            context="GCS upload failure"
        )
        raise AsyncResumeSubmissionError(
            "Async resume submission is unavailable"
        ) from error

    try:
        message = validate_resume_processing_message({
            "version": 1,
            "processing_job_id": processing_job.id,
            "gcs_object_key": stored_resume.key
        })
        (
            pubsub_publisher_service
            .publish_resume_processing_message(
                message
            )
        )
    except (
        PubSubPublisherError,
        ResumeProcessingMessageError
    ) as error:
        emit_event(
            "async_resume_submission_failed",
            severity="ERROR",
            operation="pubsub_resume_publication",
            outcome="failure",
            duration_ms=duration_ms(started_at),
            processing_job_id=processing_job.id,
            error_category=type(error).__name__
        )
        _compensate_publication_failure(
            db,
            processing_job.id,
            stored_resume
        )
        raise AsyncResumeSubmissionError(
            "Async resume submission is unavailable"
        ) from error

    emit_event(
        "async_resume_queued",
        operation="async_resume_submission",
        outcome="success",
        duration_ms=duration_ms(started_at),
        processing_job_id=processing_job.id
    )

    return processing_job


def _compensate_publication_failure(
    db: Session,
    processing_job_id: int,
    stored_resume: StoredGCSObject
) -> None:

    try:
        job_deleted = (
            processing_job_service
            .delete_pending_processing_job(
                db,
                processing_job_id
            )
        )
    except SQLAlchemyError as error:
        db.rollback()
        emit_event(
            "async_resume_compensation_failed",
            severity="ERROR",
            operation="processing_job_compensation",
            outcome="failure",
            processing_job_id=processing_job_id,
            error_category=type(error).__name__
        )
        return

    if not job_deleted:
        logger.error(
            "Pending processing job was not eligible for "
            "publication compensation: job_id=%s",
            processing_job_id
        )
        return

    _delete_stored_resume(
        stored_resume,
        context="message publication failure"
    )


def _delete_stored_resume(
    stored_resume: StoredGCSObject,
    *,
    context: str
) -> None:

    try:
        gcs_storage_service.delete_object(
            stored_resume.key
        )
    except GCSStorageError as error:
        emit_event(
            "async_resume_compensation_failed",
            severity="ERROR",
            operation="gcs_resume_cleanup",
            outcome="failure",
            error_category=type(error).__name__
        )


def _release_reservation_safely(
    db: Session,
    processing_job_id: int,
    *,
    context: str
) -> None:

    try:
        release_resume_fingerprint(
            db,
            processing_job_id
        )
    except ResumeFingerprintReservationError as error:
        emit_event(
            "async_resume_compensation_failed",
            severity="ERROR",
            operation="fingerprint_reservation_cleanup",
            outcome="failure",
            processing_job_id=processing_job_id,
            error_category=type(error).__name__
        )
