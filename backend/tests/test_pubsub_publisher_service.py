from unittest.mock import Mock

import pytest

from app.core import config
from app.models.resume_processing_message import (
    ResumeProcessingMessageError
)
from app.services import pubsub_publisher_service


@pytest.fixture(autouse=True)
def configured_publisher(monkeypatch):

    monkeypatch.setattr(
        config,
        "GCP_PROJECT_ID",
        "ats-test-project"
    )
    monkeypatch.setattr(
        config,
        "PUBSUB_RESUME_PROCESSING_TOPIC",
        "resume-processing"
    )
    monkeypatch.setattr(
        config,
        "GCS_KEY_PREFIX",
        "resumes"
    )
    monkeypatch.setattr(
        pubsub_publisher_service,
        "_publisher_client",
        None
    )


def test_publisher_client_is_initialized_lazily(
    monkeypatch
):

    client = Mock()
    client_factory = Mock(return_value=client)
    monkeypatch.setattr(
        pubsub_publisher_service.pubsub_v1,
        "PublisherClient",
        client_factory
    )

    assert pubsub_publisher_service._publisher_client is None
    assert (
        pubsub_publisher_service.get_publisher_client()
        is client
    )
    assert (
        pubsub_publisher_service.get_publisher_client()
        is client
    )
    client_factory.assert_called_once_with()


def test_publish_uses_expected_topic_and_payload(monkeypatch):

    future = Mock()
    future.result.return_value = "message-123"
    client = Mock()
    client.topic_path.return_value = (
        "projects/ats-test-project/topics/resume-processing"
    )
    client.publish.return_value = future
    monkeypatch.setattr(
        pubsub_publisher_service,
        "_publisher_client",
        client
    )

    message_id = (
        pubsub_publisher_service
        .publish_resume_processing_message({
            "version": 1,
            "processing_job_id": 42,
            "gcs_object_key": "resumes/42/document.pdf"
        })
    )

    assert message_id == "message-123"
    client.topic_path.assert_called_once_with(
        "ats-test-project",
        "resume-processing"
    )
    client.publish.assert_called_once_with(
        "projects/ats-test-project/topics/resume-processing",
        (
            b'{"gcs_object_key":"resumes/42/document.pdf",'
            b'"processing_job_id":42,"version":1}'
        )
    )
    future.result.assert_called_once_with(timeout=10)


def test_provider_failure_becomes_safe_exception(
    monkeypatch
):

    client = Mock()
    client.topic_path.return_value = (
        "projects/ats-test-project/topics/resume-processing"
    )
    client.publish.side_effect = RuntimeError(
        "provider details must not escape"
    )
    monkeypatch.setattr(
        pubsub_publisher_service,
        "_publisher_client",
        client
    )

    with pytest.raises(
        pubsub_publisher_service.PubSubOperationError
    ) as exc_info:
        (
            pubsub_publisher_service
            .publish_resume_processing_message({
                "version": 1,
                "processing_job_id": 42,
                "gcs_object_key": (
                    "resumes/42/document.pdf"
                )
            })
        )

    assert "provider details" not in str(exc_info.value)


def test_missing_configuration_does_not_create_client(
    monkeypatch
):

    client_factory = Mock()
    monkeypatch.setattr(config, "GCP_PROJECT_ID", None)
    monkeypatch.setattr(
        pubsub_publisher_service.pubsub_v1,
        "PublisherClient",
        client_factory
    )

    with pytest.raises(
        pubsub_publisher_service.PubSubConfigurationError
    ):
        (
            pubsub_publisher_service
            .publish_resume_processing_message({
                "version": 1,
                "processing_job_id": 42,
                "gcs_object_key": (
                    "resumes/42/document.pdf"
                )
            })
        )

    client_factory.assert_not_called()


def test_invalid_payload_is_not_published(monkeypatch):

    client = Mock()
    monkeypatch.setattr(
        pubsub_publisher_service,
        "_publisher_client",
        client
    )

    with pytest.raises(ResumeProcessingMessageError):
        (
            pubsub_publisher_service
            .publish_resume_processing_message({
                "version": 1,
                "processing_job_id": 0,
                "gcs_object_key": "resumes/0/document.pdf"
            })
        )

    client.publish.assert_not_called()
