from datetime import datetime, timedelta, timezone
import logging
import secrets

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core import config
from app.core.exceptions import PasswordResetError
from app.core.security import (
    InvalidTokenError,
    create_password_reset_token,
    decode_password_reset_token,
    hash_password,
    verify_password
)
from app.database.models import PasswordResetToken
from app.models.auth_model import (
    ForgotPasswordRequest,
    PasswordResetTokenResponse,
    ResetPasswordRequest,
    VerifyResetOTPRequest
)
from app.repositories import (
    password_reset_repository,
    user_repository
)
from app.services.email_service import (
    EmailServiceError,
    send_password_reset_otp
)


logger = logging.getLogger(__name__)

FORGOT_PASSWORD_MESSAGE = (
    "If an account exists for this email, "
    "a verification code has been sent."
)
RESET_SUCCESS_MESSAGE = (
    "Password reset successfully. Please sign in "
    "with your new password."
)
INVALID_RESET_MESSAGE = (
    "Invalid or expired password reset authorization"
)
INVALID_OTP_MESSAGE = (
    "Invalid or expired verification code"
)

_DUMMY_OTP_HASH = hash_password("000000")


def _utc_now() -> datetime:

    return datetime.now(timezone.utc)


def _as_utc(value: datetime) -> datetime:

    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)

    return value.astimezone(timezone.utc)


def _generate_otp() -> str:

    return f"{secrets.randbelow(1_000_000):06d}"


def request_password_reset(
    db: Session,
    data: ForgotPasswordRequest
) -> dict:

    otp = _generate_otp()
    otp_hash = hash_password(otp)
    now = _utc_now()

    user = user_repository.get_user_by_email_for_update(
        db,
        data.email
    )

    if not user or not user.is_active:
        return {"message": FORGOT_PASSWORD_MESSAGE}

    window_start = now - timedelta(
        minutes=(
            config
            .PASSWORD_RESET_REQUEST_WINDOW_MINUTES
        )
    )
    request_count = (
        password_reset_repository
        .count_recent_requests(
            db,
            user.id,
            window_start
        )
    )

    if request_count >= config.PASSWORD_RESET_REQUEST_LIMIT:
        return {"message": FORGOT_PASSWORD_MESSAGE}

    password_reset_repository.invalidate_active_tokens(
        db,
        user.id,
        now
    )
    password_reset_repository.create_token(
        db,
        PasswordResetToken(
            user_id=user.id,
            otp_hash=otp_hash,
            expires_at=now + timedelta(
                minutes=(
                    config
                    .PASSWORD_RESET_OTP_EXPIRE_MINUTES
                )
            ),
            created_at=now,
            failed_attempts=0
        )
    )

    try:

        send_password_reset_otp(
            user.email,
            otp
        )
        db.commit()

    except EmailServiceError:

        db.rollback()
        logger.exception(
            "Password reset email delivery failed"
        )

    except SQLAlchemyError:

        db.rollback()
        raise

    return {"message": FORGOT_PASSWORD_MESSAGE}


def verify_reset_otp(
    db: Session,
    data: VerifyResetOTPRequest
) -> PasswordResetTokenResponse:

    now = _utc_now()
    user = user_repository.get_user_by_email_for_update(
        db,
        data.email
    )

    if not user or not user.is_active:
        verify_password(data.otp, _DUMMY_OTP_HASH)
        raise PasswordResetError(INVALID_OTP_MESSAGE)

    challenge = (
        password_reset_repository
        .get_current_token_for_update(
            db,
            user.id
        )
    )

    if not challenge:
        raise PasswordResetError(INVALID_OTP_MESSAGE)

    if challenge.verified_at is not None:
        raise PasswordResetError(INVALID_OTP_MESSAGE)

    if (
        _as_utc(challenge.expires_at) <= now
        or challenge.failed_attempts
        >= config.PASSWORD_RESET_MAX_ATTEMPTS
    ):
        challenge.invalidated_at = now
        db.commit()
        raise PasswordResetError(INVALID_OTP_MESSAGE)

    if not verify_password(
        data.otp,
        challenge.otp_hash
    ):
        challenge.failed_attempts += 1

        if (
            challenge.failed_attempts
            >= config.PASSWORD_RESET_MAX_ATTEMPTS
        ):
            challenge.invalidated_at = now

        db.commit()
        raise PasswordResetError(INVALID_OTP_MESSAGE)

    challenge.verified_at = now
    db.commit()

    return PasswordResetTokenResponse(
        reset_token=create_password_reset_token(
            user.id,
            challenge.id,
            user.token_version
        ),
        expires_in=(
            config.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES
            * 60
        )
    )


def reset_password(
    db: Session,
    data: ResetPasswordRequest
) -> dict:

    try:
        claims = decode_password_reset_token(
            data.reset_token
        )
    except (
        InvalidTokenError,
        RuntimeError
    ) as error:
        raise PasswordResetError(
            INVALID_RESET_MESSAGE
        ) from error

    new_password_hash = hash_password(
        data.new_password
    )
    now = _utc_now()
    user = user_repository.get_user_by_id_for_update(
        db,
        claims["user_id"]
    )
    challenge = (
        password_reset_repository
        .get_token_by_id_for_update(
            db,
            claims["challenge_id"]
        )
    )

    if (
        not user
        or not user.is_active
        or user.token_version
        != claims["token_version"]
        or not challenge
        or challenge.user_id != user.id
        or challenge.verified_at is None
        or challenge.consumed_at is not None
        or challenge.invalidated_at is not None
    ):
        raise PasswordResetError(INVALID_RESET_MESSAGE)

    try:

        user.hashed_password = new_password_hash
        user.token_version += 1
        challenge.consumed_at = now
        db.flush()
        password_reset_repository.invalidate_active_tokens(
            db,
            user.id,
            now
        )
        db.commit()

    except SQLAlchemyError:

        db.rollback()
        raise

    return {"message": RESET_SUCCESS_MESSAGE}
