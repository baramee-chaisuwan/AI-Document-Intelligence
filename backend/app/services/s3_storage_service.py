import hashlib
import ipaddress
import re
import threading
import unicodedata
from dataclasses import dataclass
from typing import Mapping
from urllib.parse import quote

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from app.core import config


_BUCKET_PATTERN = re.compile(r"^[a-z0-9][a-z0-9.-]{1,61}[a-z0-9]$")
_DOCUMENT_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,127}$")
_PREFIX_SEGMENT_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
_METADATA_KEY_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}$")
_CONTROL_CHARACTER_PATTERN = re.compile(r"[\x00-\x1f\x7f]")
_MAX_METADATA_BYTES = 1800

_s3_client = None
_client_lock = threading.Lock()


class S3StorageError(RuntimeError):
    """Base exception for failures in the S3 storage boundary."""


class S3ConfigurationError(S3StorageError):
    """Raised when S3 application configuration is missing or invalid."""


class S3ValidationError(S3StorageError):
    """Raised when an object key, filename, payload, or metadata is unsafe."""


class S3ClientError(S3StorageError):
    """Raised when boto3 cannot create an S3 client."""


class S3OperationError(S3StorageError):
    """Raised when an S3 PutObject or DeleteObject request fails."""


@dataclass(frozen=True)
class StoredS3Object:
    bucket: str
    key: str
    etag: str | None = None


def get_s3_client():
    """Create the boto3 S3 client on first use and reuse it thereafter."""

    global _s3_client

    if _s3_client is None:
        with _client_lock:
            if _s3_client is None:
                try:
                    # No credentials are passed here. Boto3 resolves them through
                    # its standard credential provider chain.
                    _s3_client = boto3.client("s3")
                except BotoCoreError as exc:
                    raise S3ClientError("Unable to create the S3 client") from exc

    return _s3_client


def build_object_key(document_id: str | int, filename: str) -> str:
    """Build a deterministic key without placing the original filename in it."""

    _, prefix = _validated_storage_config()
    safe_document_id = _validate_document_id(document_id)
    safe_filename = _normalize_filename(filename)
    filename_digest = hashlib.sha256(safe_filename.encode("utf-8")).hexdigest()

    return f"{prefix}/{safe_document_id}/{filename_digest}.pdf"


def put_object(
    *,
    document_id: str | int,
    filename: str,
    content: bytes,
    metadata: Mapping[str, str] | None = None,
) -> StoredS3Object:
    """Store one PDF object using server-side encryption managed by S3."""

    bucket, _ = _validated_storage_config()
    safe_document_id = _validate_document_id(document_id)
    safe_filename = _normalize_filename(filename)
    payload = _validate_content(content)
    object_key = build_object_key(safe_document_id, safe_filename)
    safe_metadata = _prepare_metadata(
        document_id=safe_document_id,
        filename=safe_filename,
        metadata=metadata,
    )

    try:
        response = get_s3_client().put_object(
            Bucket=bucket,
            Key=object_key,
            Body=payload,
            ContentType="application/pdf",
            Metadata=safe_metadata,
            ServerSideEncryption="AES256",
        )
    except (BotoCoreError, ClientError) as exc:
        raise S3OperationError(_operation_error_message("PutObject", exc)) from exc

    etag = response.get("ETag")
    if isinstance(etag, str):
        etag = etag.strip('"') or None
    else:
        etag = None

    return StoredS3Object(bucket=bucket, key=object_key, etag=etag)


def delete_object(object_key: str) -> None:
    """Delete an object only when its key belongs to the configured prefix."""

    bucket, prefix = _validated_storage_config()
    safe_object_key = _validate_object_key(object_key, prefix)

    try:
        get_s3_client().delete_object(
            Bucket=bucket,
            Key=safe_object_key,
        )
    except (BotoCoreError, ClientError) as exc:
        raise S3OperationError(_operation_error_message("DeleteObject", exc)) from exc


