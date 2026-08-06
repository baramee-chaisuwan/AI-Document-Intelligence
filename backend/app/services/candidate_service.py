import logging

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.models.candidate_update_model import CandidateUpdate
from app.repositories import candidate_repository

from app.services.gcs_storage_service import (
    GCSStorageError,
    delete_object
)


logger = logging.getLogger(__name__)


def get_candidates(db: Session, skip: int, limit: int):
    return candidate_repository.get_candidates(db, skip, limit)


def search_candidates(db: Session, name: str, level: str, min_score: int):
    return candidate_repository.search_candidates(db, name, level, min_score)


def get_candidate_stats(db: Session):
    return candidate_repository.get_candidate_stats(db)


def get_ranking(db: Session, limit: int):
    return candidate_repository.get_ranking(db, limit)


def delete_candidate(db: Session, candidate_id: int):

    try:

        candidate = candidate_repository.get_candidate_by_id(
            db,
            candidate_id
        )

    except SQLAlchemyError:

        _rollback_preserving_error(
            db,
            candidate_id
        )

        raise

    if not candidate:
        raise NotFoundError("Candidate not found")

    resume_storage_key = candidate.resume_storage_key
    stored_resume_deleted = False

    try:

        candidate_repository.delete_candidate(
            db,
            candidate
        )

        if resume_storage_key:

            delete_object(
                resume_storage_key
            )

            stored_resume_deleted = True

        db.commit()

    except GCSStorageError:

        _rollback_preserving_error(
            db,
            candidate_id
        )

        raise

    except SQLAlchemyError:

        _rollback_preserving_error(
            db,
            candidate_id
        )

        if stored_resume_deleted:

            logger.error(
                "Candidate deletion failed after stored resume "
                "deletion; reconciliation is required: "
                "candidate_id=%s",
                candidate_id
            )

        raise

    return {
        "deleted": True
    }

def _rollback_preserving_error(
    db: Session,
    candidate_id: int
):

    try:

        db.rollback()

    except SQLAlchemyError:

        logger.exception(
            "Candidate deletion rollback failed; "
            "the original failure is preserved: "
            "candidate_id=%s",
            candidate_id
        )

def update_candidate(
    db: Session,
    candidate_id: int,
    data: CandidateUpdate
):

    candidate = candidate_repository.get_candidate_by_id(
        db,
        candidate_id
    )

    if not candidate:
        raise NotFoundError("Candidate not found")


    if data.skill_score is not None:
        candidate.skill_score = data.skill_score


    if data.candidate_level:
        candidate.candidate_level = data.candidate_level


    return candidate_repository.update_candidate(
        db,
        candidate
    )

def get_candidate_by_id(
    db: Session,
    candidate_id: int
):

    candidate = candidate_repository.get_candidate_by_id(
        db,
        candidate_id
    )

    if not candidate:
        raise NotFoundError("Candidate not found")

    return candidate
