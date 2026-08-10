from unittest.mock import MagicMock

import pytest

from app.services import email_service


def test_console_email_is_rejected_in_production(
    monkeypatch
):
    monkeypatch.setattr(
        email_service.config,
        "EMAIL_BACKEND",
        "console"
    )
    monkeypatch.setattr(
        email_service.config,
        "ENVIRONMENT",
        "production"
    )
    with pytest.raises(
        email_service.EmailConfigurationError
    ):
        email_service.send_password_reset_otp(
            "user@example.com",
            "123456"
        )


def test_smtp_backend_uses_tls_and_authentication(
    monkeypatch
):
    monkeypatch.setattr(
        email_service.config,
        "EMAIL_BACKEND",
        "smtp"
    )
    monkeypatch.setattr(
        email_service.config,
        "SMTP_HOST",
        "smtp.example.com"
    )
    monkeypatch.setattr(
        email_service.config,
        "SMTP_FROM_EMAIL",
        "no-reply@example.com"
    )
    monkeypatch.setattr(
        email_service.config,
        "SMTP_USERNAME",
        "smtp-user"
    )
    monkeypatch.setattr(
        email_service.config,
        "SMTP_PASSWORD",
        "test-only-password"
    )
    monkeypatch.setattr(
        email_service.config,
        "SMTP_USE_TLS",
        True
    )
    client = MagicMock()
    context_manager = MagicMock()
    context_manager.__enter__.return_value = client
    smtp = MagicMock(return_value=context_manager)
    monkeypatch.setattr(email_service.smtplib, "SMTP", smtp)

    email_service.send_password_reset_otp(
        "user@example.com",
        "123456"
    )

    client.starttls.assert_called_once()
    client.login.assert_called_once_with(
        "smtp-user",
        "test-only-password"
    )
    client.send_message.assert_called_once()


def test_smtp_provider_errors_are_typed(monkeypatch):
    monkeypatch.setattr(
        email_service.config,
        "EMAIL_BACKEND",
        "smtp"
    )
    monkeypatch.setattr(
        email_service.config,
        "SMTP_HOST",
        "smtp.example.com"
    )
    monkeypatch.setattr(
        email_service.config,
        "SMTP_FROM_EMAIL",
        "no-reply@example.com"
    )
    monkeypatch.setattr(
        email_service.config,
        "SMTP_USERNAME",
        None
    )
    smtp = MagicMock(
        side_effect=email_service.smtplib.SMTPException(
            "provider detail"
        )
    )
    monkeypatch.setattr(email_service.smtplib, "SMTP", smtp)

    with pytest.raises(email_service.EmailDeliveryError):
        email_service.send_password_reset_otp(
            "user@example.com",
            "123456"
        )
