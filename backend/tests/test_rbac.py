from io import BytesIO
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core import security
from app.core.security import (
    create_access_token,
    hash_password
)
from app.database.database import (
    Base,
    get_db
)
from app.database.models import User
from app.services.gcs_storage_service import StoredGCSObject
from main import app


pytestmark = pytest.mark.real_auth


TEST_JWT_SECRET = (
    "test-only-rbac-secret-that-is-long-enough-"
    "for-role-authorization-tests"
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
def isolated_rbac_database(monkeypatch):

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
def role_headers():

    with TestingSessionLocal() as db:

        admin = User(
            email="admin@example.com",
            full_name="Admin User",
            hashed_password=hash_password(
                "AdminPassword123!"
            ),
            role="admin",
            is_active=True
        )

        recruiter = User(
            email="recruiter@example.com",
            full_name="Recruiter User",
            hashed_password=hash_password(
                "RecruiterPassword123!"
            ),
            role="recruiter",
            is_active=True
        )

        db.add_all([
            admin,
            recruiter
        ])
        db.commit()
        db.refresh(admin)
        db.refresh(recruiter)

        admin_token = create_access_token(
            admin.id
        )

        recruiter_token = create_access_token(
            recruiter.id
        )

    return {
        "admin": {
            "Authorization": (
                f"Bearer {admin_token}"
            )
        },
        "recruiter": {
            "Authorization": (
                f"Bearer {recruiter_token}"
            )
        }
    }


@pytest.mark.parametrize(
    ("method", "path", "payload"),
    [
        ("get", "/candidates/", None),
        ("get", "/candidates/999", None),
        ("get", "/candidates/search", None),
        ("get", "/candidates/stats", None),
        ("get", "/candidates/ranking", None),
        ("get", "/dashboard/summary", None),
        ("get", "/dashboard/top-candidates", None),
        ("get", "/dashboard/score-distribution", None),
        ("get", "/dashboard/level-distribution", None),
        ("get", "/dashboard/recent-candidates", None),
        ("get", "/export/csv", None),
        ("delete", "/candidates/999", None),
        (
            "put",
            "/candidates/999",
            {
                "candidate_level": "Senior"
            }
        ),
        (
            "post",
            "/search/",
            {
                "query": "Python"
            }
        ),
        (
            "post",
            "/assistant/",
            {
                "question": "Who knows Python?"
            }
        ),
        (
            "post",
            "/recommend/",
            {
                "question": "Python engineer"
            }
        ),
        ("post", "/upload/", None)
    ]
)
def test_protected_endpoints_require_authentication(
    client,
    method,
    path,
    payload
):

    response = client.request(
        method.upper(),
        path,
        json=payload
    )

    assert response.status_code == 401


def test_invalid_token_returns_401(client):

    response = client.get(
        "/candidates/",
        headers={
            "Authorization": "Bearer invalid-token"
        }
    )

    assert response.status_code == 401


@pytest.mark.parametrize(
    ("method", "path", "payload"),
    [
        ("delete", "/candidates/999", None),
        (
            "put",
            "/candidates/999",
            {
                "candidate_level": "Senior"
            }
        ),
        ("get", "/export/csv", None)
    ]
)
def test_recruiter_cannot_access_admin_endpoints(
    client,
    role_headers,
    method,
    path,
    payload
):

    response = client.request(
        method.upper(),
        path,
        json=payload,
        headers=role_headers["recruiter"]
    )

    assert response.status_code == 403


def test_admin_can_access_admin_endpoints(
    client,
    role_headers
):

    export_response = client.get(
        "/export/csv",
        headers=role_headers["admin"]
    )

    update_response = client.put(
        "/candidates/999",
        json={
            "candidate_level": "Senior"
        },
        headers=role_headers["admin"]
    )

    delete_response = client.delete(
        "/candidates/999",
        headers=role_headers["admin"]
    )

    assert export_response.status_code == 200
    assert update_response.status_code == 404
    assert delete_response.status_code == 404


def test_recruiter_can_access_authenticated_reads(
    client,
    role_headers
):

    headers = role_headers["recruiter"]

    assert client.get(
        "/candidates/",
        headers=headers
    ).status_code == 200

    assert client.get(
        "/candidates/999",
        headers=headers
    ).status_code == 404

    dashboard_paths = [
        "/dashboard/summary",
        "/dashboard/top-candidates",
        "/dashboard/score-distribution",
        "/dashboard/level-distribution",
        "/dashboard/recent-candidates"
    ]

    for path in dashboard_paths:

        assert client.get(
            path,
            headers=headers
        ).status_code == 200


def test_recruiter_can_access_staff_endpoints(
    client,
    role_headers
):

    headers = role_headers["recruiter"]

    candidate_search_response = client.get(
        "/candidates/search",
        headers=headers
    )

    with patch(
        "app.api.search.semantic_search",
        return_value=[]
    ), patch(
        "app.api.assistant.ask_assistant",
        return_value="Candidate answer"
    ), patch(
        "app.api.recommend.ask_recommendation",
        return_value={
            "candidate_id": "1",
            "candidate_name": "Candidate One",
            "match_score": 90,
            "strengths": ["Python"],
            "relevant_experience": ["Backend"],
            "reason": "Strong match"
        }
    ):

        semantic_response = client.post(
            "/search/",
            json={
                "query": "Python"
            },
            headers=headers
        )

        assistant_response = client.post(
            "/assistant/",
            json={
                "question": "Who knows Python?"
            },
            headers=headers
        )

        recommend_response = client.post(
            "/recommend/",
            json={
                "question": "Python engineer"
            },
            headers=headers
        )

    with patch(
        "app.api.upload.extract_text_from_pdf",
        return_value="Resume text"
    ), patch(
        "app.api.upload.extract_resume_data",
        return_value={
            "name": "Candidate One"
        }
    ), patch(
        "app.api.upload.summarize_document",
        return_value="Summary"
    ), patch(
        "app.api.upload.analyze_resume",
        return_value={
            "candidate_level": "Junior",
            "skill_score": 80,
            "rule_score": 80,
            "ai_score": 80,
            "ai_status": "success",
            "score_breakdown": {}
        }
    ), patch(
        "app.api.upload.index_resume"
    ), patch(
        "app.api.upload.store_resume",
        return_value=StoredGCSObject(
            bucket="test-resume-bucket",
            key="resumes/test/recruiter-upload.pdf",
            etag="test-etag"
        )
    ) as mock_store:

        upload_response = client.post(
            "/upload/",
            files={
                "file": (
                    "resume.pdf",
                    BytesIO(
                        b"%PDF-1.4 test"
                    ),
                    "application/pdf"
                )
            },
            headers=headers
        )

    assert candidate_search_response.status_code == 200
    assert semantic_response.status_code == 200
    assert assistant_response.status_code == 200
    assert recommend_response.status_code == 200
    assert upload_response.status_code == 200
    mock_store.assert_called_once()
