from app.repositories import candidate_repository
from app.models.candidate_update_model import CandidateUpdate
from app.core.exceptions import NotFoundError
from sqlalchemy.orm import Session

def get_candidates(db: Session, skip: int, limit: int):
    return candidate_repository.get_candidates(db, skip, limit)

def search_candidates(db: Session, name: str, level: str, min_score: int):
    return candidate_repository.search_candidates(db, name, level, min_score)


def get_candidate_stats(db: Session):
    return candidate_repository.get_candidate_stats(db)


def get_ranking(db: Session, limit: int):
    return candidate_repository.get_ranking(db,limit)

def delete_candidate(db: Session, candidate_id: int):
    candidate = candidate_repository.get_candidate_by_id(db, candidate_id)

    if not candidate:
        raise NotFoundError("Candidate not found")

    candidate_repository.delete_candidate(db, candidate)

    return {"deleted": True}


def update_candidate(db: Session, candidate_id: int, data: CandidateUpdate):
    candidate = candidate_repository.get_candidate_by_id(db, candidate_id)

    if not candidate:
        raise NotFoundError("Candidate not found")

    if data.skill_score is not None:
        candidate.skill_score = data.skill_score

    if data.candidate_level:
        candidate.candidate_level = data.candidate_level

    return candidate_repository.update_candidate(db, candidate)

def get_candidate_by_id(db: Session, candidate_id: int):
    candidate = candidate_repository.get_candidate_by_id(db, candidate_id)

    if not candidate:
        raise NotFoundError("Candidate not found")

    return candidate