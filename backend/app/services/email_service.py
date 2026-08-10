import logging
import smtplib
import ssl
from email.message import EmailMessage

from app.core import config


logger = logging.getLogger(__name__)


class EmailServiceError(RuntimeError):
    """Base error for the outbound email boundary."""


class EmailConfigurationError(EmailServiceError):
    """Raised when the selected email backend is unsafe or incomplete."""


class EmailDeliveryError(EmailServiceError):
    """Raised when the configured provider cannot deliver a message."""


def send_password_reset_otp(
    recipient: str,
    otp: str
) -> None:

    backend = config.EMAIL_BACKEND

    if backend == "console":

        if config.ENVIRONMENT.lower() == "production":
            raise EmailConfigurationError(
                "Console email is disabled in production"
            )

        logger.warning(
            "Development password reset code for %s: %s",
            recipient,
            otp
        )
        return

    if backend != "smtp":
        raise EmailConfigurationError(
            "EMAIL_BACKEND must be console or smtp"
        )

    if not config.SMTP_HOST or not config.SMTP_FROM_EMAIL:
        raise EmailConfigurationError(
            "SMTP configuration is incomplete"
        )

    if config.SMTP_USERNAME and not config.SMTP_PASSWORD:
        raise EmailConfigurationError(
            "SMTP authentication configuration is incomplete"
        )

    message = EmailMessage()
    message["Subject"] = "Your ATS password reset code"
    message["From"] = config.SMTP_FROM_EMAIL
    message["To"] = recipient
    message.set_content(
        "Your password reset verification code is "
        f"{otp}. It expires in "
        f"{config.PASSWORD_RESET_OTP_EXPIRE_MINUTES} "
        "minutes. If you did not request this, ignore "
        "this email."
    )

    try:

        with smtplib.SMTP(
            config.SMTP_HOST,
            config.SMTP_PORT,
            timeout=config.SMTP_TIMEOUT_SECONDS
        ) as client:

            client.ehlo()

            if config.SMTP_USE_TLS:
                client.starttls(
                    context=ssl.create_default_context()
                )
                client.ehlo()

            if config.SMTP_USERNAME:
                client.login(
                    config.SMTP_USERNAME,
                    config.SMTP_PASSWORD
                )

            client.send_message(message)

    except (
        OSError,
        smtplib.SMTPException
    ) as error:

        raise EmailDeliveryError(
            "Password reset email could not be delivered"
        ) from error
