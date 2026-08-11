import base64
import json
from unittest.mock import MagicMock, Mock

import pytest
from fastapi.testclient import TestClient

from app.api import pubsub_receiver
from app.core import config
from app.core.exceptions import NotFoundError
from app.database.database import get_db
from app.services.resume_processing_worker import (
    ResumeWorkerError,
    ResumeWorkerResult,
    WorkerOutcome
)
from main import app as public_api_app
from worker_main import app as worker_app


def override_get_db():

    yield MagicMock()


@pytest.fixture(autouse=True)
def isolated_worker_receiver(monkeypatch):

    worker_app.dependency_overrides[get_db] = (
        override_get_db
    )
    monkeypatch.setattr(
        config,
        "GCS_KEY_PREFIX",
        "resumes"
    )

    yield

    worker_app.dependency_overrides.clear()


@pytest.fixture
def client():

    return TestClient(worker_app)


def push_envelope(job_id=42):

    payload = json.dumps({
        "version": 1,
        "processing_job_id": job_id,
        "gcs_object_key": "resumes/42/document.pdf"
    }).encode("utf-8")

    return {
        "message": {
            "data": base64.b64encode(
                payload
            ).decode("ascii"),
            "messageId": "provider-message-id"
        },
        "subscription": "projects/test/subscriptions/resumes"
    }


@pytest.mark.parametrize(
    "outcome",
    [
        WorkerOutcome.COMPLETED,
        WorkerOutcome.ALREADY_COMPLETED,
        WorkerOutcome.ALREADY_PROCESSING,
        WorkerOutcome.TERMINAL_FAILED,
    ]
)
def test_acknowledged_worker_outcomes_return_204(
    client,
    monkeypatch,
    outcome
):

    worker = Mock(return_value=ResumeWorkerResult(
        processing_job_id=42,
        outcome=outcome,
        candidate_id=(
            7
            if outcome in {
                WorkerOutcome.COMPLETED,
                WorkerOutcome.ALREADY_COMPLETED
            }
            else None
        )
    ))
    monkeypatch.setattr(
        pubsub_receiver,
        "handle_resume_processing_message",
        worker
    )

    response = client.post(
        "/internal/pubsub/resume-processing",
        json=push_envelope()
    )

    assert response.status_code == 204
    assert response.content == b""
    worker.assert_called_once()
    application_message = worker.call_args.args[1]
    assert application_message.processing_job_id == 42


def test_processing_failure_returns_retryable_response(
    client,
    monkeypatch
):

    worker = Mock(side_effect=ResumeWorkerError(
        "internal worker failure"
    ))
    monkeypatch.setattr(
        pubsub_receiver,
        "handle_resume_processing_message",
        worker
    )

    response = client.post(
        "/internal/pubsub/resume-processing",
        json=push_envelope()
    )

    assert response.status_code == 503
    assert response.json() == {
        "detail": "Resume processing temporarily failed"
    }
    worker.assert_called_once()


@pytest.mark.parametrize(
    "request_kwargs",
    [
        {
            "content": b"not-json",
            "headers": {"content-type": "application/json"}
        },
        {"json": {}},
        {"json": {"message": {}}},
        {
            "json": {
                "message": {
                    "data": "not-valid-base64%%%"
                }
            }
        },
    ]
)
def test_permanently_malformed_messages_are_acknowledged(
    client,
    monkeypatch,
    request_kwargs
):

    worker = Mock()
    monkeypatch.setattr(
        pubsub_receiver,
        "handle_resume_processing_message",
        worker
    )

    response = client.post(
        "/internal/pubsub/resume-processing",
        **request_kwargs
    )

    assert response.status_code == 204
    worker.assert_not_called()


def test_missing_processing_job_is_permanently_acknowledged(
    client,
    monkeypatch
):

    monkeypatch.setattr(
        pubsub_receiver,
        "handle_resume_processing_message",
        Mock(side_effect=NotFoundError(
            "Processing job not found"
        ))
    )

    response = client.post(
        "/internal/pubsub/resume-processing",
        json=push_envelope()
    )

    assert response.status_code == 204


def test_worker_receiver_relies_on_cloud_run_iam_not_recruiter_jwt(
    client,
    monkeypatch
):

    monkeypatch.setattr(
        pubsub_receiver,
        "handle_resume_processing_message",
        Mock(return_value=ResumeWorkerResult(
            processing_job_id=42,
            outcome=WorkerOutcome.COMPLETED,
            candidate_id=7
        ))
    )

    response = client.post(
        "/internal/pubsub/resume-processing",
        json=push_envelope()
    )

    assert response.status_code == 204


def test_public_api_does_not_expose_internal_worker_route():

    with TestClient(public_api_app) as client:
        response = client.post(
            "/internal/pubsub/resume-processing",
            json=push_envelope()
        )

    assert response.status_code == 404


def test_worker_health_endpoint_is_available(client):

    response = client.get("/health/")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
