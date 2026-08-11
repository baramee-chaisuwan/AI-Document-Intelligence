import base64
import binascii

from app.models.resume_processing_message import (
    ResumeProcessingMessage,
    ResumeProcessingMessageError,
    parse_resume_processing_message
)


class PubSubPushEnvelopeError(ValueError):
    """Raised when a Pub/Sub push envelope is permanently invalid."""


def parse_pubsub_push_envelope(
    envelope
) -> ResumeProcessingMessage:

    if not isinstance(envelope, dict):
        raise PubSubPushEnvelopeError(
            "Pub/Sub push envelope is invalid"
        )

    provider_message = envelope.get("message")

    if not isinstance(provider_message, dict):
        raise PubSubPushEnvelopeError(
            "Pub/Sub push envelope is invalid"
        )

    encoded_data = provider_message.get("data")

    if (
        not isinstance(encoded_data, str)
        or not encoded_data
    ):
        raise PubSubPushEnvelopeError(
            "Pub/Sub push envelope is invalid"
        )

    try:
        decoded_data = base64.b64decode(
            encoded_data,
            validate=True
        )
    except (
        binascii.Error,
        ValueError
    ) as error:
        raise PubSubPushEnvelopeError(
            "Pub/Sub push envelope is invalid"
        ) from error

    try:
        return parse_resume_processing_message(
            decoded_data
        )
    except ResumeProcessingMessageError as error:
        raise PubSubPushEnvelopeError(
            "Pub/Sub application message is invalid"
        ) from error
