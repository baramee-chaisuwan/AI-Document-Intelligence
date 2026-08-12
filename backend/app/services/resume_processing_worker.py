import logging
import time
from dataclasses import dataclass
from enum import Enum
from typing import Callable

from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError
from app.database.models import Candidate
from app.models.processing_job_status import (
    ProcessingJobStatus
)
from app.models.resume_processing_message import (
    ResumeProcessingMessage,
    parse_resume_processing_message
)
from app.repositories import processing_job_repository
from app.services import (
    analyzer_service,
    extraction_service,
    gcs_storage_service,
    gemini_service,
    indexing_service,
    pdf_service,
    processing_job_service,
    notification_service,
    resume_fingerprint_service
)
from app.services.observability_service import (
    duration_ms,
    emit_event,
    service_name
)


logger = logging.getLogger(__name__)


class ResumeWorkerError(RuntimeError):
    """Raised when claimed resume processing cannot complete."""


class WorkerOutcome(str, Enum):

    COMPLETED = "COMPLETED"
    ALREADY_COMPLETED = "ALREADY_COMPLETED"
    ALREADY_PROCESSING = "ALREADY_PROCESSING"
    TERMINAL_FAILED = "TERMINAL_FAILED"


@dataclass(frozen=True)
class ResumeWorkerResult:

    processing_job_id: int
    outcome: WorkerOutcome
    candidate_id: int | None


ResumeProcessor = Callable[
    [Session, str],
    Candidate
]


def handle_resume_processing_message(
    db: Session,
    payload: ResumeProcessingMessage | bytes | str | dict,
    processor: ResumeProcessor | None = None
) -> ResumeWorkerResult:

    started_at = time.perf_counter()
    message = parse_resume_processing_message(
        payload
    )
    job = processing_job_service.get_processing_job(
        db,
        message.processing_job_id
    )
    current_status = ProcessingJobStatus(
        job.status
    )

    duplicate_result = _duplicate_result(
        job.id,
        job.candidate_id,
        current_status
    )

    if duplicate_result:
        emit_event(
            "resume_worker_noop",
            service=service_name("ats-worker"),
            operation="resume_processing",
            outcome=duplicate_result.outcome.value,
            duration_ms=duration_ms(started_at),
            processing_job_id=job.id,
            candidate_id=job.candidate_id
        )
        return duplicate_result

    try:
        claimed_job = (
            processing_job_service
            .transition_processing_job(
                db,
                job.id,
                ProcessingJobStatus.PROCESSING
            )
        )
    except ConflictError:
        refreshed_job = (
            processing_job_service
            .get_processing_job(
                db,
                job.id
            )
        )
        refreshed_status = ProcessingJobStatus(
            refreshed_job.status
        )
        duplicate_result = _duplicate_result(
            refreshed_job.id,
            refreshed_job.candidate_id,
            refreshed_status
        )

        if duplicate_result:
            emit_event(
                "resume_worker_noop",
                service=service_name("ats-worker"),
                operation="resume_processing",
                outcome=duplicate_result.outcome.value,
                duration_ms=duration_ms(started_at),
                processing_job_id=refreshed_job.id,
                candidate_id=refreshed_job.candidate_id
            )
            return duplicate_result

        raise

    claimed_job_id = claimed_job.id
    requested_by = claimed_job.requested_by
    reservation_sha256 = claimed_job.resume_sha256
    emit_event(
        "resume_worker_started",
        service=service_name("ats-worker"),
        operation="resume_processing",
        outcome="started",
        processing_job_id=claimed_job_id
    )
    resume_processor = (
        processor
        or process_resume_from_gcs
    )

    try:
        candidate = resume_processor(
            db,
            message.gcs_object_key
        )

        if (
            reservation_sha256 is not None
            and candidate.resume_sha256
            != reservation_sha256
        ):
            raise ResumeWorkerError(
                "Resume fingerprint does not match its reservation"
            )

        if reservation_sha256 is not None:
            candidate.resume_sha256 = reservation_sha256

        processing_job_repository.associate_candidate(
            db,
            claimed_job,
            candidate.id
        )
        db.flush()
        completed_job = (
            processing_job_service
            .transition_processing_job(
                db,
                claimed_job_id,
                ProcessingJobStatus.COMPLETED
            )
        )

        result = ResumeWorkerResult(
            processing_job_id=completed_job.id,
            outcome=WorkerOutcome.COMPLETED,
            candidate_id=completed_job.candidate_id
        )

        emit_event(
            "resume_worker_completed",
            service=service_name("ats-worker"),
            operation="resume_processing",
            outcome="success",
            duration_ms=duration_ms(started_at),
            processing_job_id=completed_job.id,
            candidate_id=completed_job.candidate_id
        )

        notification_service.notify_resume_completed_safely(
            db,
            user_id=requested_by,
            processing_job_id=completed_job.id,
            candidate_id=completed_job.candidate_id
        )

        return result

    except Exception as error:
        db.rollback()

        emit_event(
            "resume_worker_failed",
            service=service_name("ats-worker"),
            severity="ERROR",
            operation="resume_processing",
            outcome="failure",
            duration_ms=duration_ms(started_at),
            processing_job_id=claimed_job_id,
            error_category=type(error).__name__
        )

        try:
            failed_job = processing_job_service.transition_processing_job(
                db,
                claimed_job_id,
                ProcessingJobStatus.FAILED,
                error_message=(
                    processing_job_service
                    .DEFAULT_PROCESSING_ERROR
                )
            )
            notification_service.notify_resume_failed_safely(
                db,
                user_id=requested_by,
                processing_job_id=failed_job.id
            )
        except Exception as transition_error:
            emit_event(
                "resume_worker_failure_state_failed",
                service=service_name("ats-worker"),
                severity="ERROR",
                operation="processing_job_failure_transition",
                outcome="failure",
                processing_job_id=claimed_job_id,
                error_category=type(transition_error).__name__
            )

        raise ResumeWorkerError(
            "Resume processing failed"
        ) from error


