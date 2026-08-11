import pytest

from app.core import config
from app.models.resume_processing_message import (
    ResumeProcessingMessage,
    ResumeProcessingMessageError,
    parse_resume_processing_message,
    serialize_resume_processing_message
)


@pytest.fixture(autouse=True)
def configured_gcs_prefix(monkeypatch):

    monkeypatch.setattr(
        config,
        "GCS_KEY_PREFIX",
        "resumes"
    )


def test_valid_resume_processing_message_is_deterministic():

    message = parse_resume_processing_message({
        "version": 1,
        "processing_job_id": 123,
        "gcs_object_key": "resumes/123/document.pdf"
    })

    assert message == ResumeProcessingMessage(
        version=1,
        processing_job_id=123,
        gcs_object_key="resumes/123/document.pdf"
    )
    assert serialize_resume_processing_message(message) == (
        b'{"gcs_object_key":"resumes/123/document.pdf",'
        b'"processing_job_id":123,"version":1}'
    )


@pytest.mark.parametrize(
    "payload",
    [
        b"not-json",
        b"[]",
        {
            "version": 1,
            "processing_job_id": 1
        },
        {
            "version": 1,
            "processing_job_id": 1,
            "gcs_object_key": "resumes/1/document.pdf",
            "resume_text": "must not be accepted"
        }
    ]
)
def test_malformed_message_is_rejected(payload):

    with pytest.raises(
        ResumeProcessingMessageError,
        match="message is invalid"
    ):
        parse_resume_processing_message(payload)


def test_unsupported_message_version_is_rejected():

    with pytest.raises(ResumeProcessingMessageError):
        parse_resume_processing_message({
            "version": 2,
            "processing_job_id": 1,
            "gcs_object_key": "resumes/1/document.pdf"
        })


@pytest.mark.parametrize(
    "job_id",
    [0, -1, True, "1"]
)
def test_invalid_processing_job_id_is_rejected(job_id):

    with pytest.raises(ResumeProcessingMessageError):
        parse_resume_processing_message({
            "version": 1,
            "processing_job_id": job_id,
            "gcs_object_key": "resumes/1/document.pdf"
        })


@pytest.mark.parametrize(
    "object_key",
    [
        "other/1/document.pdf",
        "resumes/../document.pdf",
        "/resumes/1/document.pdf",
        "resumes\\1\\document.pdf",
        "resumes/1/\x00document.pdf",
        "resumes/1/document.txt"
    ]
)
def test_invalid_gcs_object_reference_is_rejected(
    object_key
):

    with pytest.raises(ResumeProcessingMessageError):
        parse_resume_processing_message({
            "version": 1,
            "processing_job_id": 1,
            "gcs_object_key": object_key
        })
