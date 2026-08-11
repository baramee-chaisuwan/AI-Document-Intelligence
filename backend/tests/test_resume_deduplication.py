import hashlib
import importlib.util
from io import BytesIO
from pathlib import Path
from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import (
    CheckConstraint,
    Index,
    String,
    create_engine
)
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api import upload
from app.database.database import Base, get_db
from app.database.models import (
    Candidate,
    ResumeProcessingJob
)
from app.services import (
    async_resume_submission_service,
    resume_fingerprint_service
)
from app.services.gcs_storage_service import StoredGCSObject
from main import app


MIGRATION_PATH = (
    Path(__file__).parents[1]
    / "alembic"
    / "versions"
    / "a3d8c6e1f520_add_resume_sha256_deduplication.py"
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
def isolated_deduplication_database():

    Base.metadata.create_all(bind=engine)
    previous_override = app.dependency_overrides.get(
        get_db
    )
    app.dependency_overrides[get_db] = override_get_db

    yield

    if previous_override is None:
        app.dependency_overrides.pop(get_db, None)
    else:
        app.dependency_overrides[get_db] = previous_override

    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():

    return TestClient(app)


def candidate(
    *,
    name: str,
    resume_sha256: str | None
) -> Candidate:

    return Candidate(
        name=name,
        summary="Candidate summary",
        candidate_level="Senior",
        skill_score=90,
        rule_score=90,
        ai_score=90,
        ai_status="success",
        score_breakdown={},
        resume_sha256=resume_sha256
    )


def post_resume(
    client,
    content: bytes,
    path: str = "/upload/"
):

    return client.post(
        path,
        files={
            "file": (
                "candidate.pdf",
                BytesIO(content),
                "application/pdf"
            )
        }
    )


def configure_sync_pipeline(
    monkeypatch,
    *,
    candidate_name: str
):

    extract_pdf = Mock(return_value="Resume text")
    extract_data = Mock(return_value={
        "name": candidate_name
    })
    summarize = Mock(return_value="Candidate summary")
    analyze = Mock(return_value={
        "candidate_level": "Senior",
        "skill_score": 90,
        "rule_score": 90,
        "ai_score": 90,
        "ai_status": "success",
        "score_breakdown": {}
    })
    index_resume = Mock()
    store_resume = Mock(return_value=StoredGCSObject(
        bucket="test-resumes",
        key="resumes/test/resume.pdf"
    ))

    monkeypatch.setattr(upload, "extract_text_from_pdf", extract_pdf)
    monkeypatch.setattr(upload, "extract_resume_data", extract_data)
    monkeypatch.setattr(upload, "summarize_document", summarize)
    monkeypatch.setattr(upload, "analyze_resume", analyze)
    monkeypatch.setattr(upload, "index_resume", index_resume)
    monkeypatch.setattr(upload, "store_resume", store_resume)

    return {
        "extract_pdf": extract_pdf,
        "extract_data": extract_data,
        "summarize": summarize,
        "analyze": analyze,
        "index": index_resume,
        "store": store_resume,
    }


def test_resume_sha256_is_deterministic_and_byte_exact():

    content = b"%PDF-1.7\nresume"

    first = resume_fingerprint_service.calculate_resume_sha256(
        content
    )
    second = resume_fingerprint_service.calculate_resume_sha256(
        content
    )
    changed = resume_fingerprint_service.calculate_resume_sha256(
        content + b" changed"
    )

    assert first == hashlib.sha256(content).hexdigest()
    assert first == second
    assert changed != first
    assert len(first) == 64
    assert first == first.lower()


def test_existing_candidate_blocks_async_work(
    client,
    monkeypatch
):

    content = b"%PDF-1.7\nexisting candidate"
    resume_sha256 = hashlib.sha256(content).hexdigest()

    with TestingSessionLocal() as db:
        existing = candidate(
            name="Existing Candidate",
            resume_sha256=resume_sha256
        )
        db.add(existing)
        db.commit()
        candidate_id = existing.id

    put_object = Mock()
    publish = Mock()
    monkeypatch.setattr(
        async_resume_submission_service.gcs_storage_service,
        "put_object",
        put_object
    )
    monkeypatch.setattr(
        async_resume_submission_service.pubsub_publisher_service,
        "publish_resume_processing_message",
        publish
    )

    response = post_resume(
        client,
        content,
        path="/upload/async"
    )

    assert response.status_code == 409
    assert response.json()["candidate_id"] == candidate_id
    put_object.assert_not_called()
    publish.assert_not_called()

    with TestingSessionLocal() as db:
        assert db.query(Candidate).count() == 1
        assert db.query(ResumeProcessingJob).count() == 0


def test_synchronous_upload_persists_fingerprint(
    client,
    monkeypatch
):

    content = b"%PDF-1.7\nnew synchronous resume"
    configure_sync_pipeline(
        monkeypatch,
        candidate_name="Synchronous Candidate"
    )

    response = post_resume(client, content)

    assert response.status_code == 200
    with TestingSessionLocal() as db:
        persisted = db.query(Candidate).one()
        assert persisted.resume_sha256 == hashlib.sha256(
            content
        ).hexdigest()
        assert db.query(ResumeProcessingJob).count() == 0


def test_synchronous_exact_duplicate_stops_before_ai_or_storage(
    client,
    monkeypatch
):

    content = b"%PDF-1.7\nexact duplicate"
    resume_sha256 = hashlib.sha256(content).hexdigest()

    with TestingSessionLocal() as db:
        existing = candidate(
            name="Existing Candidate",
            resume_sha256=resume_sha256
        )
        db.add(existing)
        db.commit()
        candidate_id = existing.id

    pipeline = configure_sync_pipeline(
        monkeypatch,
        candidate_name="Existing Candidate"
    )

    response = post_resume(client, content)

    assert response.status_code == 409
    assert response.json() == {
        "status": "duplicate",
        "message": "This exact resume file already exists",
        "candidate_id": candidate_id
    }
    pipeline["extract_pdf"].assert_not_called()
    pipeline["summarize"].assert_not_called()
    pipeline["analyze"].assert_not_called()
    pipeline["index"].assert_not_called()
    pipeline["store"].assert_not_called()


def test_changed_bytes_are_new_even_with_same_candidate_name(
    client,
    monkeypatch
):

    original = b"%PDF-1.7\noriginal"
    changed = b"%PDF-1.7\nchanged"

    with TestingSessionLocal() as db:
        db.add(candidate(
            name="Same Person",
            resume_sha256=hashlib.sha256(original).hexdigest()
        ))
        db.commit()

    configure_sync_pipeline(
        monkeypatch,
        candidate_name="Same Person"
    )

    response = post_resume(client, changed)

    assert response.status_code == 200
    with TestingSessionLocal() as db:
        assert db.query(Candidate).count() == 2


def test_legacy_candidate_with_null_fingerprint_remains_valid():

    with TestingSessionLocal() as db:
        legacy = candidate(
            name="Legacy Candidate",
            resume_sha256=None
        )
        db.add(legacy)
        db.commit()
        db.refresh(legacy)

        assert legacy.id is not None
        assert legacy.resume_sha256 is None


def test_candidate_deletion_releases_fingerprint():

    resume_sha256 = hashlib.sha256(
        b"%PDF-1.7\nreusable after deletion"
    ).hexdigest()

    with TestingSessionLocal() as db:
        original = candidate(
            name="Original Candidate",
            resume_sha256=resume_sha256
        )
        db.add(original)
        db.commit()
        db.delete(original)
        db.commit()

        replacement = candidate(
            name="Replacement Candidate",
            resume_sha256=resume_sha256
        )
        db.add(replacement)
        db.commit()

        assert db.query(Candidate).one().id == replacement.id


def load_migration():

    spec = importlib.util.spec_from_file_location(
        "resume_sha256_migration",
        MIGRATION_PATH
    )
    assert spec is not None
    assert spec.loader is not None
    migration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration)

    return migration


