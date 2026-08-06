import hashlib
import ipaddress
import re
import threading
import unicodedata
from dataclasses import dataclass
from typing import Mapping
from urllib.parse import quote

from google.api_core.exceptions import (
    GoogleAPIError,
    NotFound
)
from google.auth.exceptions import GoogleAuthError
from google.cloud import storage

from app.core import config


_BUCKET_PATTERN = re.compile(
    r"^[a-z0-9][a-z0-9._-]{1,61}[a-z0-9]$"
)
_DOCUMENT_ID_PATTERN = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9_-]{0,127}$"
)
_PREFIX_SEGMENT_PATTERN = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$"
)
_METADATA_KEY_PATTERN = re.compile(
    r"^[a-z0-9][a-z0-9-]{0,63}$"
)
_CONTROL_CHARACTER_PATTERN = re.compile(
    r"[\x00-\x1f\x7f]"
)
_MAX_METADATA_BYTES = 1800

_storage_client = None
_client_lock = threading.Lock()


class GCSStorageError(RuntimeError):
    """Base exception for failures in the GCS storage boundary."""


class GCSConfigurationError(GCSStorageError):
    """Raised when GCS application configuration is missing or invalid."""


class GCSValidationError(GCSStorageError):
    """Raised when an object key, filename, payload, or metadata is unsafe."""


class GCSClientError(GCSStorageError):
    """Raised when the ADC-backed GCS client cannot be created."""


class GCSOperationError(GCSStorageError):
    """Raised when a GCS upload or delete request fails."""


@dataclass(frozen=True)
class StoredGCSObject:
    bucket: str
    key: str
    etag: str | None = None


def get_storage_client():
    """Create an ADC-backed GCS client on first use and reuse it."""

    global _storage_client

    if _storage_client is None:

        with _client_lock:

            if _storage_client is None:

                try:

                    _storage_client = storage.Client()

                except (
                    GoogleAuthError,
                    GoogleAPIError
                ) as error:

                    raise GCSClientError(
                        "Unable to create the GCS client"
                    ) from error

    return _storage_client


def build_object_key(
    document_id: str | int,
    filename: str
) -> str:
    """Build a deterministic key without exposing the filename."""

    _, prefix = _validated_storage_config()
    safe_document_id = _validate_document_id(
        document_id
    )
    safe_filename = _normalize_filename(
        filename
    )
    filename_digest = hashlib.sha256(
        safe_filename.encode("utf-8")
    ).hexdigest()

    return (
        f"{prefix}/{safe_document_id}/"
        f"{filename_digest}.pdf"
    )


def put_object(
    *,
    document_id: str | int,
    filename: str,
    content: bytes,
    metadata: Mapping[str, str] | None = None
) -> StoredGCSObject:
    """Upload one private PDF object to the configured GCS bucket."""

    bucket_name, _ = _validated_storage_config()
    safe_document_id = _validate_document_id(
        document_id
    )
    safe_filename = _normalize_filename(
        filename
    )
    payload = _validate_content(
        content
    )
    object_key = build_object_key(
        safe_document_id,
        safe_filename
    )
    safe_metadata = _prepare_metadata(
        document_id=safe_document_id,
        filename=safe_filename,
        metadata=metadata
    )

    try:

        bucket = get_storage_client().bucket(
            bucket_name
        )
        blob = bucket.blob(
            object_key
        )
        blob.metadata = safe_metadata
        blob.upload_from_string(
            payload,
            content_type="application/pdf",
            if_generation_match=0
        )

    except (
        GoogleAuthError,
        GoogleAPIError
    ) as error:

        raise GCSOperationError(
            _operation_error_message(
                "upload",
                error
            )
        ) from error

    etag = getattr(
        blob,
        "etag",
        None
    )

    if isinstance(etag, str):

        etag = etag.strip('"') or None

    else:

        etag = None

    return StoredGCSObject(
        bucket=bucket_name,
        key=object_key,
        etag=etag
    )


def delete_object(
    object_key: str
) -> None:
    """Delete an object only when its key is under the configured prefix."""

    bucket_name, prefix = _validated_storage_config()
    safe_object_key = _validate_object_key(
        object_key,
        prefix
    )

    try:

        bucket = get_storage_client().bucket(
            bucket_name
        )
        blob = bucket.blob(
            safe_object_key
        )
        blob.delete()

    except NotFound:

        return

    except (
        GoogleAuthError,
        GoogleAPIError
    ) as error:

        raise GCSOperationError(
            _operation_error_message(
                "delete",
                error
            )
        ) from error


