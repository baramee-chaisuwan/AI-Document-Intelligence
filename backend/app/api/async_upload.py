from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
    status
)
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_staff_user
from app.api.upload import (
    MAX_UPLOAD_SIZE_BYTES,
    validate_file
)
from app.database.database import get_db
from app.models.processing_job_model import (
    AsyncResumeSubmissionResponse,
    ExactDuplicateResumeResponse
)
from app.services.async_resume_submission_service import (
    AsyncResumeSubmissionError,
    submit_resume
)
from app.services.resume_fingerprint_service import (
    DuplicateResumeError
)


router = APIRouter(
    prefix="/upload",
    tags=["Resume Upload"]
)


@router.post(
    "/async",
    dependencies=[
        Depends(get_current_staff_user)
    ],
    response_model=AsyncResumeSubmissionResponse,
    responses={
        status.HTTP_409_CONFLICT: {
            "model": ExactDuplicateResumeResponse
        }
    },
    status_code=status.HTTP_202_ACCEPTED,
    summary="Submit a resume for asynchronous processing"
)
def upload_document_async(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    try:
        file_bytes = file.file.read(
            MAX_UPLOAD_SIZE_BYTES + 1
        )
        validate_file(
            file,
            file_bytes
        )

        try:
            processing_job = submit_resume(
                db,
                (file.filename or "").strip(),
                file_bytes
            )
        except DuplicateResumeError as error:
            duplicate = ExactDuplicateResumeResponse(
                message=(
                    "This exact resume file already exists"
                ),
                candidate_id=error.candidate_id
            )
            return JSONResponse(
                status_code=status.HTTP_409_CONFLICT,
                content=duplicate.model_dump()
            )
        except AsyncResumeSubmissionError as error:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=(
                    "Async resume submission "
                    "is unavailable"
                )
            ) from error

        return AsyncResumeSubmissionResponse(
            processing_job_id=processing_job.id,
            status=processing_job.status
        )
    finally:
        try:
            file.file.close()
        except Exception:
            pass
