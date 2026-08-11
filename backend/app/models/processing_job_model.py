from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.processing_job_status import (
    ProcessingJobStatus
)


class ResumeProcessingJobResponse(BaseModel):

    model_config = ConfigDict(
        from_attributes=True
    )

    id: int
    candidate_id: int | None
    status: ProcessingJobStatus
    error_message: str | None
    created_at: datetime
    started_at: datetime | None
    completed_at: datetime | None
    updated_at: datetime


class AsyncResumeSubmissionResponse(BaseModel):

    processing_job_id: int
    status: ProcessingJobStatus
