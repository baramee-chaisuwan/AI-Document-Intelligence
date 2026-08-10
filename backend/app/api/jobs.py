from fastapi import (
    APIRouter,
    Depends,
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
    JobCreateRequest,
    JobResponse
)
from app.services import job_service


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

    return job_service.create_job(
        db,
        data,
        current_user
    )


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
