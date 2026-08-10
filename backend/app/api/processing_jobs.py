from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.database.database import get_db
from app.models.processing_job_model import (
    ResumeProcessingJobResponse
)
from app.services import processing_job_service


router = APIRouter(
    prefix="/processing-jobs",
    tags=["Processing Jobs"]
)


@router.get(
    "/{job_id:int}",
    dependencies=[
        Depends(get_current_user)
    ],
    response_model=ResumeProcessingJobResponse,
    summary="Get resume processing job status"
)
def get_processing_job(
    job_id: int,
    db: Session = Depends(get_db)
):

    return processing_job_service.get_processing_job(
        db,
        job_id
    )
