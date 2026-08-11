from fastapi import (
    APIRouter,
    UploadFile,
    File,
    HTTPException,
    Depends
)
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import (
    IntegrityError,
    SQLAlchemyError
)
from typing import Union
import logging
import os

from app.api.dependencies import (
    get_current_staff_user
)
from app.models.resume_model import (
    ResumeResponse,
    DuplicateResponse
)
from app.models.processing_job_model import (
    ExactDuplicateResumeResponse
)

from app.database.database import get_db
from app.database.models import Candidate
from app.services.gcs_storage_service import (
    GCSStorageError
)
from app.services.indexing_service import (
    ResumeIndexingError
)
from app.services import resume_fingerprint_service
from app.services.resume_fingerprint_service import (
    DuplicateResumeError,
    ResumeFingerprintReservationError
)


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/upload",
    tags=["Resume Upload"]
)

MAX_UPLOAD_SIZE_MB = int(
    os.getenv("MAX_UPLOAD_SIZE_MB", "10")
)

MAX_UPLOAD_SIZE_BYTES = (
    MAX_UPLOAD_SIZE_MB
    * 1024
    * 1024
)

def extract_text_from_pdf(file_bytes):

    from app.services.pdf_service import (
        extract_text_from_pdf as service
    )

    return service(file_bytes)

def summarize_document(text):

    from app.services.gemini_service import (
        summarize_document as service
    )

    return service(text)

def extract_resume_data(text):

    from app.services.extraction_service import (
        extract_resume_data as service
    )

    return service(text)

def analyze_resume(data):

    from app.services.analyzer_service import (
        analyze_resume as service
    )

    return service(data)

def index_resume(
    db: Session,
    document_id: str,
    resume_text: str
):

    from app.services.indexing_service import (
        index_resume as service
    )

    return service(
        db=db,
        document_id=document_id,
        resume_text=resume_text
    )

def store_resume(
    document_id,
    filename,
    content
):

    from app.services.gcs_storage_service import (
        put_object
    )

    return put_object(
        document_id=document_id,
        filename=filename,
        content=content
    )

def delete_stored_resume(
    object_key
):

    from app.services.gcs_storage_service import (
        delete_object
    )

    return delete_object(
        object_key
    )

def validate_file(
    file,
    file_bytes
):

    filename = (
        file.filename or ""
    ).strip()

    if not filename:

        raise HTTPException(
            status_code=400,
            detail="Filename is required"
        )

    if not filename.lower().endswith(".pdf"):

        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed"
        )

    if not file_bytes:

        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty"
        )

    if len(file_bytes) > MAX_UPLOAD_SIZE_BYTES:

        raise HTTPException(
            status_code=413,
            detail=(
                "PDF file must not exceed "
                f"{MAX_UPLOAD_SIZE_MB} MB"
            )
        )

    if not file_bytes.startswith(b"%PDF-"):

        raise HTTPException(
            status_code=415,
            detail="Uploaded file is not a valid PDF"
        )

def validate_candidate_name(
    resume_data
):

    if not isinstance(
        resume_data,
        dict
    ):

        raise HTTPException(
            status_code=502,
            detail=(
                "Resume extraction returned "
                "an invalid result"
            )
        )


    candidate_name = str(
        resume_data.get("name") or ""
    ).strip()

    if (
        not candidate_name
        or candidate_name.lower() == "unknown"
    ):

        raise HTTPException(
            status_code=422,
            detail=(
                "Candidate name could not "
                "be extracted"
            )
        )


    return candidate_name

def validate_analysis(
    analysis
):

    if not isinstance(
        analysis,
        dict
    ):

        raise HTTPException(
            status_code=502,
            detail=(
                "Resume analysis returned "
                "an invalid result"
            )
        )

    required_fields = [
        "candidate_level",
        "skill_score",
        "rule_score",
        "ai_score",
        "ai_status",
        "score_breakdown"
    ]

    for field in required_fields:

        if field not in analysis:

            raise HTTPException(
                status_code=502,
                detail=(
                    "Resume analysis is missing "
                    f"the field: {field}"
                )
            )

    candidate_level = str(
        analysis.get(
            "candidate_level"
        ) or ""
    ).strip()

    if (
        not candidate_level
        or candidate_level.lower() == "unknown"
    ):

        raise HTTPException(
            status_code=422,
            detail=(
                "Candidate level could not "
                "be determined"
            )
        )

    score_fields = [
        "skill_score",
        "rule_score",
        "ai_score"
    ]

    for field in score_fields:

        score = analysis.get(field)

        if (
            isinstance(score, bool)
            or not isinstance(
                score,
                (int, float)
            )
        ):

            raise HTTPException(
                status_code=502,
                detail=(
                    f"{field} must be a number"
                )
            )

        if score < 0 or score > 100:

            raise HTTPException(
                status_code=502,
                detail=(
                    f"{field} must be between "
                    "0 and 100"
                )
            )

    if not isinstance(
        analysis.get(
            "score_breakdown"
        ),
        dict
    ):

        raise HTTPException(
            status_code=502,
            detail=(
                "Score breakdown must be "
                "an object"
            )
        )

