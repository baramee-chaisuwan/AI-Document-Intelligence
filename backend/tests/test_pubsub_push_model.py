import base64
import json

import pytest

from app.core import config
from app.models.pubsub_push_model import (
    PubSubPushEnvelopeError,
    parse_pubsub_push_envelope
)


@pytest.fixture(autouse=True)
def configured_gcs_prefix(monkeypatch):

    monkeypatch.setattr(
        config,
        "GCS_KEY_PREFIX",
        "resumes"
    )


def encode_application_message(payload) -> str:

    return base64.b64encode(
        json.dumps(payload).encode("utf-8")
    ).decode("ascii")


def test_valid_pubsub_envelope_returns_application_message():

    message = parse_pubsub_push_envelope({
        "message": {
            "data": encode_application_message({
                "version": 1,
                "processing_job_id": 42,
                "gcs_object_key": "resumes/42/document.pdf"
            }),
            "messageId": "provider-message-id"
        },
        "subscription": "projects/test/subscriptions/resumes"
    })

    assert message.version == 1
    assert message.processing_job_id == 42
    assert message.gcs_object_key == (
        "resumes/42/document.pdf"
    )


@pytest.mark.parametrize(
    "envelope",
    [
        None,
        [],
        {},
        {"message": None},
        {"message": {}},
        {"message": {"data": None}},
        {"message": {"data": ""}},
    ]
)
def test_missing_message_or_data_is_rejected(envelope):

    with pytest.raises(PubSubPushEnvelopeError):
        parse_pubsub_push_envelope(envelope)


def test_malformed_base64_is_rejected():

    with pytest.raises(PubSubPushEnvelopeError):
        parse_pubsub_push_envelope({
            "message": {
                "data": "not-valid-base64%%%"
            }
        })


@pytest.mark.parametrize(
    "decoded_data",
    [
        b"\xff\xfe",
        b"not-json",
        b"[]",
    ]
)
def test_invalid_utf8_or_json_is_rejected(decoded_data):

    with pytest.raises(PubSubPushEnvelopeError):
        parse_pubsub_push_envelope({
            "message": {
                "data": base64.b64encode(
                    decoded_data
                ).decode("ascii")
            }
        })


def test_invalid_resume_processing_message_is_rejected():

    with pytest.raises(PubSubPushEnvelopeError):
        parse_pubsub_push_envelope({
            "message": {
                "data": encode_application_message({
                    "version": 2,
                    "processing_job_id": 42,
                    "gcs_object_key": "resumes/42/document.pdf"
                })
            }
        })
