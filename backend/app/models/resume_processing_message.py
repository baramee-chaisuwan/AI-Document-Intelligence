import json
import re
from typing import Any, Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    ValidationError,
    field_validator
)

from app.core import config


_CONTROL_CHARACTER_PATTERN = re.compile(
    r"[\x00-\x1f\x7f]"
)


class ResumeProcessingMessageError(ValueError):
    """Raised when a resume-processing message is malformed."""


class ResumeProcessingMessage(BaseModel):

    model_config = ConfigDict(
        extra="forbid",
        frozen=True
    )

    version: Literal[1]
    processing_job_id: int = Field(
        strict=True,
        gt=0
    )
    gcs_object_key: str = Field(
        strict=True,
        min_length=1,
        max_length=1024
    )

    @field_validator("gcs_object_key")
    @classmethod
    def validate_gcs_object_key(
        cls,
        value: str
    ) -> str:

        prefix = (
            config.GCS_KEY_PREFIX
            or ""
        ).strip().strip("/")

        if (
            value != value.strip()
            or "\\" in value
            or _CONTROL_CHARACTER_PATTERN.search(value)
            or not prefix
            or not value.startswith(f"{prefix}/")
            or not value.casefold().endswith(".pdf")
        ):
            raise ValueError(
                "gcs_object_key is invalid"
            )

        segments = value.split("/")

        if any(
            segment in {"", ".", ".."}
            for segment in segments
        ):
            raise ValueError(
                "gcs_object_key is invalid"
            )

        return value


def validate_resume_processing_message(
    payload: ResumeProcessingMessage | dict[str, Any]
) -> ResumeProcessingMessage:

    if isinstance(payload, ResumeProcessingMessage):
        return payload

    try:
        return ResumeProcessingMessage.model_validate(
            payload
        )
    except ValidationError as error:
        raise ResumeProcessingMessageError(
            "Resume processing message is invalid"
        ) from error


def parse_resume_processing_message(
    payload: (
        ResumeProcessingMessage
        | bytes
        | str
        | dict[str, Any]
    )
) -> ResumeProcessingMessage:

    if isinstance(payload, ResumeProcessingMessage):
        return payload

    if isinstance(payload, dict):
        return validate_resume_processing_message(
            payload
        )

    if not isinstance(payload, (bytes, str)):
        raise ResumeProcessingMessageError(
            "Resume processing message is invalid"
        )

    try:
        decoded = json.loads(payload)
    except (
        UnicodeDecodeError,
        json.JSONDecodeError,
        TypeError
    ) as error:
        raise ResumeProcessingMessageError(
            "Resume processing message is invalid"
        ) from error

    if not isinstance(decoded, dict):
        raise ResumeProcessingMessageError(
            "Resume processing message is invalid"
        )

    return validate_resume_processing_message(
        decoded
    )


def serialize_resume_processing_message(
    message: ResumeProcessingMessage
) -> bytes:

    validated = validate_resume_processing_message(
        message
    )

    return json.dumps(
        validated.model_dump(mode="json"),
        sort_keys=True,
        separators=(",", ":")
    ).encode("utf-8")
