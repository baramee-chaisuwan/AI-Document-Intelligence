from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
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
    db: Session = Depends(get_db)
):

    candidates = db.query(Candidate).all()

    return candidates


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