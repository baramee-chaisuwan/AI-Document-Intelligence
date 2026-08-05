from unittest.mock import Mock

import pytest
from botocore.exceptions import ClientError, NoCredentialsError

from app.core import config
from app.services import s3_storage_service


@pytest.fixture(autouse=True)
def reset_s3_service(monkeypatch):
    monkeypatch.setattr(config, "S3_BUCKET_NAME", "ats-resumes-dev-k7m2x9")
    monkeypatch.setattr(config, "S3_KEY_PREFIX", "resumes")
    monkeypatch.setattr(s3_storage_service, "_s3_client", None)


def test_s3_client_is_created_lazily_and_cached(monkeypatch):
    client = Mock()
    client_factory = Mock(return_value=client)
    monkeypatch.setattr(s3_storage_service.boto3, "client", client_factory)

    assert s3_storage_service._s3_client is None
    assert s3_storage_service.get_s3_client() is client
    assert s3_storage_service.get_s3_client() is client

    client_factory.assert_called_once_with("s3")


def test_s3_client_creation_uses_typed_error(monkeypatch):
    monkeypatch.setattr(
        s3_storage_service.boto3,
        "client",
        Mock(side_effect=NoCredentialsError()),
    )

    with pytest.raises(s3_storage_service.S3ClientError) as exc_info:
        s3_storage_service.get_s3_client()

    assert "credentials" not in str(exc_info.value).lower()


@pytest.mark.parametrize(
    ("bucket", "prefix"),
    [
        (None, "resumes"),
        ("Invalid_Bucket", "resumes"),
        ("192.168.1.1", "resumes"),
        ("ats-resumes-dev-k7m2x9", "../resumes"),
        ("ats-resumes-dev-k7m2x9", "resumes\\private"),
    ],
)
def test_invalid_storage_configuration_is_rejected(monkeypatch, bucket, prefix):
    client_factory = Mock()
    monkeypatch.setattr(config, "S3_BUCKET_NAME", bucket)
    monkeypatch.setattr(config, "S3_KEY_PREFIX", prefix)
    monkeypatch.setattr(s3_storage_service.boto3, "client", client_factory)

    with pytest.raises(s3_storage_service.S3ConfigurationError):
        s3_storage_service.build_object_key("candidate-1", "resume.pdf")

    client_factory.assert_not_called()


def test_object_key_is_deterministic_and_excludes_original_filename():
    first_key = s3_storage_service.build_object_key(
        "candidate-1",
        "../../Résumé Final.PDF",
    )
    second_key = s3_storage_service.build_object_key(
        "candidate-1",
        "Résumé Final.PDF",
    )

    assert first_key == second_key
    assert first_key.startswith("resumes/candidate-1/")
    assert first_key.endswith(".pdf")
    assert "Résumé" not in first_key


def test_put_object_uses_safe_arguments_and_returns_reference(monkeypatch):
    client = Mock()
    client.put_object.return_value = {"ETag": '"abc123"'}
    monkeypatch.setattr(s3_storage_service, "_s3_client", client)

    stored_object = s3_storage_service.put_object(
        document_id=42,
        filename="Résumé Final.pdf",
        content=b"%PDF-1.7 test",
        metadata={"source": "recruiter portal"},
    )

    request = client.put_object.call_args.kwargs
    assert request["Bucket"] == "ats-resumes-dev-k7m2x9"
    assert request["Key"] == stored_object.key
    assert request["Body"] == b"%PDF-1.7 test"
    assert request["ContentType"] == "application/pdf"
    assert request["ServerSideEncryption"] == "AES256"
    assert request["Metadata"] == {
        "document-id": "42",
        "original-filename": "R%C3%A9sum%C3%A9%20Final.pdf",
        "source": "recruiter%20portal",
    }
    assert stored_object.bucket == "ats-resumes-dev-k7m2x9"
    assert stored_object.etag == "abc123"


@pytest.mark.parametrize(
    "kwargs",
    [
        {"document_id": "../42", "filename": "resume.pdf", "content": b"pdf"},
        {"document_id": "42", "filename": "resume.txt", "content": b"text"},
        {"document_id": "42", "filename": "resume.pdf", "content": b""},
        {
            "document_id": "42",
            "filename": "resume.pdf",
            "content": b"pdf",
            "metadata": {"document-id": "override"},
        },
        {
            "document_id": "42",
            "filename": "resume.pdf",
            "content": b"pdf",
            "metadata": {"unsafe_key": "value"},
        },
    ],
)
def test_put_object_rejects_unsafe_input_before_calling_s3(monkeypatch, kwargs):
    client = Mock()
    monkeypatch.setattr(s3_storage_service, "_s3_client", client)

    with pytest.raises(s3_storage_service.S3ValidationError):
        s3_storage_service.put_object(**kwargs)

    client.put_object.assert_not_called()


def test_put_object_wraps_aws_error_without_exposing_filename(monkeypatch):
    client = Mock()
    client.put_object.side_effect = ClientError(
        {"Error": {"Code": "AccessDenied", "Message": "denied"}},
        "PutObject",
    )
    monkeypatch.setattr(s3_storage_service, "_s3_client", client)

    with pytest.raises(s3_storage_service.S3OperationError) as exc_info:
        s3_storage_service.put_object(
            document_id="42",
            filename="private-name.pdf",
            content=b"pdf",
        )

    assert "AccessDenied" in str(exc_info.value)
    assert "private-name.pdf" not in str(exc_info.value)


def test_delete_object_deletes_only_from_configured_bucket_and_prefix(monkeypatch):
    client = Mock()
    monkeypatch.setattr(s3_storage_service, "_s3_client", client)
    object_key = s3_storage_service.build_object_key("42", "resume.pdf")

    s3_storage_service.delete_object(object_key)

    client.delete_object.assert_called_once_with(
        Bucket="ats-resumes-dev-k7m2x9",
        Key=object_key,
    )


def test_delete_object_rejects_key_outside_configured_prefix(monkeypatch):
    client = Mock()
    monkeypatch.setattr(s3_storage_service, "_s3_client", client)

    with pytest.raises(s3_storage_service.S3ValidationError):
        s3_storage_service.delete_object("other-prefix/42/resume.pdf")

    client.delete_object.assert_not_called()


def test_delete_object_wraps_aws_error(monkeypatch):
    client = Mock()
    client.delete_object.side_effect = ClientError(
        {"Error": {"Code": "ServiceUnavailable", "Message": "try later"}},
        "DeleteObject",
    )
    monkeypatch.setattr(s3_storage_service, "_s3_client", client)
    object_key = s3_storage_service.build_object_key("42", "resume.pdf")

    with pytest.raises(s3_storage_service.S3OperationError) as exc_info:
        s3_storage_service.delete_object(object_key)

    assert "ServiceUnavailable" in str(exc_info.value)
