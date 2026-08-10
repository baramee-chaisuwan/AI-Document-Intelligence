from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status
)
from sqlalchemy.orm import Session

from app.api.dependencies import (
    get_current_staff_user,
    get_current_user
)
from app.database.database import get_db
from app.database.models import User
from app.models.job_model import (
    JobCandidateMatchResponse,
    JobCreateRequest,
    JobResponse
)
from app.services import (
    job_matching_service,
    job_service
)


router = APIRouter(
    prefix="/jobs",
    tags=["Jobs"]
)


@router.post(
    "",
    response_model=JobResponse,
    status_code=status.HTTP_201_CREATED
)
def create_job(
    data: JobCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_staff_user
    )
):

    try:
        return job_service.create_job(
            db,
            data,
            current_user
        )

    except job_service.JobProcessingError as error:
        raise HTTPException(
            status_code=(
                status.HTTP_503_SERVICE_UNAVAILABLE
            ),
            detail=(
                "Job processing service "
                "is unavailable"
            )
        ) from error


@router.get(
    "",
    dependencies=[
        Depends(get_current_user)
    ],
    response_model=list[JobResponse]
)
def get_jobs(
    db: Session = Depends(get_db)
):

    return job_service.get_jobs(db)


@router.post(
    "/{job_id:int}/match",
    dependencies=[
        Depends(get_current_staff_user)
    ],
    response_model=list[
        JobCandidateMatchResponse
    ]
)
def match_job_candidates(
    job_id: int,
    db: Session = Depends(get_db)
):

    return (
        job_matching_service
        .match_job_candidates(
            db,
            job_id
        )
    )
