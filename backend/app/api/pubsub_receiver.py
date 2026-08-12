import json
import logging

from fastapi import (
    APIRouter,
    Depends,
    Request,
    Response,
    status
)
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.database.database import get_db
from app.models.pubsub_push_model import (
    PubSubPushEnvelopeError,
    parse_pubsub_push_envelope
)
from app.services.resume_processing_worker import (
    ResumeWorkerError,
    WorkerOutcome,
    handle_resume_processing_message
)
from app.services.observability_service import emit_event


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/internal/pubsub",
    tags=["Internal Pub/Sub Worker"]
)

ACKNOWLEDGED_OUTCOMES = {
    WorkerOutcome.COMPLETED,
    WorkerOutcome.ALREADY_COMPLETED,
    WorkerOutcome.ALREADY_PROCESSING,
    WorkerOutcome.TERMINAL_FAILED,
}


@router.post(
    "/resume-processing",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Receive an authenticated Pub/Sub resume message",
    description=(
        "This internal endpoint must be protected by Cloud Run "
        "IAM authenticated invocation."
    )
)
async def receive_resume_processing_message(
    request: Request,
    db: Session = Depends(get_db)
):

    try:
        envelope = await request.json()
    except (
        json.JSONDecodeError,
        UnicodeDecodeError
    ):
        logger.warning(
            "Discarding malformed Pub/Sub push request"
        )
        return Response(
            status_code=status.HTTP_204_NO_CONTENT
        )

    try:
        message = parse_pubsub_push_envelope(
            envelope
        )
    except PubSubPushEnvelopeError:
        logger.warning(
            "Discarding permanently invalid Pub/Sub message"
        )
        return Response(
            status_code=status.HTTP_204_NO_CONTENT
        )

    try:
        result = handle_resume_processing_message(
            db,
            message
        )
    except NotFoundError:
        logger.warning(
            "Discarding Pub/Sub message for a missing "
            "processing job"
        )
        return Response(
            status_code=status.HTTP_204_NO_CONTENT
        )
    except ResumeWorkerError as error:
        emit_event(
            "pubsub_worker_request_failed",
            severity="ERROR",
            operation="resume_processing",
            outcome="failure",
            processing_job_id=message.processing_job_id,
            error_category=type(error).__name__
        )
        return _retryable_response()
    except Exception as error:
        emit_event(
            "pubsub_worker_request_failed",
            severity="ERROR",
            operation="resume_processing",
            outcome="failure",
            processing_job_id=message.processing_job_id,
            error_category=type(error).__name__
        )
        return _retryable_response()

    if result.outcome not in ACKNOWLEDGED_OUTCOMES:
        logger.error(
            "Resume worker returned an unsupported outcome"
        )
        return _retryable_response()

    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )


def _retryable_response() -> JSONResponse:

    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={
            "detail": "Resume processing temporarily failed"
        }
    )
