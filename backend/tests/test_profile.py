from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.dependencies import get_current_user
from app.core import security
from app.database.database import Base, get_db
from app.database.models import User
from app.services import gcs_storage_service, profile_service
from main import app


TEST_SECRET = "profile-test-jwt-secret-that-is-long-enough"
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
def isolated_profile_database(monkeypatch):
    Base.metadata.create_all(bind=engine)
    app.dependency_overrides[get_db] = override_get_db
    monkeypatch.setattr(security, "JWT_SECRET_KEY", TEST_SECRET)
    yield
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def authenticated_user(client):
    password = "StrongPassword123!"
    with TestingSessionLocal() as db:
        user = User(
            email="profile@example.com",
            full_name="Profile User",
            hashed_password=security.hash_password(password),
            role="recruiter",
            is_active=True,
            token_version=0
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        user_id = user.id
        db.expunge(user)
    token = security.create_access_token(user_id, 0)
    app.dependency_overrides[get_current_user] = lambda: user
    return {
        "id": user_id,
        "password": password,
        "headers": {
            "Authorization": f"Bearer {token}"
        },
    }


def test_get_and_update_own_profile(client, authenticated_user):
    before = client.get(
        "/auth/me",
        headers=authenticated_user["headers"]
    )
    updated = client.patch(
        "/auth/me",
        headers=authenticated_user["headers"],
        json={"full_name": "  Updated Recruiter  "}
    )

    assert before.status_code == 200
    assert before.json()["has_profile_image"] is False
    assert "profile_image_key" not in before.json()
    assert updated.status_code == 200
    assert updated.json()["full_name"] == "Updated Recruiter"
    assert updated.json()["email"] == "profile@example.com"


@pytest.mark.parametrize("full_name", ["", "   ", "x" * 256])
def test_profile_name_validation(client, authenticated_user, full_name):
    response = client.patch(
        "/auth/me",
        headers=authenticated_user["headers"],
        json={"full_name": full_name}
    )
    assert response.status_code == 422


def test_profile_update_rejects_user_id_override(
    client,
    authenticated_user
):
    response = client.patch(
        "/auth/me",
        headers=authenticated_user["headers"],
        json={
            "full_name": "Attempted Override",
            "user_id": authenticated_user["id"] + 1,
        }
    )
    assert response.status_code == 422


def test_profile_endpoints_require_authentication(client):
    app.dependency_overrides.pop(get_current_user, None)
    assert client.patch(
        "/auth/me",
        json={"full_name": "Other"}
    ).status_code == 401
    assert client.post(
        "/auth/change-password",
        json={
            "current_password": "old",
            "new_password": "NewPassword123!",
            "confirm_password": "NewPassword123!",
        }
    ).status_code == 401


def test_profile_photo_upload_replacement_and_deletion(
    client,
    authenticated_user,
    monkeypatch
):
    first = gcs_storage_service.StoredProfileImage(
        bucket="test",
        key=(
            f"resumes/profile-images/"
            f"{authenticated_user['id']}/first.png"
        ),
        content_type="image/png"
    )
    second = gcs_storage_service.StoredProfileImage(
        bucket="test",
        key=(
            f"resumes/profile-images/"
            f"{authenticated_user['id']}/second.webp"
        ),
        content_type="image/webp"
    )
    upload = Mock(side_effect=[first, second])
    delete = Mock()
    monkeypatch.setattr(
        gcs_storage_service,
        "put_profile_image",
        upload
    )
    monkeypatch.setattr(
        gcs_storage_service,
        "delete_profile_image",
        delete
    )

    first_response = client.post(
        "/auth/me/profile-photo",
        headers=authenticated_user["headers"],
        files={"photo": ("photo.png", b"\x89PNG\r\n\x1a\nimage", "image/png")}
    )
    second_response = client.post(
        "/auth/me/profile-photo",
        headers=authenticated_user["headers"],
        files={"photo": ("photo.webp", b"RIFFxxxxWEBPimage", "image/webp")}
    )
    delete_response = client.delete(
        "/auth/me/profile-photo",
        headers=authenticated_user["headers"]
    )

    assert first_response.status_code == 200
    assert first_response.json()["has_profile_image"] is True
    assert second_response.status_code == 200
    assert delete_response.status_code == 200
    assert delete_response.json()["has_profile_image"] is False
    assert delete.call_args_list == [
        ((first.key, authenticated_user["id"]),),
        ((second.key, authenticated_user["id"]),),
    ]


@pytest.mark.parametrize(
    ("filename", "content", "content_type"),
    [
        ("photo.gif", b"GIF89a", "image/gif"),
        ("fake.png", b"not-a-png", "image/png"),
    ]
)
def test_profile_photo_rejects_invalid_content(
    client,
    authenticated_user,
    filename,
    content,
    content_type
):
    response = client.post(
        "/auth/me/profile-photo",
        headers=authenticated_user["headers"],
        files={"photo": (filename, content, content_type)}
    )
    assert response.status_code == 400


def test_profile_photo_rejects_oversized_content(
    client,
    authenticated_user,
    monkeypatch
):
    monkeypatch.setattr(
        gcs_storage_service,
        "_MAX_PROFILE_IMAGE_BYTES",
        8
    )
    response = client.post(
        "/auth/me/profile-photo",
        headers=authenticated_user["headers"],
        files={
            "photo": (
                "large.jpg",
                b"\xff\xd8\xffoversized",
                "image/jpeg"
            )
        }
    )
    assert response.status_code == 400


def test_storage_failure_preserves_existing_profile_key(
    client,
    authenticated_user,
    monkeypatch
):
    with TestingSessionLocal() as db:
        user = db.get(User, authenticated_user["id"])
        user.profile_image_key = (
            f"resumes/profile-images/{user.id}/existing.png"
        )
        db.commit()

    monkeypatch.setattr(
        gcs_storage_service,
        "put_profile_image",
        Mock(side_effect=gcs_storage_service.GCSOperationError("failed"))
    )

    response = client.post(
        "/auth/me/profile-photo",
        headers=authenticated_user["headers"],
        files={"photo": ("new.png", b"\x89PNG\r\n\x1a\nimage", "image/png")}
    )

    assert response.status_code == 503
    with TestingSessionLocal() as db:
        assert db.get(User, authenticated_user["id"]).profile_image_key.endswith(
            "existing.png"
        )


def test_change_password_invalidates_existing_token(
    client,
    authenticated_user
):
    response = client.post(
        "/auth/change-password",
        headers=authenticated_user["headers"],
        json={
            "current_password": authenticated_user["password"],
            "new_password": "ReplacementPassword123!",
            "confirm_password": "ReplacementPassword123!",
        }
    )

    assert response.status_code == 200
    with TestingSessionLocal() as db:
        stored_user = db.get(User, authenticated_user["id"])
        assert stored_user.token_version == 1
    assert client.post("/auth/login", json={
        "email": "profile@example.com",
        "password": "ReplacementPassword123!",
    }).status_code == 200


def test_change_password_rejects_wrong_current_password(
    client,
    authenticated_user
):
    response = client.post(
        "/auth/change-password",
        headers=authenticated_user["headers"],
        json={
            "current_password": "WrongPassword123!",
            "new_password": "ReplacementPassword123!",
            "confirm_password": "ReplacementPassword123!",
        }
    )
    assert response.status_code == 400
    assert response.json() == {
        "detail": "Current password is incorrect"
    }


def test_password_change_validation(client, authenticated_user):
    response = client.post(
        "/auth/change-password",
        headers=authenticated_user["headers"],
        json={
            "current_password": authenticated_user["password"],
            "new_password": "short",
            "confirm_password": "different",
        }
    )
    assert response.status_code == 422


def test_profile_storage_owner_validation(monkeypatch):
    client = Mock()
    monkeypatch.setattr(gcs_storage_service, "_storage_client", client)
    monkeypatch.setattr(
        gcs_storage_service.config,
        "GCS_BUCKET_NAME",
        "ats-profile-test"
    )
    monkeypatch.setattr(
        gcs_storage_service.config,
        "GCS_KEY_PREFIX",
        "resumes"
    )

    with pytest.raises(gcs_storage_service.GCSValidationError):
        gcs_storage_service.delete_profile_image(
            "resumes/profile-images/2/photo.png",
            user_id=1
        )
    client.bucket.assert_not_called()


def test_profile_storage_upload_is_private_and_user_scoped(monkeypatch):
    client = Mock()
    bucket = Mock()
    blob = Mock()
    client.bucket.return_value = bucket
    bucket.blob.return_value = blob
    monkeypatch.setattr(gcs_storage_service, "_storage_client", client)
    monkeypatch.setattr(
        gcs_storage_service.config,
        "GCS_BUCKET_NAME",
        "ats-profile-test"
    )
    monkeypatch.setattr(
        gcs_storage_service.config,
        "GCS_KEY_PREFIX",
        "resumes"
    )

    stored = gcs_storage_service.put_profile_image(
        user_id=7,
        content=b"\x89PNG\r\n\x1a\nimage",
        content_type="image/png"
    )

    assert stored.key.startswith("resumes/profile-images/7/")
    assert stored.key.endswith(".png")
    assert stored.content_type == "image/png"
    blob.upload_from_string.assert_called_once_with(
        b"\x89PNG\r\n\x1a\nimage",
        content_type="image/png",
        if_generation_match=0
    )
    assert blob.metadata == {"owner-user-id": "7"}
    blob.make_public.assert_not_called()
