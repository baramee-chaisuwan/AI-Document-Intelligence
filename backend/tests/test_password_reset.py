from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.dependencies import get_db
from app.core import security
from app.database.database import Base
from app.database.models import PasswordResetToken
from app.services import password_reset_service
from app.services.email_service import EmailDeliveryError
from main import app


pytestmark = pytest.mark.real_auth

TEST_JWT_SECRET = (
    "test-only-jwt-secret-that-is-long-enough-"
    "for-password-reset-tests"
)
EMAIL = "reset.user@example.com"
OLD_PASSWORD = "OldPassword123!"
NEW_PASSWORD = "NewPassword456!"

engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    bind=engine
)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def isolated_database(monkeypatch):
    Base.metadata.create_all(bind=engine)
    app.dependency_overrides[get_db] = override_get_db
    monkeypatch.setattr(
        security,
        "JWT_SECRET_KEY",
        TEST_JWT_SECRET
    )
    yield
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def sent_codes(monkeypatch):
    messages = []

    def capture(recipient, otp):
        messages.append((recipient, otp))

    monkeypatch.setattr(
        password_reset_service,
        "send_password_reset_otp",
        capture
    )
    return messages


def register(client):
    response = client.post(
        "/auth/register",
        json={
            "email": EMAIL,
            "full_name": "Reset User",
            "password": OLD_PASSWORD
        }
    )
    assert response.status_code == 201


def request_code(client, sent_codes):
    response = client.post(
        "/auth/forgot-password",
        json={"email": EMAIL}
    )
    assert response.status_code == 200
    return sent_codes[-1][1]


def verify_code(client, otp):
    return client.post(
        "/auth/verify-reset-otp",
        json={"email": EMAIL, "otp": otp}
    )


def complete_verification(client, sent_codes):
    otp = request_code(client, sent_codes)
    response = verify_code(client, otp)
    assert response.status_code == 200
    return response.json()["reset_token"]


def test_forgot_password_is_enumeration_safe(
    client,
    sent_codes
):
    register(client)
    existing = client.post(
        "/auth/forgot-password",
        json={"email": EMAIL}
    )
    missing = client.post(
        "/auth/forgot-password",
        json={"email": "missing@example.com"}
    )
    assert existing.status_code == missing.status_code == 200
    assert existing.json() == missing.json()
    assert len(sent_codes) == 1


def test_otp_is_six_digits_and_only_hash_is_stored(
    client,
    sent_codes
):
    register(client)
    otp = request_code(client, sent_codes)
    assert len(otp) == 6 and otp.isdigit()
    with TestingSessionLocal() as db:
        challenge = db.query(PasswordResetToken).one()
        assert challenge.otp_hash != otp
        assert security.verify_password(
            otp,
            challenge.otp_hash
        )


def test_valid_otp_issues_distinct_reset_token(
    client,
    sent_codes
):
    register(client)
    reset_token = complete_verification(
        client,
        sent_codes
    )
    claims = security.decode_password_reset_token(
        reset_token
    )
    assert claims["type"] == "password_reset"
    assert claims["challenge_id"] > 0
    assert claims["exp"] - claims["iat"] == 600

    assert client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {reset_token}"}
    ).status_code == 401


def test_invalid_otp_increments_and_enforces_limit(
    client,
    sent_codes,
    monkeypatch
):
    register(client)
    request_code(client, sent_codes)
    monkeypatch.setattr(
        password_reset_service.config,
        "PASSWORD_RESET_MAX_ATTEMPTS",
        2
    )
    for _ in range(2):
        assert verify_code(client, "999999").status_code == 400
    with TestingSessionLocal() as db:
        challenge = db.query(PasswordResetToken).one()
        assert challenge.failed_attempts == 2
        assert challenge.invalidated_at is not None
    assert verify_code(client, sent_codes[-1][1]).status_code == 400


def test_expired_otp_is_rejected(client, sent_codes):
    register(client)
    otp = request_code(client, sent_codes)
    with TestingSessionLocal() as db:
        challenge = db.query(PasswordResetToken).one()
        challenge.expires_at = (
            datetime.now(timezone.utc)
            - timedelta(seconds=1)
        )
        db.commit()
    assert verify_code(client, otp).status_code == 400


def test_verified_otp_cannot_mint_another_reset_token(
    client,
    sent_codes
):
    register(client)
    otp = request_code(client, sent_codes)
    first_response = verify_code(client, otp)
    assert first_response.status_code == 200
    assert first_response.json()["reset_token"]
    assert verify_code(client, otp).status_code == 400


