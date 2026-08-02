from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.dashboard_model import (
    DashboardSummaryResponse,
    TopCandidateResponse,
    RecentCandidateResponse,
)
from app.models.dashboard_analytics_model import (
    LevelDistributionResponse,
    ScoreDistributionResponse,
)
from app.services import dashboard_service

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)

@router.get(
    "/summary",
    response_model=DashboardSummaryResponse,
    summary="Get dashboard summary",
    description="Returns high-level dashboard metrics including counts by level."
)
def dashboard_summary(
    db: Session = Depends(get_db)
):
    return dashboard_service.get_dashboard_summary(db)

@router.get(
    "/top-candidates",
    response_model=list[TopCandidateResponse],
    summary="Get top candidates",
    description="Returns the highest-scoring candidates for the dashboard."
)
def top_candidates(
    limit: int = 5,
    db: Session = Depends(get_db)
):
    return dashboard_service.get_top_candidates(db, limit)

@router.get(
    "/score-distribution",
    response_model=list[ScoreDistributionResponse],
    summary="Get score distribution",
    description="Returns the distribution of candidates skill scores grouped into ranges for dashboard visualization."
)
def score_distribution(db: Session = Depends(get_db)):
    return dashboard_service.get_score_distribution(db)

@router.get(
    "/level-distribution",
    response_model=list[LevelDistributionResponse],
    summary="Get level distribution",
    description="Returns count of candidates grouped by level"
)
def level_distribution(db: Session = Depends(get_db)):
    return dashboard_service.get_level_distribution(db)

@router.get(
    "/recent-candidates",
    response_model=list[RecentCandidateResponse],
    summary="Get recent candidates",
    description="Returns most recently created candidates."
)
def recent_candidates(
    limit: int = 5,
    db: Session = Depends(get_db)
):
    return dashboard_service.get_recent_candidates(db, limit)