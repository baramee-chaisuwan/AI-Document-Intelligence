from sqlalchemy.orm import Session

from app.database.models import (
    Job,
    User,
    empty_job_requirements
)
from app.models.job_model import (
    JobCreateRequest
)
from app.repositories import job_repository


def create_job(
    db: Session,
    data: JobCreateRequest,
    current_user: User
) -> Job:

    job = Job(
        title=data.title,
        description=data.description,
        extracted_requirements=(
            empty_job_requirements()
        ),
        created_by=current_user.id
    )

    return job_repository.create_job(
        db,
        job
    )


def get_jobs(
    db: Session
) -> list[Job]:

    return job_repository.get_jobs(db)
