import re
import threading

from google.cloud import pubsub_v1

from app.core import config
from app.models.resume_processing_message import (
    ResumeProcessingMessage,
    serialize_resume_processing_message,
    validate_resume_processing_message
)


_PROJECT_ID_PATTERN = re.compile(
    r"^[a-z][a-z0-9:.-]{4,254}$"
)
_TOPIC_ID_PATTERN = re.compile(
    r"^[A-Za-z][A-Za-z0-9._~+%-]{2,254}$"
)
_PUBLISH_TIMEOUT_SECONDS = 10

_publisher_client = None
_client_lock = threading.Lock()


class PubSubPublisherError(RuntimeError):
    """Base exception for the Pub/Sub publishing boundary."""


class PubSubConfigurationError(PubSubPublisherError):
    """Raised when Pub/Sub application configuration is invalid."""


class PubSubOperationError(PubSubPublisherError):
    """Raised when Pub/Sub publication fails."""


def get_publisher_client():
    """Create an ADC-backed publisher client only when first used."""

    global _publisher_client

    if _publisher_client is None:

        with _client_lock:

            if _publisher_client is None:

                try:
                    _publisher_client = (
                        pubsub_v1.PublisherClient()
                    )
                except Exception as error:
                    raise PubSubOperationError(
                        "Unable to create the Pub/Sub publisher"
                    ) from error

    return _publisher_client


def publish_resume_processing_message(
    message: ResumeProcessingMessage | dict
) -> str:

    validated = validate_resume_processing_message(
        message
    )
    project_id, topic_id = _validated_config()
    payload = serialize_resume_processing_message(
        validated
    )

    try:
        client = get_publisher_client()
        topic_path = client.topic_path(
            project_id,
            topic_id
        )
        future = client.publish(
            topic_path,
            payload
        )
        message_id = future.result(
            timeout=_PUBLISH_TIMEOUT_SECONDS
        )
    except PubSubPublisherError:
        raise
    except Exception as error:
        raise PubSubOperationError(
            "Resume processing message could not be published"
        ) from error

    return str(message_id)


def _validated_config() -> tuple[str, str]:

    project_id = (
        config.GCP_PROJECT_ID
        or ""
    ).strip()
    topic_id = (
        config.PUBSUB_RESUME_PROCESSING_TOPIC
        or ""
    ).strip()

    if not _PROJECT_ID_PATTERN.fullmatch(project_id):
        raise PubSubConfigurationError(
            "GCP_PROJECT_ID is missing or invalid"
        )

    if (
        not _TOPIC_ID_PATTERN.fullmatch(topic_id)
        or topic_id.casefold().startswith("goog")
    ):
        raise PubSubConfigurationError(
            "PUBSUB_RESUME_PROCESSING_TOPIC is missing or invalid"
        )

    return project_id, topic_id