def _validated_storage_config() -> tuple[str, str]:

    bucket = (
        config.GCS_BUCKET_NAME
        or ""
    ).strip()
    prefix = (
        config.GCS_KEY_PREFIX
        or ""
    ).strip().strip("/")

    if not _is_valid_bucket_name(
        bucket
    ):

        raise GCSConfigurationError(
            "GCS_BUCKET_NAME is missing or invalid"
        )

    if (
        not prefix
        or len(prefix.encode("utf-8")) > 512
        or "\\" in prefix
    ):

        raise GCSConfigurationError(
            "GCS_KEY_PREFIX is missing or invalid"
        )

    segments = prefix.split("/")

    if any(
        segment in {".", ".."}
        or not _PREFIX_SEGMENT_PATTERN.fullmatch(
            segment
        )
        for segment in segments
    ):

        raise GCSConfigurationError(
            "GCS_KEY_PREFIX is missing or invalid"
        )

    return bucket, prefix


def _is_valid_bucket_name(
    bucket: str
) -> bool:

    if (
        not _BUCKET_PATTERN.fullmatch(
            bucket
        )
        or ".." in bucket
    ):

        return False

    try:

        ipaddress.ip_address(
            bucket
        )

    except ValueError:

        return True

    return False


def _validate_document_id(
    document_id: str | int
) -> str:

    normalized = str(
        document_id
    ).strip()

    if not _DOCUMENT_ID_PATTERN.fullmatch(
        normalized
    ):

        raise GCSValidationError(
            "document_id is invalid"
        )

    return normalized


def _normalize_filename(
    filename: str
) -> str:

    if not isinstance(
        filename,
        str
    ):

        raise GCSValidationError(
            "filename must be a string"
        )

    normalized = unicodedata.normalize(
        "NFKC",
        filename
    ).replace("\\", "/")
    normalized = normalized.rsplit(
        "/",
        maxsplit=1
    )[-1].strip()

    if (
        not normalized
        or _CONTROL_CHARACTER_PATTERN.search(
            normalized
        )
        or len(normalized.encode("utf-8")) > 255
        or not normalized.casefold().endswith(
            ".pdf"
        )
    ):

        raise GCSValidationError(
            "filename must be a valid PDF filename"
        )

    return normalized


def _validate_content(
    content: bytes
) -> bytes:

    if (
        not isinstance(content, bytes)
        or not content
    ):

        raise GCSValidationError(
            "content must be non-empty bytes"
        )

    return content


def _prepare_metadata(
    *,
    document_id: str,
    filename: str,
    metadata: Mapping[str, str] | None
) -> dict[str, str]:

    safe_metadata = {
        "document-id": document_id,
        "original-filename": quote(
            filename,
            safe="-_.~"
        )
    }

    for key, value in (
        metadata
        or {}
    ).items():

        if (
            not isinstance(key, str)
            or not isinstance(value, str)
        ):

            raise GCSValidationError(
                "metadata keys and values must be strings"
            )

        normalized_key = key.strip().lower()

        if (
            not _METADATA_KEY_PATTERN.fullmatch(
                normalized_key
            )
            or normalized_key in safe_metadata
        ):

            raise GCSValidationError(
                "metadata key is invalid or reserved"
            )

        if _CONTROL_CHARACTER_PATTERN.search(
            value
        ):

            raise GCSValidationError(
                "metadata value contains control characters"
            )

        safe_metadata[normalized_key] = quote(
            value,
            safe="-_.~"
        )

    metadata_size = sum(
        len(key.encode("ascii"))
        + len(value.encode("ascii"))
        for key, value in safe_metadata.items()
    )

    if metadata_size > _MAX_METADATA_BYTES:

        raise GCSValidationError(
            "metadata is too large"
        )

    return safe_metadata


def _validate_object_key(
    object_key: str,
    prefix: str
) -> str:

    if (
        not isinstance(object_key, str)
        or not object_key
        or len(object_key.encode("utf-8")) > 1024
        or "\\" in object_key
        or _CONTROL_CHARACTER_PATTERN.search(
            object_key
        )
        or not object_key.startswith(
            f"{prefix}/"
        )
    ):

        raise GCSValidationError(
            "object key is invalid"
        )

    segments = object_key.split("/")

    if any(
        segment in {"", ".", ".."}
        for segment in segments
    ):

        raise GCSValidationError(
            "object key is invalid"
        )

    return object_key


def _operation_error_message(
    operation: str,
    error: Exception
) -> str:

    error_code = getattr(
        error,
        "code",
        None
    )

    if error_code is not None:

        return (
            f"GCS {operation} failed "
            f"({error_code})"
        )

    return f"GCS {operation} failed"