def process_resume_from_gcs(
    db: Session,
    object_key: str
) -> Candidate:

    file_bytes = gcs_storage_service.get_object(
        object_key
    )
    resume_sha256 = (
        resume_fingerprint_service
        .calculate_resume_sha256(
            file_bytes
        )
    )
    extracted_text = pdf_service.extract_text_from_pdf(
        file_bytes
    )

    if (
        not isinstance(extracted_text, str)
        or not extracted_text.strip()
    ):
        raise ResumeWorkerError(
            "Resume PDF contains no extractable text"
        )

    extracted_text = extracted_text.strip()
    resume_data = extraction_service.extract_resume_data(
        extracted_text
    )
    candidate_name = _candidate_name(
        resume_data
    )
    resume_data["name"] = candidate_name
    summary = gemini_service.summarize_document(
        extracted_text
    )
    analysis = analyzer_service.analyze_resume(
        resume_data
    )
    _validate_analysis(analysis)

    candidate = Candidate(
        name=candidate_name,
        summary=str(summary or "").strip(),
        candidate_level=str(
            analysis["candidate_level"]
        ).strip(),
        skill_score=int(round(analysis["skill_score"])),
        rule_score=int(round(analysis["rule_score"])),
        ai_score=int(round(analysis["ai_score"])),
        ai_status=str(analysis["ai_status"]),
        score_breakdown=analysis["score_breakdown"],
        resume_storage_key=object_key,
        resume_sha256=resume_sha256
    )

    if not candidate.summary:
        raise ResumeWorkerError(
            "Resume summary is unavailable"
        )

    db.add(candidate)
    db.flush()

    indexing_service.index_resume(
        db=db,
        document_id=candidate.id,
        resume_text=extracted_text
    )

    return candidate


def _duplicate_result(
    job_id: int,
    candidate_id: int | None,
    status: ProcessingJobStatus
) -> ResumeWorkerResult | None:

    outcomes = {
        ProcessingJobStatus.PROCESSING: (
            WorkerOutcome.ALREADY_PROCESSING
        ),
        ProcessingJobStatus.COMPLETED: (
            WorkerOutcome.ALREADY_COMPLETED
        ),
        ProcessingJobStatus.FAILED: (
            WorkerOutcome.TERMINAL_FAILED
        ),
    }
    outcome = outcomes.get(status)

    if outcome is None:
        return None

    return ResumeWorkerResult(
        processing_job_id=job_id,
        outcome=outcome,
        candidate_id=candidate_id
    )


def _candidate_name(
    resume_data
) -> str:

    if not isinstance(resume_data, dict):
        raise ResumeWorkerError(
            "Resume extraction returned invalid data"
        )

    candidate_name = str(
        resume_data.get("name")
        or ""
    ).strip()

    if (
        not candidate_name
        or len(candidate_name) > 255
        or candidate_name.casefold()
        in {"unknown", "unknown candidate", "n/a", "none"}
    ):
        raise ResumeWorkerError(
            "Candidate name could not be determined"
        )

    return candidate_name


def _validate_analysis(analysis) -> None:

    if not isinstance(analysis, dict):
        raise ResumeWorkerError(
            "Resume analysis returned invalid data"
        )

    required_fields = (
        "candidate_level",
        "skill_score",
        "rule_score",
        "ai_score",
        "ai_status",
        "score_breakdown"
    )

    if any(
        field not in analysis
        for field in required_fields
    ):
        raise ResumeWorkerError(
            "Resume analysis returned incomplete data"
        )

    if (
        not str(analysis["candidate_level"]).strip()
        or not str(analysis["ai_status"]).strip()
        or not isinstance(analysis["score_breakdown"], dict)
    ):
        raise ResumeWorkerError(
            "Resume analysis returned invalid data"
        )

    for field in (
        "skill_score",
        "rule_score",
        "ai_score"
    ):
        value = analysis[field]

        if (
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or value < 0
            or value > 100
        ):
            raise ResumeWorkerError(
                "Resume analysis returned invalid scores"
            )
