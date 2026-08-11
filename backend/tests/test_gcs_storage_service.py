from unittest.mock import Mock

import pytest
from google.api_core.exceptions import (
    Forbidden,
    NotFound,
    ServiceUnavailable
)
from google.auth.exceptions import (
    DefaultCredentialsError
)

from app.core import config
from app.services import gcs_storage_service


@pytest.fixture(autouse=True)
def reset_gcs_service(monkeypatch):

    monkeypatch.setattr(
        config,
        "GCS_BUCKET_NAME",
        "ats-resumes-test"
    )
    monkeypatch.setattr(
        config,
        "GCS_KEY_PREFIX",
        "resumes"
    )
    monkeypatch.setattr(
        gcs_storage_service,
        "_storage_client",
        None
    )


def test_gcs_client_uses_adc_lazily_and_is_cached(
    monkeypatch
):

    client = Mock()
    client_factory = Mock(
        return_value=client
    )
    monkeypatch.setattr(
        gcs_storage_service.storage,
        "Client",
        client_factory
    )

    assert gcs_storage_service._storage_client is None
    assert (
        gcs_storage_service.get_storage_client()
        is client
    )
    assert (
        gcs_storage_service.get_storage_client()
        is client
    )

    client_factory.assert_called_once_with()


def test_gcs_client_creation_uses_typed_error(
    monkeypatch
):

    monkeypatch.setattr(
        gcs_storage_service.storage,
        "Client",
        Mock(
            side_effect=DefaultCredentialsError(
                "ADC unavailable"
            )
        )
    )

    with pytest.raises(
        gcs_storage_service.GCSClientError
    ) as exc_info:

        gcs_storage_service.get_storage_client()

    assert "ADC unavailable" not in str(
        exc_info.value
    )


@pytest.mark.parametrize(
    ("bucket", "prefix"),
    [
        (None, "resumes"),
        ("Invalid Bucket", "resumes"),
        ("192.168.1.1", "resumes"),
        ("ats-resumes-test", "../resumes"),
        ("ats-resumes-test", "resumes\\private")
    ]
)
def test_invalid_storage_configuration_is_rejected(
    monkeypatch,
    bucket,
    prefix
):

    client_factory = Mock()
    monkeypatch.setattr(
        config,
        "GCS_BUCKET_NAME",
        bucket
    )
    monkeypatch.setattr(
        config,
        "GCS_KEY_PREFIX",
        prefix
    )
    monkeypatch.setattr(
        gcs_storage_service.storage,
        "Client",
        client_factory
    )

    with pytest.raises(
        gcs_storage_service.GCSConfigurationError
    ):

        gcs_storage_service.build_object_key(
            "candidate-1",
            "resume.pdf"
        )

    client_factory.assert_not_called()


def test_object_key_is_deterministic_and_hides_filename():

    first_key = gcs_storage_service.build_object_key(
        "candidate-1",
        "../../Résumé Final.PDF"
    )
    second_key = gcs_storage_service.build_object_key(
        "candidate-1",
        "Résumé Final.PDF"
    )

    assert first_key == second_key
    assert first_key.startswith(
        "resumes/candidate-1/"
    )
    assert first_key.endswith(".pdf")
    assert "Résumé" not in first_key


def test_put_object_uses_private_gcs_blob_and_returns_reference(
    monkeypatch
):

    client = Mock()
    bucket = Mock()
    blob = Mock()
    blob.etag = '"abc123"'
    client.bucket.return_value = bucket
    bucket.blob.return_value = blob
    monkeypatch.setattr(
        gcs_storage_service,
        "_storage_client",
        client
    )

    stored_object = gcs_storage_service.put_object(
        document_id=42,
        filename="Résumé Final.pdf",
        content=b"%PDF-1.7 test",
        metadata={
            "source": "recruiter portal"
        }
    )

    client.bucket.assert_called_once_with(
        "ats-resumes-test"
    )
    bucket.blob.assert_called_once_with(
        stored_object.key
    )
    blob.upload_from_string.assert_called_once_with(
        b"%PDF-1.7 test",
        content_type="application/pdf",
        if_generation_match=0
    )
    assert blob.metadata == {
        "document-id": "42",
        "original-filename": (
            "R%C3%A9sum%C3%A9%20Final.pdf"
        ),
        "source": "recruiter%20portal"
    }
    blob.make_public.assert_not_called()
    assert stored_object.bucket == "ats-resumes-test"
    assert stored_object.etag == "abc123"


@pytest.mark.parametrize(
    "kwargs",
    [
        {
            "document_id": "../42",
            "filename": "resume.pdf",
            "content": b"pdf"
        },
        {
            "document_id": "42",
            "filename": "resume.txt",
            "content": b"text"
        },
        {
            "document_id": "42",
            "filename": "resume.pdf",
            "content": b""
        },
        {
            "document_id": "42",
            "filename": "resume.pdf",
            "content": b"pdf",
            "metadata": {
                "document-id": "override"
            }
        },
        {
            "document_id": "42",
            "filename": "resume.pdf",
            "content": b"pdf",
            "metadata": {
                "unsafe_key": "value"
            }
        }
    ]
)
def test_put_object_rejects_unsafe_input_before_gcs_call(
    monkeypatch,
    kwargs
):

    client = Mock()
    monkeypatch.setattr(
        gcs_storage_service,
        "_storage_client",
        client
    )

    with pytest.raises(
        gcs_storage_service.GCSValidationError
    ):

        gcs_storage_service.put_object(
            **kwargs
        )

    client.bucket.assert_not_called()


