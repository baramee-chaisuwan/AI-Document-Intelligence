import csv
import io

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database.models import Candidate
from app.models.candidate_model import CandidateResponse, RankingResponse
from app.models.candidate_stats_model import CandidateStatsResponse
from app.models.candidate_update_model import CandidateUpdate
from app.models.dashboard_model import DashboardSummaryResponse, TopCandidateResponse

router = APIRouter(
    prefix="/candidates",
    tags=["Candidates"],
)

@router.get(
    "/",
    response_model=list[CandidateResponse],
    summary="Get all candidates",
    description="Returns a paginated list of candidates ordered by skill score.",
)
def get_candidates(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
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
    response_model=list[CandidateResponse],
    summary="Search candidates",
    description="Filter candidates by name, level, or minimum skill score.",
)
def search_candidates(
    name: str | None = None,
    level: str | None = None,
    min_score: int | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(Candidate)

    if name:
        query = query.filter(Candidate.name.contains(name))

    if level:
        query = query.filter(Candidate.candidate_level == level)

    if min_score is not None:
        query = query.filter(Candidate.skill_score >= min_score)

    return query.order_by(desc(Candidate.skill_score)).all()

@router.get(
    "/stats",
    response_model=CandidateStatsResponse,
    summary="Get candidate statistics",
    description="Returns aggregate counts and average skill score.",
)
def get_candidate_stats(db: Session = Depends(get_db)):
    total_candidates = db.query(Candidate).count()

    average_skill_score = (
        db.query(func.avg(Candidate.skill_score))
        .scalar()
    )

    entry_level_count = (
        db.query(Candidate)
        .filter(Candidate.candidate_level == "Entry-Level")
        .count()
    )

    junior_count = (
        db.query(Candidate)
        .filter(Candidate.candidate_level == "Junior")
        .count()
    )

    return {
        "total_candidates": total_candidates,
        "average_skill_score": round(average_skill_score or 0, 2),
        "entry_level_count": entry_level_count,
        "junior_count": junior_count,
    }

@router.get(
    "/ranking",
    response_model=list[RankingResponse],
    summary="Get candidate ranking",
    description="Returns top candidates ordered by skill score, then by ID.",
)
def get_ranking(
    limit: int = 10,
    db: Session = Depends(get_db),
):
    candidates = (
        db.query(Candidate)
        .order_by(
            Candidate.skill_score.desc(),
            Candidate.id.asc(),
        )
        .limit(limit)
        .all()
    )

    return candidates

@router.get(
    "/dashboard/summary",
    response_model=DashboardSummaryResponse,
    summary="Get dashboard summary",
    description="Returns high-level dashboard metrics including counts by level.",
)
def dashboard_summary(db: Session = Depends(get_db)):
    total_candidates = db.query(Candidate).count()

    average_score = (
        db.query(func.avg(Candidate.skill_score))
        .scalar()
    )

    top_candidate = (
        db.query(Candidate)
        .order_by(Candidate.skill_score.desc())
        .first()
    )

    junior_count = (
        db.query(Candidate)
        .filter(Candidate.candidate_level == "Junior")
        .count()
    )

    mid_count = (
        db.query(Candidate)
        .filter(Candidate.candidate_level == "Mid-Level")
        .count()
    )

    senior_count = (
        db.query(Candidate)
        .filter(Candidate.candidate_level == "Senior")
        .count()
    )

    return DashboardSummaryResponse(
        total_candidates=total_candidates,
        average_score=round(average_score or 0, 2),
        top_candidate=top_candidate.name if top_candidate else "",
        top_score=top_candidate.skill_score if top_candidate else 0,
        junior_count=junior_count,
        mid_count=mid_count,
        senior_count=senior_count,
    )

@router.get(
    "/dashboard/top-candidates",
    response_model=list[TopCandidateResponse],
    summary="Get top candidates",
    description="Returns the highest-scoring candidates for the dashboard.",
)
def top_candidates(
    limit: int = 5,
    db: Session = Depends(get_db),
):
    return (
        db.query(Candidate)
        .order_by(Candidate.skill_score.desc())
        .limit(limit)
        .all()
    )

@router.get(
    "/csv",
    summary="Export candidates to CSV",
    description="Downloads all candidates as a CSV file.",
)
def export_candidates_csv(db: Session = Depends(get_db)):
    candidates = db.query(Candidate).all()

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        "id",
        "name",
        "candidate_level",
        "skill_score",
    ])

    for c in candidates:
        writer.writerow([
            c.id,
            c.name,
            c.candidate_level,
            c.skill_score,
        ])

    output.seek(0)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=candidates.csv",
        },
    )

@router.delete(
    "/{candidate_id:int}",
    summary="Delete candidate",
    description="Permanently removes a candidate by ID.",
)
def delete_candidate(
    candidate_id: int,
    db: Session = Depends(get_db),
):
    candidate = (
        db.query(Candidate)
        .filter(Candidate.id == candidate_id)
        .first()
    )

    if not candidate:
        raise HTTPException(
            status_code=404,
            detail="Candidate not found",
        )

    db.delete(candidate)
    db.commit()

    return {"message": "Candidate deleted successfully"}

@router.put(
    "/{candidate_id:int}",
    response_model=CandidateResponse,
    summary="Update candidate",
    description="Updates a candidate's skill score and/or level.",
)
def update_candidate(
    candidate_id: int,
    candidate_data: CandidateUpdate,
    db: Session = Depends(get_db),
):
    candidate = (
        db.query(Candidate)
        .filter(Candidate.id == candidate_id)
        .first()
    )

    if not candidate:
        raise HTTPException(
            status_code=404,
            detail="Candidate not found",
        )

    if candidate_data.skill_score is not None:
        candidate.skill_score = candidate_data.skill_score

    if candidate_data.candidate_level:
        candidate.candidate_level = candidate_data.candidate_level

    db.commit()
    db.refresh(candidate)

    return candidate

@router.get(
    "/{candidate_id:int}",
    response_model=CandidateResponse,
    summary="Get candidate by ID",
    description="Returns a single candidate by ID.",
)
def get_candidate(
    candidate_id: int,
    db: Session = Depends(get_db),
):
    candidate = (
        db.query(Candidate)
        .filter(Candidate.id == candidate_id)
        .first()
    )

    if not candidate:
        raise HTTPException(
            status_code=404,
            detail="Candidate not found",
        )

    return candidate
