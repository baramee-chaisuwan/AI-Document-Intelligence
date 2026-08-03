import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core import security
from app.api.dependencies import (
    get_current_admin_user
)
from app.database.database import (
    Base,
    get_db
)
from app.database.models import User
from main import app


pytestmark = pytest.mark.real_auth


TEST_JWT_SECRET = (
    "test-only-jwt-secret-that-is-long-enough-"
    "for-authentication-tests"
)


engine = create_engine(
    "sqlite://",
    connect_args={
        "check_same_thread": False
    },
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
def isolated_auth_database(monkeypatch):

    Base.metadata.create_all(
        bind=engine
    )

    app.dependency_overrides[
        get_db
    ] = override_get_db

    monkeypatch.setattr(
        security,
        "JWT_SECRET_KEY",
        TEST_JWT_SECRET
    )

    yield

    app.dependency_overrides.clear()

    Base.metadata.drop_all(
        bind=engine
    )


@pytest.fixture
def client():

    return TestClient(app)


@pytest.fixture
def registered_user(client):

    payload = {
        "email": "recruiter@example.com",
        "full_name": "Recruiter One",
        "password": "StrongPassword123!"
    }

    response = client.post(
        "/auth/register",
        json=payload
    )

    assert response.status_code == 201

    return payload


def test_register_user(client):

    response = client.post(
        "/auth/register",
        json={
            "email": "New.User@Example.com",
            "full_name": "  New User  ",
            "password": "StrongPassword123!"
        }
    )

    assert response.status_code == 201

    data = response.json()

    assert data["email"] == "new.user@example.com"
    assert data["full_name"] == "New User"
    assert data["role"] == "recruiter"
    assert data["is_active"] is True
    assert "hashed_password" not in data
    assert "password" not in data


def test_login_returns_access_token(
    client,
    registered_user
):

    response = client.post(
        "/auth/login",
        json={
            "email": registered_user["email"],
            "password": registered_user["password"]
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["token_type"] == "bearer"
    assert data["access_token"]
    assert data["expires_in"] == 1800


def test_login_rejects_invalid_credentials(
    client,
    registered_user
):

    response = client.post(
        "/auth/login",
        json={
            "email": registered_user["email"],
            "password": "IncorrectPassword!"
        }
    )

    assert response.status_code == 401
    assert response.json() == {
        "detail": "Invalid email or password"
    }
    assert (
        response.headers["www-authenticate"]
        == "Bearer"
    )


def test_register_rejects_duplicate_email(
    client,
    registered_user
):

    response = client.post(
        "/auth/register",
        json={
            "email": "RECRUITER@example.com",
            "full_name": "Another Recruiter",
            "password": "AnotherPassword123!"
        }
    )

    assert response.status_code == 409
    assert response.json() == {
        "detail": (
            "A user with this email already exists"
        )
    }


def test_auth_me_returns_current_user(
    client,
    registered_user
):

    login_response = client.post(
        "/auth/login",
        json={
            "email": registered_user["email"],
            "password": registered_user["password"]
        }
    )

    token = login_response.json()[
        "access_token"
    ]

    response = client.get(
        "/auth/me",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["email"] == registered_user["email"]
    assert data["full_name"] == "Recruiter One"
    assert data["role"] == "recruiter"
    assert data["is_active"] is True


def test_auth_me_requires_bearer_token(client):

    response = client.get(
        "/auth/me"
    )

    assert response.status_code == 401
    assert (
        response.headers["www-authenticate"]
        == "Bearer"
    )


def test_admin_dependency_allows_admin():

    admin = User(
        role="admin"
    )

    assert (
        get_current_admin_user(admin)
        is admin
    )


def test_admin_dependency_rejects_recruiter():

    recruiter = User(
        role="recruiter"
    )

    with pytest.raises(
        HTTPException
    ) as error:

        get_current_admin_user(
            recruiter
        )

    assert error.value.status_code == 403
