import hashlib
import re

from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.repositories import (
    candidate_repository,
    processing_job_repository
)
from app.services import processing_job_service

RESUME_SHA256_PATTERN = re.compile(
    r"^[0-9a-f]{64}$"
)


class DuplicateResumeError(RuntimeError):
    """Raised when exact resume bytes are already represented."""

    def __init__(self, candidate_id: int | None = None):
        self.candidate_id = candidate_id
        super().__init__("This exact resume file already exists")


class ResumeFingerprintReservationError(RuntimeError):
    """Raised when fingerprint reservation cannot be managed safely."""


def calculate_resume_sha256(content: bytes) -> str:

    if not isinstance(content, bytes) or not content:
        raise ValueError("Resume content must be non-empty bytes")

    return hashlib.sha256(content).hexdigest()


def reserve_resume_fingerprint(
    db: Session,
    resume_sha256: str
):

    _validate_resume_sha256(resume_sha256)
    existing_candidate = get_existing_candidate(
        db,
        resume_sha256
    )

    if existing_candidate:
        raise DuplicateResumeError(
            existing_candidate.id
        )

    try:
        reservation_job = (
            processing_job_service
            .create_processing_job(
                db,
                resume_sha256=resume_sha256
            )
        )
    except IntegrityError as error:
        db.rollback()
        existing_candidate = get_existing_candidate(
            db,
            resume_sha256
        )
        existing_reservation = (
            processing_job_repository
            .get_processing_job_by_resume_sha256(
                db,
                resume_sha256
            )
        )

        if not existing_candidate and not existing_reservation:
            raise ResumeFingerprintReservationError(
                "Resume fingerprint reservation failed"
            ) from error

        raise DuplicateResumeError(
            existing_candidate.id
            if existing_candidate
            else None
        ) from error

    existing_candidate = get_existing_candidate(
        db,
        resume_sha256
    )

    if existing_candidate:
        release_resume_fingerprint(
            db,
            reservation_job.id
        )
        raise DuplicateResumeError(
            existing_candidate.id
        )

    return reservation_job


def get_existing_candidate(
    db: Session,
    resume_sha256: str
):

    _validate_resume_sha256(resume_sha256)

    return (
        candidate_repository
        .get_candidate_by_resume_sha256(
            db,
            resume_sha256
        )
    )


def release_resume_fingerprint(
    db: Session,
    processing_job_id: int
) -> None:

    try:
        deleted = (
            processing_job_service
            .delete_pending_processing_job(
                db,
                processing_job_id
            )
        )
    except SQLAlchemyError as error:
        db.rollback()
        raise ResumeFingerprintReservationError(
            "Resume fingerprint reservation could not be released"
        ) from error

    if not deleted:
        raise ResumeFingerprintReservationError(
            "Resume fingerprint reservation could not be released"
        )


def prepare_reservation_completion(
    db: Session,
    reservation_job
) -> None:

    processing_job_repository.prepare_delete_processing_job(
        db,
        reservation_job
    )


def _validate_resume_sha256(resume_sha256: str) -> None:

    if (
        not isinstance(resume_sha256, str)
        or not RESUME_SHA256_PATTERN.fullmatch(
            resume_sha256
        )
    ):
        raise ValueError("Resume SHA-256 is invalid")
