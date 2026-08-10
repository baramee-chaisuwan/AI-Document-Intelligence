from sqlalchemy.orm import Session

from app.database.models import Job


def create_job(
    db: Session,
    job: Job
) -> Job:

    db.add(job)
    db.commit()
    db.refresh(job)

    return job


def get_jobs(
    db: Session
) -> list[Job]:

    return (
        db.query(Job)
        .order_by(
            Job.created_at.desc(),
            Job.id.desc()
        )
        .all()
    )
