from sqlalchemy.orm import Session

from app.repositories import candidate_repository

def get_dashboard_summary(db: Session):
    return candidate_repository.get_dashboard_summary(db)

def get_top_candidates(db: Session,limit: int):
    return candidate_repository.get_top_candidates(db,limit)

def get_score_distribution(db: Session):
    return candidate_repository.get_score_distribution(db)

def get_level_distribution(db: Session):
    return candidate_repository.get_level_distribution(db)

def get_recent_candidates(db: Session, limit: int):
    return candidate_repository.get_recent_candidates(db,limit)