@router.post(
    "/",
    dependencies=[
        Depends(get_current_staff_user)
    ],
    response_model=Union[
        ResumeResponse,
        DuplicateResponse,
        ExactDuplicateResumeResponse
    ],
    responses={
        409: {
            "model": ExactDuplicateResumeResponse
        }
    }
)
def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    filename = (
        file.filename or ""
    ).strip()

    file_bytes = None
    extracted_text = None
    reservation_job = None
    resume_sha256 = None

    try:

        file_bytes = file.file.read(
            MAX_UPLOAD_SIZE_BYTES + 1
        )


        validate_file(
            file,
            file_bytes
        )

        resume_sha256 = (
            resume_fingerprint_service
            .calculate_resume_sha256(
                file_bytes
            )
        )

        try:
            reservation_job = (
                resume_fingerprint_service
                .reserve_resume_fingerprint(
                    db,
                    resume_sha256
                )
            )
        except DuplicateResumeError as error:
            return _exact_duplicate_response(
                error.candidate_id
            )
        except (
            SQLAlchemyError,
            ResumeFingerprintReservationError
        ) as error:
            db.rollback()
            raise HTTPException(
                status_code=500,
                detail=(
                    "Resume duplicate check "
                    "could not be completed"
                )
            ) from error


        try:

            extracted_text = (
                extract_text_from_pdf(
                    file_bytes
                )
            )

        except Exception:

            raise HTTPException(
                status_code=422,
                detail=(
                    "The PDF could not "
                    "be processed"
                )
            )


        if (
            not extracted_text
            or not extracted_text.strip()
        ):

            raise HTTPException(
                status_code=422,
                detail=(
                    "No extractable text "
                    "was found in the PDF"
                )
            )


        extracted_text = (
            extracted_text.strip()
        )

        try:

            resume_data = (
                extract_resume_data(
                    extracted_text
                )
            )

        except Exception:

            raise HTTPException(
                status_code=503,
                detail=(
                    "Resume extraction "
                    "service is unavailable"
                )
            )

        candidate_name = (
            validate_candidate_name(
                resume_data
            )
        )

        resume_data["name"] = (
            candidate_name
        )


        try:

            summary = summarize_document(
                extracted_text
            )


            analysis = analyze_resume(
                resume_data
            )

        except Exception:

            raise HTTPException(
                status_code=503,
                detail=(
                    "Resume analysis "
                    "service is unavailable"
                )
            )

        validate_analysis(
            analysis
        )


        candidate = Candidate(
            name=candidate_name,
            summary=summary,
            candidate_level=(
                analysis[
                    "candidate_level"
                ]
            ),
            skill_score=int(
                round(
                    analysis[
                        "skill_score"
                    ]
                )
            ),
            rule_score=int(
                round(
                    analysis[
                        "rule_score"
                    ]
                )
            ),
            ai_score=int(
                round(
                    analysis[
                        "ai_score"
                    ]
                )
            ),
            ai_status=(
                analysis[
                    "ai_status"
                ]
            ),
            score_breakdown=(
                analysis[
                    "score_breakdown"
                ]
            ),
            resume_sha256=resume_sha256
        )

        stored_resume = None

        try:

            db.add(candidate)
            db.flush()

            stored_resume = store_resume(
                document_id=candidate.id,
                filename=filename,
                content=file_bytes
            )

            candidate.resume_storage_key = (
                stored_resume.key
            )
            candidate.resume_filename = (
                filename
            )

            index_resume(
                db=db,
                document_id=str(
                    candidate.id
                ),
                resume_text=(
                    extracted_text
                )
            )

            (
                resume_fingerprint_service
                .prepare_reservation_completion(
                    db,
                    reservation_job
                )
            )

            db.commit()
            reservation_job = None

        except GCSStorageError as error:

            db.rollback()

            raise HTTPException(
                status_code=503,
                detail=(
                    "Resume storage "
                    "service is unavailable"
                )
            ) from error

        except ResumeIndexingError as error:

            db.rollback()

            _compensate_resume_upload(
                stored_resume,
                candidate.id
            )

            raise HTTPException(
                status_code=503,
                detail=(
                    "Resume indexing "
                    "service is unavailable"
                )
            ) from error

        except IntegrityError as error:

            db.rollback()

            _compensate_resume_upload(
                stored_resume,
                candidate.id
            )

            existing_candidate = (
                resume_fingerprint_service
                .get_existing_candidate(
                    db,
                    resume_sha256
                )
            )

            if existing_candidate is None:
                raise HTTPException(
                    status_code=500,
                    detail="Candidate could not be saved"
                ) from error

            return _exact_duplicate_response(
                existing_candidate.id
            )

        except SQLAlchemyError as error:

            db.rollback()

            _compensate_resume_upload(
                stored_resume,
                candidate.id
            )

            raise HTTPException(
                status_code=500,
                detail=(
                    "Candidate could "
                    "not be saved"
                )
            ) from error

        return ResumeResponse(
            candidate_id=candidate.id,
            filename=filename,
            message=(
                "File uploaded and "
                "indexed successfully"
            ),
            summary=summary,
            resume_data=resume_data,
            analysis=analysis
        )

    finally:

        if reservation_job is not None:
            _release_fingerprint_reservation(
                db,
                reservation_job.id
            )

        try:

            file.file.close()

        except Exception:

            pass


def _compensate_resume_upload(
    stored_resume,
    candidate_id
):

    if stored_resume is None:

        return

    try:

        delete_stored_resume(
            stored_resume.key
        )

    except GCSStorageError:

        logger.exception(
            "GCS compensation failed after "
            "candidate persistence or indexing failure: "
            "candidate_id=%s",
            candidate_id
        )


def _release_fingerprint_reservation(
    db: Session,
    processing_job_id: int
):

    try:
        resume_fingerprint_service.release_resume_fingerprint(
            db,
            processing_job_id
        )
    except ResumeFingerprintReservationError:
        logger.exception(
            "Resume fingerprint reservation cleanup failed: "
            "job_id=%s",
            processing_job_id
        )


def _exact_duplicate_response(
    candidate_id: int | None
):

    duplicate = ExactDuplicateResumeResponse(
        message="This exact resume file already exists",
        candidate_id=candidate_id
    )

    return JSONResponse(
        status_code=409,
        content=duplicate.model_dump()
    )