def test_put_object_wraps_gcs_error_without_filename(
    monkeypatch
):

    client = Mock()
    bucket = Mock()
    blob = Mock()
    client.bucket.return_value = bucket
    bucket.blob.return_value = blob
    blob.upload_from_string.side_effect = Forbidden(
        "denied"
    )
    monkeypatch.setattr(
        gcs_storage_service,
        "_storage_client",
        client
    )

    with pytest.raises(
        gcs_storage_service.GCSOperationError
    ) as exc_info:

        gcs_storage_service.put_object(
            document_id="42",
            filename="private-name.pdf",
            content=b"pdf"
        )

    assert "403" in str(exc_info.value)
    assert "private-name.pdf" not in str(
        exc_info.value
    )


def test_delete_object_uses_configured_bucket_and_prefix(
    monkeypatch
):

    client = Mock()
    bucket = Mock()
    blob = Mock()
    client.bucket.return_value = bucket
    bucket.blob.return_value = blob
    monkeypatch.setattr(
        gcs_storage_service,
        "_storage_client",
        client
    )
    object_key = gcs_storage_service.build_object_key(
        "42",
        "resume.pdf"
    )

    gcs_storage_service.delete_object(
        object_key
    )

    client.bucket.assert_called_once_with(
        "ats-resumes-test"
    )
    bucket.blob.assert_called_once_with(
        object_key
    )
    blob.delete.assert_called_once_with()


def test_delete_object_rejects_key_outside_prefix(
    monkeypatch
):

    client = Mock()
    monkeypatch.setattr(
        gcs_storage_service,
        "_storage_client",
        client
    )

    with pytest.raises(
        gcs_storage_service.GCSValidationError
    ):

        gcs_storage_service.delete_object(
            "other-prefix/42/resume.pdf"
        )

    client.bucket.assert_not_called()


def test_delete_object_treats_missing_blob_as_deleted(
    monkeypatch
):

    client = Mock()
    bucket = Mock()
    blob = Mock()
    client.bucket.return_value = bucket
    bucket.blob.return_value = blob
    blob.delete.side_effect = NotFound(
        "missing"
    )
    monkeypatch.setattr(
        gcs_storage_service,
        "_storage_client",
        client
    )
    object_key = gcs_storage_service.build_object_key(
        "42",
        "resume.pdf"
    )

    gcs_storage_service.delete_object(
        object_key
    )

    blob.delete.assert_called_once_with()


def test_delete_object_wraps_gcs_error(
    monkeypatch
):

    client = Mock()
    bucket = Mock()
    blob = Mock()
    client.bucket.return_value = bucket
    bucket.blob.return_value = blob
    blob.delete.side_effect = ServiceUnavailable(
        "try later"
    )
    monkeypatch.setattr(
        gcs_storage_service,
        "_storage_client",
        client
    )
    object_key = gcs_storage_service.build_object_key(
        "42",
        "resume.pdf"
    )

    with pytest.raises(
        gcs_storage_service.GCSOperationError
    ) as exc_info:

        gcs_storage_service.delete_object(
            object_key
        )

    assert "503" in str(exc_info.value)


def test_get_object_downloads_private_content(
    monkeypatch
):

    client = Mock()
    bucket = Mock()
    blob = Mock()
    blob.download_as_bytes.return_value = (
        b"%PDF-1.7 test"
    )
    client.bucket.return_value = bucket
    bucket.blob.return_value = blob
    monkeypatch.setattr(
        gcs_storage_service,
        "_storage_client",
        client
    )

    content = gcs_storage_service.get_object(
        "resumes/42/document.pdf"
    )

    assert content == b"%PDF-1.7 test"
    client.bucket.assert_called_once_with(
        "ats-resumes-test"
    )
    bucket.blob.assert_called_once_with(
        "resumes/42/document.pdf"
    )
    blob.download_as_bytes.assert_called_once_with()


def test_get_object_wraps_missing_object_safely(
    monkeypatch
):

    client = Mock()
    bucket = Mock()
    blob = Mock()
    blob.download_as_bytes.side_effect = NotFound(
        "private provider detail"
    )
    client.bucket.return_value = bucket
    bucket.blob.return_value = blob
    monkeypatch.setattr(
        gcs_storage_service,
        "_storage_client",
        client
    )

    with pytest.raises(
        gcs_storage_service.GCSOperationError
    ) as exc_info:
        gcs_storage_service.get_object(
            "resumes/42/document.pdf"
        )

    assert "private provider detail" not in str(
        exc_info.value
    )
