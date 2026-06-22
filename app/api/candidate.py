from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc, func

from app.database.database import get_db
from app.database.models import Candidate
from app.models.candidate_model import CandidateResponse

router = APIRouter(
    prefix="/candidates",
    tags=["Candidates"]
)


@router.get(
    "/",
    response_model=list[CandidateResponse]
)
def get_candidates(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):

    candidates = (
        db.query(Candidate)
        .order_by(desc(Candidate.skill_score))
        .offset(skip)
        .limit(limit)
        .all()
    )

    return candidates


@router.get(
    "/search",
    response_model=list[CandidateResponse]
)
def search_candidates(
    name: str | None = None,
    level: str | None = None,
    min_score: int | None = None,
    db: Session = Depends(get_db)
):

    query = db.query(Candidate)

    if name:
        query = query.filter(
            Candidate.name.contains(name)
        )

    if level:
        query = query.filter(
            Candidate.candidate_level == level
        )

    if min_score:
        query = query.filter(
            Candidate.skill_score >= min_score
        )

    return (
        query
        .order_by(desc(Candidate.skill_score))
        .all()
    )


@router.get("/stats")
def get_candidate_stats(
    db: Session = Depends(get_db)
):

    total_candidates = (
        db.query(Candidate)
        .count()
    )

    average_skill_score = (
        db.query(
            func.avg(Candidate.skill_score)
        )
        .scalar()
    )

    entry_level_count = (
        db.query(Candidate)
        .filter(
            Candidate.candidate_level == "Entry-Level"
        )
        .count()
    )

    junior_count = (
        db.query(Candidate)
        .filter(
            Candidate.candidate_level == "Junior"
        )
        .count()
    )

    return {
        "total_candidates": total_candidates,
        "average_skill_score": round(
            average_skill_score or 0,
            2
        ),
        "entry_level_count": entry_level_count,
        "junior_count": junior_count
    }


@router.get(
    "/{candidate_id}",
    response_model=CandidateResponse
)
def get_candidate(
    candidate_id: int,
    db: Session = Depends(get_db)
):

    candidate = (
        db.query(Candidate)
        .filter(Candidate.id == candidate_id)
        .first()
    )

    if not candidate:
        raise HTTPException(
            status_code=404,
            detail="Candidate not found"
        )

    return candidate