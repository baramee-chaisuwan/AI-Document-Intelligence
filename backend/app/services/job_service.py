import logging

from sqlalchemy.orm import Session

from app.database.models import (
    Job,
    User
)
from app.models.job_model import (
    JobCreateRequest
)
from app.rag.embedding_service import (
    create_embedding,
    normalize_embedding
)
from app.repositories import job_repository
from app.services.job_extraction_service import (
    JobRequirementExtractionError,
    extract_job_requirements
)


logger = logging.getLogger(__name__)


class JobProcessingError(RuntimeError):
    """Raised when Job AI data cannot be prepared safely."""


def create_job(
    db: Session,
    data: JobCreateRequest,
    current_user: User
) -> Job:

    try:
        extracted_requirements = (
            extract_job_requirements(
                data.description
            )
        )
        embedding = normalize_embedding(
            create_embedding(
                data.description
            )
        )

    except (
        JobRequirementExtractionError,
        RuntimeError,
        ValueError
    ) as error:
        logger.exception(
            "Job AI processing failed"
        )
        raise JobProcessingError(
            "Job AI processing failed"
        ) from error

    job = Job(
        title=data.title,
        description=data.description,
        extracted_requirements=(
            extracted_requirements
        ),
        embedding=embedding,
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
