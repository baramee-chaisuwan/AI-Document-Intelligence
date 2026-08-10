from datetime import datetime

from sqlalchemy.orm import Session

from app.database.models import ResumeProcessingJob


def create_processing_job(
    db: Session,
    candidate_id: int | None = None
) -> ResumeProcessingJob:

    job = ResumeProcessingJob(
        candidate_id=candidate_id
    )

    db.add(job)
    db.commit()
    db.refresh(job)

    return job


def get_processing_job_by_id(
    db: Session,
    job_id: int
) -> ResumeProcessingJob | None:

    return (
        db.query(ResumeProcessingJob)
        .filter(
            ResumeProcessingJob.id == job_id
        )
        .first()
    )


def transition_processing_job(
    db: Session,
    job_id: int,
    expected_status: str,
    next_status: str,
    transitioned_at: datetime,
    started_at: datetime | None,
    completed_at: datetime | None,
    error_message: str | None
) -> ResumeProcessingJob | None:

    values = {
        "status": next_status,
        "updated_at": transitioned_at,
        "error_message": error_message,
    }

    if started_at is not None:
        values["started_at"] = started_at

    if completed_at is not None:
        values["completed_at"] = completed_at

    updated_count = (
        db.query(ResumeProcessingJob)
        .filter(
            ResumeProcessingJob.id == job_id,
            ResumeProcessingJob.status
            == expected_status
        )
        .update(
            values,
            synchronize_session=False
        )
    )

    if updated_count != 1:
        db.rollback()
        return None

    db.commit()
    db.expire_all()

    return get_processing_job_by_id(
        db,
        job_id
    )
