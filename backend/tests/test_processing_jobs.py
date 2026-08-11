import importlib.util
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    String,
    create_engine
)
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core import security
from app.core.exceptions import ConflictError
from app.core.security import (
    create_access_token,
    hash_password
)
from app.database.database import Base, get_db
from app.database.models import (
    ResumeProcessingJob,
    User
)
from app.models.processing_job_status import (
    ProcessingJobStatus
)
from app.repositories import processing_job_repository
from app.services import processing_job_service
from main import app


pytestmark = pytest.mark.real_auth


TEST_JWT_SECRET = (
    "test-only-processing-jobs-secret-that-is-"
    "long-enough-for-authentication-tests"
)

MIGRATION_PATH = (
    Path(__file__).parents[1]
    / "alembic"
    / "versions"
    / "f4a6c8e2d190_add_resume_processing_jobs.py"
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
def isolated_processing_job_database(monkeypatch):

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
def auth_headers():

    with TestingSessionLocal() as db:
        user = User(
            email="processing-status@example.com",
            full_name="Processing Status User",
            hashed_password=hash_password(
                "StrongPassword123!"
            ),
            role="recruiter",
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        token = create_access_token(user.id)

    return {
        "Authorization": f"Bearer {token}"
    }


def load_migration():

    spec = importlib.util.spec_from_file_location(
        "resume_processing_jobs_migration",
        MIGRATION_PATH
    )
    assert spec is not None
    assert spec.loader is not None
    migration = importlib.util.module_from_spec(
        spec
    )
    spec.loader.exec_module(migration)

    return migration


def test_processing_job_model_schema_contract():

    table = ResumeProcessingJob.__table__
    columns = table.columns

    assert columns.id.primary_key is True
    assert columns.candidate_id.nullable is True
    candidate_foreign_key = next(
        iter(columns.candidate_id.foreign_keys)
    )
    assert isinstance(candidate_foreign_key, ForeignKey)
    assert candidate_foreign_key.target_fullname == (
        "candidates.id"
    )
    assert candidate_foreign_key.ondelete == "SET NULL"

    assert isinstance(columns.status.type, String)
    assert columns.status.type.length == 20
    assert columns.status.nullable is False
    assert columns.status.default.arg == "PENDING"
    assert str(columns.status.server_default.arg) == "PENDING"

    for timestamp_name in (
        "created_at",
        "started_at",
        "completed_at",
        "updated_at"
    ):
        timestamp = columns[timestamp_name]
        assert isinstance(timestamp.type, DateTime)
        assert timestamp.type.timezone is True

    constraints = {
        constraint.name
        for constraint in table.constraints
        if isinstance(constraint, CheckConstraint)
    }
    assert "ck_resume_processing_jobs_status" in constraints
    assert (
        "ck_resume_processing_jobs_resume_sha256_format"
        in constraints
    )

    indexes = {
        index.name: index
        for index in table.indexes
        if isinstance(index, Index)
    }
    assert set(indexes) == {
        "ix_resume_processing_jobs_candidate_id",
        "ix_resume_processing_jobs_status_created_at",
        "ux_resume_processing_jobs_resume_sha256"
    }


def test_processing_job_migration_contract(monkeypatch):

    migration = load_migration()
    operation = Mock()
    monkeypatch.setattr(migration, "op", operation)

    assert migration.revision == "f4a6c8e2d190"
    assert migration.down_revision == "e1b4c7d9a260"

    migration.upgrade()

    operation.create_table.assert_called_once()
    table_call = operation.create_table.call_args
    assert table_call.args[0] == "resume_processing_jobs"
    status_column = next(
        item
        for item in table_call.args[1:]
        if getattr(item, "name", None) == "status"
    )
    assert status_column.nullable is False
    assert str(status_column.server_default.arg) == "'PENDING'"
    assert operation.create_index.call_count == 2

    operation.reset_mock()
    migration.downgrade()
    assert operation.drop_index.call_count == 2
    operation.drop_table.assert_called_once_with(
        "resume_processing_jobs"
    )


def test_processing_job_creation_defaults_to_pending():

    with TestingSessionLocal() as db:
        job = processing_job_service.create_processing_job(db)

        assert job.status == ProcessingJobStatus.PENDING.value
        assert job.candidate_id is None
        assert job.error_message is None
        assert job.resume_sha256 is None
        assert job.started_at is None
        assert job.completed_at is None
        assert job.created_at is not None
        assert job.updated_at is not None


def test_valid_processing_job_transitions_set_timestamps():

    started_at = datetime(2026, 8, 11, 10, 0, 0)
    completed_at = datetime(2026, 8, 11, 10, 2, 0)

    with TestingSessionLocal() as db:
        job = processing_job_service.create_processing_job(db)

        processing = (
            processing_job_service
            .transition_processing_job(
                db,
                job.id,
                ProcessingJobStatus.PROCESSING,
                transitioned_at=started_at
            )
        )
        assert processing.status == "PROCESSING"
        assert processing.started_at == started_at
        assert processing.completed_at is None
        assert processing.error_message is None
        assert processing.updated_at == started_at

        completed = (
            processing_job_service
            .transition_processing_job(
                db,
                job.id,
                ProcessingJobStatus.COMPLETED,
                transitioned_at=completed_at
            )
        )
        assert completed.status == "COMPLETED"
        assert completed.started_at == started_at
        assert completed.completed_at == completed_at
        assert completed.updated_at == completed_at
        assert completed.error_message is None


@pytest.mark.parametrize(
    "invalid_status",
    [
        ProcessingJobStatus.COMPLETED,
        ProcessingJobStatus.FAILED,
        ProcessingJobStatus.PENDING,
    ]
)
def test_invalid_processing_job_transitions_are_rejected(
    invalid_status
):

    with TestingSessionLocal() as db:
        job = processing_job_service.create_processing_job(db)

        with pytest.raises(
            ConflictError,
            match="Invalid processing job status transition"
        ):
            processing_job_service.transition_processing_job(
                db,
                job.id,
                invalid_status
            )

        persisted = db.get(ResumeProcessingJob, job.id)
        assert persisted is not None
        assert persisted.status == "PENDING"


def test_failed_transition_stores_safe_error_message():

    failed_at = datetime(2026, 8, 11, 11, 0, 0)

    with TestingSessionLocal() as db:
        job = processing_job_service.create_processing_job(db)
        processing_job_service.transition_processing_job(
            db,
            job.id,
            ProcessingJobStatus.PROCESSING
        )
        failed = (
            processing_job_service
            .transition_processing_job(
                db,
                job.id,
                ProcessingJobStatus.FAILED,
                error_message=(
                    "PDF text could not be extracted"
                ),
                transitioned_at=failed_at
            )
        )

        assert failed.status == "FAILED"
        assert failed.completed_at == failed_at
        assert failed.error_message == (
            "PDF text could not be extracted"
        )

    assert processing_job_service.sanitize_error_message(
        "Traceback:\npassword=do-not-expose"
    ) == processing_job_service.DEFAULT_PROCESSING_ERROR


def test_concurrent_status_change_is_rejected(monkeypatch):

    with TestingSessionLocal() as db:
        job = processing_job_service.create_processing_job(db)
        monkeypatch.setattr(
            processing_job_repository,
            "transition_processing_job",
            lambda **kwargs: None
        )

        with pytest.raises(
            ConflictError,
            match="changed concurrently"
        ):
            processing_job_service.transition_processing_job(
                db,
                job.id,
                ProcessingJobStatus.PROCESSING
            )


def test_authenticated_user_can_get_processing_job_status(
    client,
    auth_headers
):

    with TestingSessionLocal() as db:
        job = processing_job_service.create_processing_job(db)
        job_id = job.id

    response = client.get(
        f"/processing-jobs/{job_id}",
        headers=auth_headers
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": job_id,
        "candidate_id": None,
        "status": "PENDING",
        "error_message": None,
        "created_at": response.json()["created_at"],
        "started_at": None,
        "completed_at": None,
        "updated_at": response.json()["updated_at"],
    }


def test_processing_job_status_requires_authentication(
    client
):

    response = client.get(
        "/processing-jobs/1"
    )

    assert response.status_code == 401


def test_missing_processing_job_returns_not_found(
    client,
    auth_headers
):

    response = client.get(
        "/processing-jobs/999999",
        headers=auth_headers
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Processing job not found"
    }