def test_reset_jwt_remains_valid_after_verified_otp_expires(
    client,
    sent_codes,
    monkeypatch
):
    register(client)
    otp = request_code(client, sent_codes)
    verification_time = datetime.now(timezone.utc)

    with TestingSessionLocal() as db:
        challenge = db.query(PasswordResetToken).one()
        challenge.expires_at = (
            verification_time
            + timedelta(seconds=5)
        )
        db.commit()

    verification = verify_code(client, otp)
    assert verification.status_code == 200
    reset_token = verification.json()["reset_token"]

    monkeypatch.setattr(
        password_reset_service,
        "_utc_now",
        lambda: (
            verification_time
            + timedelta(seconds=6)
        )
    )

    response = client.post(
        "/auth/reset-password",
        json={
            "reset_token": reset_token,
            "new_password": NEW_PASSWORD,
            "confirm_password": NEW_PASSWORD
        }
    )
    assert response.status_code == 200


def test_newer_otp_invalidates_previous_challenge(
    client,
    sent_codes
):
    register(client)
    old_otp = request_code(client, sent_codes)
    new_otp = request_code(client, sent_codes)
    assert verify_code(client, old_otp).status_code == 400
    assert verify_code(client, new_otp).status_code == 200


def test_access_token_cannot_authorize_password_reset(
    client
):
    register(client)
    access_token = client.post(
        "/auth/login",
        json={"email": EMAIL, "password": OLD_PASSWORD}
    ).json()["access_token"]
    response = client.post(
        "/auth/reset-password",
        json={
            "reset_token": access_token,
            "new_password": NEW_PASSWORD,
            "confirm_password": NEW_PASSWORD
        }
    )
    assert response.status_code == 400


def test_expired_reset_authorization_is_rejected(
    client,
    sent_codes,
    monkeypatch
):
    register(client)
    reset_token = complete_verification(client, sent_codes)
    real_datetime = datetime

    class FutureDatetime(real_datetime):
        @classmethod
        def now(cls, tz=None):
            value = real_datetime.now(timezone.utc)
            return value + timedelta(minutes=11)

    monkeypatch.setattr(
        security,
        "datetime",
        FutureDatetime
    )
    response = client.post(
        "/auth/reset-password",
        json={
            "reset_token": reset_token,
            "new_password": NEW_PASSWORD,
            "confirm_password": NEW_PASSWORD
        }
    )
    assert response.status_code == 400


def test_password_reset_changes_password_invalidates_access_and_replay(
    client,
    sent_codes
):
    register(client)
    old_access_token = client.post(
        "/auth/login",
        json={"email": EMAIL, "password": OLD_PASSWORD}
    ).json()["access_token"]
    reset_token = complete_verification(client, sent_codes)
    payload = {
        "reset_token": reset_token,
        "new_password": NEW_PASSWORD,
        "confirm_password": NEW_PASSWORD
    }
    assert client.post(
        "/auth/reset-password",
        json=payload
    ).status_code == 200
    assert client.post(
        "/auth/login",
        json={"email": EMAIL, "password": OLD_PASSWORD}
    ).status_code == 401
    assert client.post(
        "/auth/login",
        json={"email": EMAIL, "password": NEW_PASSWORD}
    ).status_code == 200
    assert client.get(
        "/auth/me",
        headers={
            "Authorization": f"Bearer {old_access_token}"
        }
    ).status_code == 401
    assert client.post(
        "/auth/reset-password",
        json=payload
    ).status_code == 400


def test_email_failure_is_hidden_and_challenge_rolled_back(
    client,
    monkeypatch
):
    register(client)

    def fail_delivery(recipient, otp):
        raise EmailDeliveryError("provider detail")

    monkeypatch.setattr(
        password_reset_service,
        "send_password_reset_otp",
        fail_delivery
    )
    response = client.post(
        "/auth/forgot-password",
        json={"email": EMAIL}
    )
    assert response.status_code == 200
    assert "provider" not in response.text.lower()
    with TestingSessionLocal() as db:
        assert db.query(PasswordResetToken).count() == 0


def test_forgot_password_database_rate_limit(
    client,
    sent_codes,
    monkeypatch
):
    register(client)
    monkeypatch.setattr(
        password_reset_service.config,
        "PASSWORD_RESET_REQUEST_LIMIT",
        2
    )
    for _ in range(3):
        response = client.post(
            "/auth/forgot-password",
            json={"email": EMAIL}
        )
        assert response.status_code == 200
    assert len(sent_codes) == 2
    with TestingSessionLocal() as db:
        assert db.query(PasswordResetToken).count() == 2