def test_resume_sha256_model_and_migration_contract(
    monkeypatch
):

    candidate_column = Candidate.__table__.columns.resume_sha256
    job_column = ResumeProcessingJob.__table__.columns.resume_sha256

    assert isinstance(candidate_column.type, String)
    assert candidate_column.type.length == 64
    assert candidate_column.nullable is True
    assert isinstance(job_column.type, String)
    assert job_column.type.length == 64
    assert job_column.nullable is True

    candidate_indexes = {
        index.name: index
        for index in Candidate.__table__.indexes
        if isinstance(index, Index)
    }
    job_indexes = {
        index.name: index
        for index in ResumeProcessingJob.__table__.indexes
        if isinstance(index, Index)
    }
    assert candidate_indexes[
        "ux_candidates_resume_sha256"
    ].unique is True
    assert job_indexes[
        "ux_resume_processing_jobs_resume_sha256"
    ].unique is True

    candidate_constraints = {
        constraint.name
        for constraint in Candidate.__table__.constraints
        if isinstance(constraint, CheckConstraint)
    }
    assert "ck_candidates_resume_sha256_format" in (
        candidate_constraints
    )

    migration = load_migration()
    operation = Mock()
    monkeypatch.setattr(migration, "op", operation)

    assert migration.revision == "a3d8c6e1f520"
    assert migration.down_revision == "f4a6c8e2d190"

    migration.upgrade()
    assert operation.add_column.call_count == 2
    assert operation.create_check_constraint.call_count == 2
    assert operation.create_index.call_count == 2

    operation.reset_mock()
    migration.downgrade()
    assert operation.drop_index.call_count == 2
    assert operation.drop_constraint.call_count == 2
    assert operation.drop_column.call_count == 2