def _validated_storage_config() -> tuple[str, str]:
    bucket = (config.S3_BUCKET_NAME or "").strip()
    prefix = (config.S3_KEY_PREFIX or "").strip().strip("/")

    if not _is_valid_bucket_name(bucket):
        raise S3ConfigurationError("S3_BUCKET_NAME is missing or invalid")

    if not prefix or len(prefix.encode("utf-8")) > 512 or "\\" in prefix:
        raise S3ConfigurationError("S3_KEY_PREFIX is missing or invalid")

    segments = prefix.split("/")
    if any(
        segment in {".", ".."}
        or not _PREFIX_SEGMENT_PATTERN.fullmatch(segment)
        for segment in segments
    ):
        raise S3ConfigurationError("S3_KEY_PREFIX is missing or invalid")

    return bucket, prefix


def _is_valid_bucket_name(bucket: str) -> bool:
    if not _BUCKET_PATTERN.fullmatch(bucket) or ".." in bucket:
        return False

    try:
        ipaddress.ip_address(bucket)
    except ValueError:
        return True

    return False


def _validate_document_id(document_id: str | int) -> str:
    normalized = str(document_id).strip()
    if not _DOCUMENT_ID_PATTERN.fullmatch(normalized):
        raise S3ValidationError("document_id is invalid")
    return normalized


def _normalize_filename(filename: str) -> str:
    if not isinstance(filename, str):
        raise S3ValidationError("filename must be a string")

    normalized = unicodedata.normalize("NFKC", filename).replace("\\", "/")
    normalized = normalized.rsplit("/", maxsplit=1)[-1].strip()

    if (
        not normalized
        or _CONTROL_CHARACTER_PATTERN.search(normalized)
        or len(normalized.encode("utf-8")) > 255
        or not normalized.casefold().endswith(".pdf")
    ):
        raise S3ValidationError("filename must be a valid PDF filename")

    return normalized


def _validate_content(content: bytes) -> bytes:
    if not isinstance(content, bytes) or not content:
        raise S3ValidationError("content must be non-empty bytes")
    return content


def _prepare_metadata(
    *,
    document_id: str,
    filename: str,
    metadata: Mapping[str, str] | None,
) -> dict[str, str]:
    safe_metadata = {
        "document-id": document_id,
        "original-filename": quote(filename, safe="-_.~"),
    }

    for key, value in (metadata or {}).items():
        if not isinstance(key, str) or not isinstance(value, str):
            raise S3ValidationError("metadata keys and values must be strings")

        normalized_key = key.strip().lower()
        if (
            not _METADATA_KEY_PATTERN.fullmatch(normalized_key)
            or normalized_key in safe_metadata
        ):
            raise S3ValidationError("metadata key is invalid or reserved")

        if _CONTROL_CHARACTER_PATTERN.search(value):
            raise S3ValidationError("metadata value contains control characters")

        safe_metadata[normalized_key] = quote(value, safe="-_.~")

    metadata_size = sum(
        len(key.encode("ascii")) + len(value.encode("ascii"))
        for key, value in safe_metadata.items()
    )
    if metadata_size > _MAX_METADATA_BYTES:
        raise S3ValidationError("metadata is too large")

    return safe_metadata


def _validate_object_key(object_key: str, prefix: str) -> str:
    if (
        not isinstance(object_key, str)
        or not object_key
        or len(object_key.encode("utf-8")) > 1024
        or "\\" in object_key
        or _CONTROL_CHARACTER_PATTERN.search(object_key)
        or not object_key.startswith(f"{prefix}/")
    ):
        raise S3ValidationError("object key is invalid")

    segments = object_key.split("/")
    if any(segment in {"", ".", ".."} for segment in segments):
        raise S3ValidationError("object key is invalid")

    return object_key


def _operation_error_message(operation: str, exc: Exception) -> str:
    error_code = None
    if isinstance(exc, ClientError):
        error_code = exc.response.get("Error", {}).get("Code")

    if error_code:
        return f"S3 {operation} failed ({error_code})"
    return f"S3 {operation} failed"
