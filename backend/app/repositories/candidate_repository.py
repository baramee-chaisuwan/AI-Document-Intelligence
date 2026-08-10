from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from app.database.models import Candidate

def get_candidates(
    db: Session,
    skip: int,
    limit: int
):
    return (
        db.query(Candidate)
        .order_by(
            desc(Candidate.ai_score)
        )
        .offset(skip)
        .limit(limit)
        .all()
    )

def get_candidate_by_id(
    db: Session,
    candidate_id: int
):
    return (
        db.query(Candidate)
        .filter(
            Candidate.id == candidate_id
        )
        .first()
    )

def delete_candidate(
    db: Session,
    candidate: Candidate
):
    db.delete(candidate)
    db.flush()

def update_candidate(
    db: Session,
    candidate: Candidate,
):
    db.add(candidate)
    db.commit()
    db.refresh(candidate)

    return candidate


def update_candidate_stage(
    db: Session,
    candidate: Candidate,
    candidate_stage: str
):
    candidate.candidate_stage = candidate_stage
    db.add(candidate)
    db.commit()
    db.refresh(candidate)

    return candidate

def search_candidates(
    db: Session,
    name: str | None = None,
    level: str | None = None,
    min_score: int | None = None
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

    if min_score is not None:
        query = query.filter(
            Candidate.ai_score >= min_score
        )

    return (
        query
        .order_by(
            desc(Candidate.ai_score)
        )
        .all()
    )

def get_ranking(
    db: Session,
    limit: int
):

    return (
        db.query(Candidate)
        .order_by(
            Candidate.ai_score.desc(),
            Candidate.id.asc()
        )
        .limit(limit)
        .all()
    )

def get_candidate_stats(
    db: Session
):

    total_candidates = (
        db.query(Candidate)
        .count()
    )

    average_ai_score = (
        db.query(
            func.avg(
                Candidate.ai_score
            )
        )
        .scalar()
    )

    return {
        "total_candidates": total_candidates,
        "average_ai_score": float(
            round(
                average_ai_score or 0,
                2
            )
        )
    }

def get_dashboard_summary(
    db: Session
):

    total_candidates = (
        db.query(Candidate)
        .count()
    )

    average_score = (
        db.query(
            func.avg(
                Candidate.ai_score
            )
        )
        .scalar()
    )

    top_candidate = (
        db.query(Candidate)
        .order_by(
            Candidate.ai_score.desc()
        )
        .first()
    )

    junior_count = (
        db.query(Candidate)
        .filter(
            Candidate.candidate_level == "Junior"
        )
        .count()
    )

    mid_count = (
        db.query(Candidate)
        .filter(
            Candidate.candidate_level == "Mid-Level"
        )
        .count()
    )

    senior_count = (
        db.query(Candidate)
        .filter(
            Candidate.candidate_level == "Senior"
        )
        .count()
    )

    return {

        "total_candidates":
            total_candidates,

        "average_score":
            round(
                average_score or 0,
                2
            ),

        "top_candidate":
            (
                top_candidate.name
                if top_candidate
                else ""
            ),

        "top_score":
            (
                top_candidate.ai_score
                if top_candidate
                else 0
            ),

        "junior_count":
            junior_count,

        "mid_count":
            mid_count,

        "senior_count":
            senior_count
    }

def get_top_candidates(
    db: Session,
    limit: int
):

    return (
        db.query(Candidate)
        .order_by(
            Candidate.ai_score.desc()
        )
        .limit(limit)
        .all()
    )

def get_score_distribution(
    db: Session
):

    candidates = (
        db.query(
            Candidate.ai_score
        )
        .all()
    )

    ranges = {

        "0-20": 0,
        "21-40": 0,
        "41-60": 0,
        "61-80": 0,
        "81-100": 0

    }

    for candidate in candidates:

        score = candidate.ai_score

        if score <= 20:
            ranges["0-20"] += 1

        elif score <= 40:
            ranges["21-40"] += 1

        elif score <= 60:
            ranges["41-60"] += 1

        elif score <= 80:
            ranges["61-80"] += 1

        else:
            ranges["81-100"] += 1

    return [

        {
            "score_range": key,
            "count": value
        }

        for key, value in ranges.items()

        if value > 0

    ]

def get_level_distribution(
    db: Session
):

    result = (
        db.query(
            Candidate.candidate_level,
            func.count(
                Candidate.id
            )
        )
        .group_by(
            Candidate.candidate_level
        )
        .all()
    )

    return [

        {
            "level": level,
            "count": count
        }

        for level, count in result

    ]

def get_recent_candidates(
    db: Session,
    limit: int
):

    candidates = (
        db.query(Candidate)
        .order_by(
            Candidate.created_at.desc()
        )
        .limit(limit)
        .all()
    )

    return [

        {
            "id": candidate.id,
            "name": candidate.name,
            "candidate_level": candidate.candidate_level,
            "ai_score": candidate.ai_score,
            "created_at": candidate.created_at,
        }

        for candidate in candidates

    ]
