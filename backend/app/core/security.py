from datetime import (
    datetime,
    timedelta,
    timezone
)
import base64
import hashlib
import hmac
import json

import bcrypt

from app.core.config import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    JWT_ALGORITHM,
    JWT_SECRET_KEY
)


class InvalidTokenError(ValueError):
    pass


def _base64url_encode(value: bytes) -> str:

    return (
        base64.urlsafe_b64encode(value)
        .rstrip(b"=")
        .decode("ascii")
    )


def _base64url_decode(value: str) -> bytes:

    padding = "=" * (-len(value) % 4)

    try:

        return base64.urlsafe_b64decode(
            value + padding
        )

    except (ValueError, TypeError) as error:

        raise InvalidTokenError(
            "Token encoding is invalid"
        ) from error


def hash_password(password: str) -> str:

    return bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt(rounds=12)
    ).decode("utf-8")


def verify_password(
    password: str,
    hashed_password: str
) -> bool:

    try:

        return bcrypt.checkpw(
            password.encode("utf-8"),
            hashed_password.encode("utf-8")
        )

    except (TypeError, ValueError):

        return False


def _get_jwt_secret() -> str:

    if (
        not JWT_SECRET_KEY
        or len(
            JWT_SECRET_KEY.encode("utf-8")
        ) < 32
    ):

        raise RuntimeError(
            "JWT_SECRET_KEY must contain at least "
            "32 UTF-8 bytes"
        )

    return JWT_SECRET_KEY


def create_access_token(user_id: int) -> str:

    now = datetime.now(timezone.utc)

    if JWT_ALGORITHM != "HS256":

        raise RuntimeError(
            "Only the HS256 JWT algorithm is supported"
        )

    header = {
        "alg": "HS256",
        "typ": "JWT"
    }

    payload = {
        "sub": str(user_id),
        "type": "access",
        "iat": int(now.timestamp()),
        "exp": int(
            (
                now + timedelta(
                    minutes=(
                        ACCESS_TOKEN_EXPIRE_MINUTES
                    )
                )
            ).timestamp()
        )
    }

    header_segment = _base64url_encode(
        json.dumps(
            header,
            separators=(",", ":")
        ).encode("utf-8")
    )

    payload_segment = _base64url_encode(
        json.dumps(
            payload,
            separators=(",", ":")
        ).encode("utf-8")
    )

    signing_input = (
        f"{header_segment}.{payload_segment}"
    ).encode("ascii")

    signature = hmac.new(
        _get_jwt_secret().encode("utf-8"),
        signing_input,
        hashlib.sha256
    ).digest()

    return (
        f"{header_segment}."
        f"{payload_segment}."
        f"{_base64url_encode(signature)}"
    )


def decode_access_token(token: str) -> int:

    if JWT_ALGORITHM != "HS256":

        raise RuntimeError(
            "Only the HS256 JWT algorithm is supported"
        )

    try:

        header_segment, payload_segment, signature_segment = (
            token.split(".")
        )

    except ValueError as error:

        raise InvalidTokenError(
            "Token must contain three segments"
        ) from error

    signing_input = (
        f"{header_segment}.{payload_segment}"
    ).encode("ascii")

    expected_signature = hmac.new(
        _get_jwt_secret().encode("utf-8"),
        signing_input,
        hashlib.sha256
    ).digest()

    supplied_signature = _base64url_decode(
        signature_segment
    )

    if not hmac.compare_digest(
        expected_signature,
        supplied_signature
    ):

        raise InvalidTokenError(
            "Token signature is invalid"
        )

    try:

        header = json.loads(
            _base64url_decode(
                header_segment
            )
        )

        payload = json.loads(
            _base64url_decode(
                payload_segment
            )
        )

    except (
        json.JSONDecodeError,
        UnicodeDecodeError,
        TypeError
    ) as error:

        raise InvalidTokenError(
            "Token JSON is invalid"
        ) from error

    if (
        header.get("alg") != "HS256"
        or header.get("typ") != "JWT"
    ):

        raise InvalidTokenError(
            "Token header is invalid"
        )

    expires_at = payload.get("exp")

    if (
        not isinstance(expires_at, int)
        or expires_at
        <= int(
            datetime.now(
                timezone.utc
            ).timestamp()
        )
    ):

        raise InvalidTokenError(
            "Token has expired"
        )

    if payload.get("type") != "access":

        raise InvalidTokenError(
            "Invalid token type"
        )

    subject = payload.get("sub")

    if not subject:

        raise InvalidTokenError(
            "Token subject is missing"
        )

    try:

        return int(subject)

    except (TypeError, ValueError) as error:

        raise InvalidTokenError(
            "Token subject is invalid"
        ) from error
