from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.candidate_model import CandidateResponse, RankingResponse
from app.models.candidate_stats_model import CandidateStatsResponse
from app.models.candidate_update_model import CandidateUpdate
from app.services import candidate_service

router = APIRouter(
    prefix="/candidates",
    tags=["Candidates"]
)

@router.get(
    "/",
    response_model=list[CandidateResponse],
    summary="Get all candidates",
    description="Returns a paginated list of candidates ordered by skill score."
)
def get_candidates(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
     return candidate_service.get_candidates(db, skip, limit)

@router.get(
    "/search",
    response_model=list[CandidateResponse],
    summary="Search candidates",
    description="Filter candidates by name, level, or minimum skill score."
)
def search_candidates(
    name: str | None = None,
    level: str | None = None,
    min_score: int | None = None,
    db: Session = Depends(get_db)
):
    return candidate_service.search_candidates(db, name, level, min_score)

@router.get(
    "/stats",
    response_model=CandidateStatsResponse,
    summary="Get candidate statistics",
    description="Returns aggregate counts and average skill score."
)
def get_candidate_stats(
    db: Session = Depends(get_db)
):
    return candidate_service.get_candidate_stats(db)

@router.get(
    "/ranking",
    response_model=list[RankingResponse],
    summary="Get candidate ranking",
    description="Returns top candidates ordered by skill score, then by ID."
)
def get_ranking(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    return candidate_service.get_ranking(db, limit)

@router.delete(
    "/{candidate_id:int}",
    summary="Delete candidate",
    description="Permanently removes a candidate by ID."
)
def delete_candidate(
    candidate_id: int,
    db: Session = Depends(get_db)
):
    candidate_service.delete_candidate(db, candidate_id)
    return {"message": "Candidate deleted successfully"}

@router.put(
    "/{candidate_id:int}",
    response_model=CandidateResponse,
    summary="Update candidate",
    description="Updates a candidate's skill score and/or level."
)
def update_candidate(
    candidate_id: int,
    data: CandidateUpdate,
    db: Session = Depends(get_db)
):
    return candidate_service.update_candidate(db, candidate_id, data)
    
@router.get(
    "/{candidate_id:int}",
    response_model=CandidateResponse,
    summary="Get candidate by ID",
    description="Returns a single candidate by ID."
)
def get_candidate(
    candidate_id: int,
    db: Session = Depends(get_db)
):
    return candidate_service.get_candidate_by_id(db, candidate_id)
