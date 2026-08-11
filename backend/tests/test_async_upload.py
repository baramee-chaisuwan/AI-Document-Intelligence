from io import BytesIO
from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api import async_upload, upload
from app.core import config, security
from app.core.security import (
    create_access_token,
    hash_password
)
from app.database.database import Base, get_db
from app.database.models import (
    Candidate,
    ResumeProcessingJob,
    User
)
from app.services import async_resume_submission_service
from app.services.gcs_storage_service import (
    GCSOperationError,
    StoredGCSObject
)
from app.services.pubsub_publisher_service import (
    PubSubOperationError
)
from main import app


pytestmark = pytest.mark.real_auth

TEST_JWT_SECRET = (
    "test-only-async-upload-secret-that-is-long-enough-"
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
def isolated_async_upload_database(monkeypatch):

    Base.metadata.create_all(bind=engine)
    app.dependency_overrides[get_db] = override_get_db
    monkeypatch.setattr(
        security,
        "JWT_SECRET_KEY",
        TEST_JWT_SECRET
    )
    monkeypatch.setattr(
        config,
        "GCS_KEY_PREFIX",
        "resumes"
    )

    yield

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():

    return TestClient(app)


@pytest.fixture
def recruiter_headers():

    with TestingSessionLocal() as db:
        recruiter = User(
            email="async-recruiter@example.com",
            full_name="Async Recruiter",
            hashed_password=hash_password(
                "StrongPassword123!"
            ),
            role="recruiter",
            is_active=True
        )
        db.add(recruiter)
        db.commit()
        db.refresh(recruiter)
        token = create_access_token(recruiter.id)

    return {
        "Authorization": f"Bearer {token}"
    }


def stored_resume() -> StoredGCSObject:

    return StoredGCSObject(
        bucket="test-resume-bucket",
        key=(
            "resumes/async-1234567890abcdef/"
            "resume-hash.pdf"
        ),
        etag="test-etag"
    )


def post_async_resume(
    client,
    headers,
    content=b"%PDF-1.7\ntest resume"
):

    return client.post(
        "/upload/async",
        headers=headers,
        files={
            "file": (
                "candidate.pdf",
                BytesIO(content),
                "application/pdf"
            )
        }
    )


def test_async_submission_stores_job_and_publishes_once(
    client,
    recruiter_headers,
    monkeypatch
):

    put_object = Mock(return_value=stored_resume())
    publish = Mock(return_value="message-id")
    gemini = Mock()
    extraction = Mock()
    analysis = Mock()
    indexing = Mock()

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
    monkeypatch.setattr(upload, "summarize_document", gemini)
    monkeypatch.setattr(upload, "extract_resume_data", extraction)
    monkeypatch.setattr(upload, "analyze_resume", analysis)
    monkeypatch.setattr(upload, "index_resume", indexing)

    response = post_async_resume(
        client,
        recruiter_headers
    )

    assert response.status_code == 202
    assert response.json() == {
        "processing_job_id": response.json()[
            "processing_job_id"
        ],
        "status": "PENDING"
    }

    with TestingSessionLocal() as db:
        jobs = db.query(ResumeProcessingJob).all()
        assert len(jobs) == 1
        assert jobs[0].status == "PENDING"
        assert jobs[0].candidate_id is None
        assert db.query(Candidate).count() == 0

    upload_call = put_object.call_args.kwargs
    assert upload_call["document_id"].startswith("async-")
    assert upload_call["filename"] == "candidate.pdf"
    assert upload_call["content"] == (
        b"%PDF-1.7\ntest resume"
    )

    publish.assert_called_once()
    published_message = publish.call_args.args[0]
    assert published_message.version == 1
    assert published_message.processing_job_id == (
        response.json()["processing_job_id"]
    )
    assert published_message.gcs_object_key == (
        stored_resume().key
    )
    gemini.assert_not_called()
    extraction.assert_not_called()
    analysis.assert_not_called()
    indexing.assert_not_called()


def test_same_filename_uses_unique_storage_identity(
    client,
    recruiter_headers,
    monkeypatch
):

    document_ids = []

    def store_with_generated_key(**kwargs):
        document_ids.append(kwargs["document_id"])
        return StoredGCSObject(
            bucket="test-resume-bucket",
            key=(
                f"resumes/{kwargs['document_id']}/"
                "resume-hash.pdf"
            )
        )

    monkeypatch.setattr(
        async_resume_submission_service.gcs_storage_service,
        "put_object",
        Mock(side_effect=store_with_generated_key)
    )
    monkeypatch.setattr(
        async_resume_submission_service.pubsub_publisher_service,
        "publish_resume_processing_message",
        Mock(return_value="message-id")
    )

    first = post_async_resume(client, recruiter_headers)
    second = post_async_resume(client, recruiter_headers)

    assert first.status_code == 202
    assert second.status_code == 202
    assert len(document_ids) == 2
    assert document_ids[0] != document_ids[1]


@pytest.mark.parametrize(
    ("content", "expected_status"),
    [
        (b"not-a-pdf", 415),
        (b"", 400),
    ]
)
def test_async_submission_reuses_pdf_validation(
    client,
    recruiter_headers,
    monkeypatch,
    content,
    expected_status
):

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

    response = post_async_resume(
        client,
        recruiter_headers,
        content=content
    )

    assert response.status_code == expected_status
    put_object.assert_not_called()
    publish.assert_not_called()


def test_async_submission_rejects_oversized_pdf(
    client,
    recruiter_headers,
    monkeypatch
):

    monkeypatch.setattr(
        async_upload,
        "MAX_UPLOAD_SIZE_BYTES",
        10
    )
    monkeypatch.setattr(
        upload,
        "MAX_UPLOAD_SIZE_BYTES",
        10
    )
    put_object = Mock()
    monkeypatch.setattr(
        async_resume_submission_service.gcs_storage_service,
        "put_object",
        put_object
    )

    response = post_async_resume(
        client,
        recruiter_headers,
        content=b"%PDF-123456789"
    )

    assert response.status_code == 413
    put_object.assert_not_called()


def test_async_submission_requires_authentication(
    client,
    monkeypatch
):

    put_object = Mock()
    monkeypatch.setattr(
        async_resume_submission_service.gcs_storage_service,
        "put_object",
        put_object
    )

    response = post_async_resume(client, {})

    assert response.status_code == 401
    put_object.assert_not_called()


def test_gcs_failure_creates_no_job_or_message(
    client,
    recruiter_headers,
    monkeypatch
):

    publish = Mock()
    monkeypatch.setattr(
        async_resume_submission_service.gcs_storage_service,
        "put_object",
        Mock(side_effect=GCSOperationError("storage unavailable"))
    )
    monkeypatch.setattr(
        async_resume_submission_service.pubsub_publisher_service,
        "publish_resume_processing_message",
        publish
    )

    response = post_async_resume(
        client,
        recruiter_headers
    )

    assert response.status_code == 503
    publish.assert_not_called()
    with TestingSessionLocal() as db:
        assert db.query(ResumeProcessingJob).count() == 0


def test_job_creation_failure_cleans_up_object_without_publish(
    client,
    recruiter_headers,
    monkeypatch
):

    delete_object = Mock()
    publish = Mock()
    monkeypatch.setattr(
        async_resume_submission_service.gcs_storage_service,
        "put_object",
        Mock(return_value=stored_resume())
    )
    monkeypatch.setattr(
        async_resume_submission_service.gcs_storage_service,
        "delete_object",
        delete_object
    )
    monkeypatch.setattr(
        async_resume_submission_service.processing_job_service,
        "create_processing_job",
        Mock(side_effect=SQLAlchemyError("job insert failed"))
    )
    monkeypatch.setattr(
        async_resume_submission_service.pubsub_publisher_service,
        "publish_resume_processing_message",
        publish
    )

    response = post_async_resume(
        client,
        recruiter_headers
    )

    assert response.status_code == 503
    delete_object.assert_called_once_with(stored_resume().key)
    publish.assert_not_called()
    with TestingSessionLocal() as db:
        assert db.query(ResumeProcessingJob).count() == 0


def test_publication_failure_deletes_pending_job_and_object(
    client,
    recruiter_headers,
    monkeypatch
):

    delete_object = Mock()
    monkeypatch.setattr(
        async_resume_submission_service.gcs_storage_service,
        "put_object",
        Mock(return_value=stored_resume())
    )
    monkeypatch.setattr(
        async_resume_submission_service.gcs_storage_service,
        "delete_object",
        delete_object
    )
    monkeypatch.setattr(
        async_resume_submission_service.pubsub_publisher_service,
        "publish_resume_processing_message",
        Mock(side_effect=PubSubOperationError("publish failed"))
    )

    response = post_async_resume(
        client,
        recruiter_headers
    )

    assert response.status_code == 503
    delete_object.assert_called_once_with(stored_resume().key)
    with TestingSessionLocal() as db:
        assert db.query(ResumeProcessingJob).count() == 0
        assert db.query(Candidate).count() == 0


def test_missing_queue_configuration_is_compensated(
    client,
    recruiter_headers,
    monkeypatch
):

    delete_object = Mock()
    monkeypatch.setattr(config, "GCP_PROJECT_ID", None)
    monkeypatch.setattr(
        config,
        "PUBSUB_RESUME_PROCESSING_TOPIC",
        None
    )
    monkeypatch.setattr(
        async_resume_submission_service.gcs_storage_service,
        "put_object",
        Mock(return_value=stored_resume())
    )
    monkeypatch.setattr(
        async_resume_submission_service.gcs_storage_service,
        "delete_object",
        delete_object
    )

    response = post_async_resume(
        client,
        recruiter_headers
    )

    assert response.status_code == 503
    delete_object.assert_called_once_with(stored_resume().key)
    with TestingSessionLocal() as db:
        assert db.query(ResumeProcessingJob).count() == 0


def test_cleanup_failure_preserves_original_submission_failure(
    client,
    recruiter_headers,
    monkeypatch,
    caplog
):

    monkeypatch.setattr(
        async_resume_submission_service.gcs_storage_service,
        "put_object",
        Mock(return_value=stored_resume())
    )
    monkeypatch.setattr(
        async_resume_submission_service.gcs_storage_service,
        "delete_object",
        Mock(side_effect=GCSOperationError("cleanup failed"))
    )
    monkeypatch.setattr(
        async_resume_submission_service.pubsub_publisher_service,
        "publish_resume_processing_message",
        Mock(side_effect=PubSubOperationError("publish failed"))
    )

    response = post_async_resume(
        client,
        recruiter_headers
    )

    assert response.status_code == 503
    assert response.json() == {
        "detail": "Async resume submission is unavailable"
    }
    assert "GCS compensation failed" in caplog.text
    with TestingSessionLocal() as db:
        assert db.query(ResumeProcessingJob).count() == 0
