from datetime import (
    datetime,
    timedelta,
    timezone
)
from unittest.mock import Mock

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
from app.database.models import (
    Job,
    User
)
from app.services import job_service
from main import app


pytestmark = pytest.mark.real_auth


TEST_JWT_SECRET = (
    "test-only-jobs-secret-that-is-long-enough-"
    "for-job-authorization-tests"
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
def isolated_jobs_database(monkeypatch):

    Base.metadata.create_all(bind=engine)
    app.dependency_overrides[get_db] = (
        override_get_db
    )
    monkeypatch.setattr(
        security,
        "JWT_SECRET_KEY",
        TEST_JWT_SECRET
    )
    monkeypatch.setattr(
        job_service,
        "extract_job_requirements",
        lambda description: {
            "required_skills": ["Python"],
            "preferred_skills": [],
            "experience_requirements": [],
            "responsibilities": [
                "Build reliable APIs"
            ]
        }
    )
    monkeypatch.setattr(
        job_service,
        "create_embedding",
        lambda description: [0.25] * 384
    )

    yield

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():

    return TestClient(app)


@pytest.fixture
def role_headers():

    headers = {}

    with TestingSessionLocal() as db:
        for role in ("admin", "recruiter"):
            user = User(
                email=f"{role}@example.com",
                full_name=f"{role.title()} User",
                hashed_password=hash_password(
                    "StrongPassword123!"
                ),
                role=role,
                is_active=True
            )
            db.add(user)
            db.commit()
            db.refresh(user)

            headers[role] = {
                "Authorization": (
                    "Bearer "
                    f"{create_access_token(user.id)}"
                )
            }

    return headers


def test_recruiter_creates_persisted_job_with_ownership(
    client,
    role_headers
):

    response = client.post(
        "/jobs",
        json={
            "title": "  Senior Backend Engineer  ",
            "description": "  Build reliable APIs.  "
        },
        headers=role_headers["recruiter"]
    )

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Senior Backend Engineer"
    assert data["description"] == "Build reliable APIs."
    assert data["extracted_requirements"] == {
        "required_skills": ["Python"],
        "preferred_skills": [],
        "experience_requirements": [],
        "responsibilities": [
            "Build reliable APIs"
        ]
    }
    assert "embedding" not in data

    with TestingSessionLocal() as db:
        job = db.get(Job, data["id"])
        recruiter = (
            db.query(User)
            .filter(User.role == "recruiter")
            .one()
        )

        assert job is not None
        assert job.title == "Senior Backend Engineer"
        assert job.description == "Build reliable APIs."
        assert job.extracted_requirements == (
            data["extracted_requirements"]
        )
        assert len(job.embedding) == 384
        assert job.embedding == [0.25] * 384
        assert job.created_by == recruiter.id
        assert data["created_by"] == recruiter.id


def test_admin_can_create_job(
    client,
    role_headers
):

    response = client.post(
        "/jobs",
        json={
            "title": "Engineering Manager",
            "description": "Lead the platform team."
        },
        headers=role_headers["admin"]
    )

    assert response.status_code == 201


@pytest.mark.parametrize(
    "payload",
    [
        {
            "title": "",
            "description": "Valid description"
        },
        {
            "title": "   ",
            "description": "Valid description"
        },
        {
            "title": "Valid title",
            "description": ""
        },
        {
            "title": "Valid title",
            "description": "   "
        },
        {
            "title": "x" * 256,
            "description": "Valid description"
        }
    ]
)
def test_create_job_validates_title_and_description(
    client,
    role_headers,
    payload
):

    response = client.post(
        "/jobs",
        json=payload,
        headers=role_headers["recruiter"]
    )

    assert response.status_code == 422


def test_job_endpoints_require_authentication(client):

    create_response = client.post(
        "/jobs",
        json={
            "title": "Backend Engineer",
            "description": "Build APIs."
        }
    )
    list_response = client.get("/jobs")

    assert create_response.status_code == 401
    assert list_response.status_code == 401


def test_extraction_failure_does_not_persist_job(
    client,
    role_headers,
    monkeypatch
):

    embedding_mock = Mock(
        return_value=[0.25] * 384
    )
    monkeypatch.setattr(
        job_service,
        "extract_job_requirements",
        Mock(
            side_effect=RuntimeError(
                "extraction unavailable"
            )
        )
    )
    monkeypatch.setattr(
        job_service,
        "create_embedding",
        embedding_mock
    )

    response = client.post(
        "/jobs",
        json={
            "title": "Backend Engineer",
            "description": "Build APIs."
        },
        headers=role_headers["recruiter"]
    )

    assert response.status_code == 503
    assert response.json() == {
        "detail": (
            "Job processing service is unavailable"
        )
    }
    embedding_mock.assert_not_called()

    with TestingSessionLocal() as db:
        assert db.query(Job).count() == 0


def test_embedding_failure_does_not_persist_job(
    client,
    role_headers,
    monkeypatch
):

    monkeypatch.setattr(
        job_service,
        "create_embedding",
        Mock(
            side_effect=RuntimeError(
                "embedding unavailable"
            )
        )
    )

    response = client.post(
        "/jobs",
        json={
            "title": "Backend Engineer",
            "description": "Build APIs."
        },
        headers=role_headers["recruiter"]
    )

    assert response.status_code == 503

    with TestingSessionLocal() as db:
        assert db.query(Job).count() == 0


def test_get_jobs_returns_deterministic_newest_first_order(
    client,
    role_headers
):

    now = datetime.now(timezone.utc)

    with TestingSessionLocal() as db:
        recruiter = (
            db.query(User)
            .filter(User.role == "recruiter")
            .one()
        )
        jobs = [
            Job(
                title="Older job",
                description="Older description",
                created_by=recruiter.id,
                created_at=now - timedelta(days=1)
            ),
            Job(
                title="Newer job one",
                description="Newer description one",
                created_by=recruiter.id,
                created_at=now
            ),
            Job(
                title="Newer job two",
                description="Newer description two",
                created_by=recruiter.id,
                created_at=now
            )
        ]
        db.add_all(jobs)
        db.commit()
        expected_ids = [
            jobs[2].id,
            jobs[1].id,
            jobs[0].id
        ]

    response = client.get(
        "/jobs",
        headers=role_headers["recruiter"]
    )

    assert response.status_code == 200
    assert [
        job["id"]
        for job in response.json()
    ] == expected_ids
