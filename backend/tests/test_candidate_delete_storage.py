from unittest.mock import Mock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database.database import Base, get_db
from app.database.models import Candidate
from app.services import candidate_service
from app.services.gcs_storage_service import GCSOperationError
from main import app


engine = create_engine(
    "sqlite://",
    connect_args={
        "check_same_thread": False
    },
    poolclass=StaticPool
)

TestingSessionLocal = sessionmaker(
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
def isolated_candidate_database():

    Base.metadata.create_all(
        bind=engine
    )

    previous_override = (
        app.dependency_overrides.get(
            get_db
        )
    )
    app.dependency_overrides[
        get_db
    ] = override_get_db

    yield

    if previous_override is None:

        app.dependency_overrides.pop(
            get_db,
            None
        )

    else:

        app.dependency_overrides[
            get_db
        ] = previous_override

    Base.metadata.drop_all(
        bind=engine
    )


@pytest.fixture
def client():

    with TestClient(
        app,
        raise_server_exceptions=False
    ) as test_client:

        yield test_client


def create_candidate(
    *,
    resume_storage_key=None
):

    with TestingSessionLocal() as db:

        candidate = Candidate(
            name="Delete Test Candidate",
            summary="Candidate deletion test",
            candidate_level="Junior",
            skill_score=80,
            rule_score=80,
            ai_score=80,
            ai_status="success",
            score_breakdown={},
            resume_storage_key=resume_storage_key,
            resume_filename=(
                "resume.pdf"
                if resume_storage_key
                else None
            )
        )

        db.add(candidate)
        db.commit()

        return candidate.id


def candidate_exists(candidate_id):

    with TestingSessionLocal() as db:

        return (
            db.get(
                Candidate,
                candidate_id
            )
            is not None
        )


def test_delete_candidate_removes_stored_resume_and_preserves_response(
    client
):

    object_key = "resumes/42/resume-hash.pdf"
    candidate_id = create_candidate(
        resume_storage_key=object_key
    )

    with patch(
        "app.services.candidate_service.delete_object"
    ) as storage_delete:

        response = client.delete(
            f"/candidates/{candidate_id}"
        )

    assert response.status_code == 200
    assert response.json() == {
        "message": "Candidate deleted successfully"
    }
    storage_delete.assert_called_once_with(
        object_key
    )
    assert candidate_exists(candidate_id) is False

def test_delete_candidate_without_storage_key_skips_cleanup(
    client
):

    candidate_id = create_candidate()

    with patch(
        "app.services.candidate_service.delete_object"
    ) as storage_delete:

        response = client.delete(
            f"/candidates/{candidate_id}"
        )

    assert response.status_code == 200
    storage_delete.assert_not_called()
    assert candidate_exists(candidate_id) is False


def test_gcs_delete_failure_rolls_back_candidate_deletion(
    client
):

    object_key = "resumes/42/storage-failure-hash.pdf"
    candidate_id = create_candidate(
        resume_storage_key=object_key
    )

    with patch(
        "app.services.candidate_service.delete_object",
        side_effect=GCSOperationError(
            "GCS delete failed"
        )
    ) as storage_delete:

        response = client.delete(
            f"/candidates/{candidate_id}"
        )

    assert response.status_code == 500
    storage_delete.assert_called_once_with(
        object_key
    )
    assert candidate_exists(candidate_id) is True


def test_database_flush_failure_preserves_candidate_and_storage(
    client
):

    object_key = "resumes/42/db-flush-failure-hash.pdf"
    candidate_id = create_candidate(
        resume_storage_key=object_key
    )

    with patch(
        "app.repositories.candidate_repository.delete_candidate",
        side_effect=SQLAlchemyError(
            "delete flush failed"
        )
    ), patch(
        "app.services.candidate_service.delete_object"
    ) as storage_delete:

        response = client.delete(
            f"/candidates/{candidate_id}"
        )

    assert response.status_code == 500
    storage_delete.assert_not_called()
    assert candidate_exists(candidate_id) is True


def test_commit_failure_after_storage_delete_rolls_back_candidate(
    client,
    caplog
):

    object_key = "resumes/42/db-commit-failure-hash.pdf"
    candidate_id = create_candidate(
        resume_storage_key=object_key
    )
    request_sessions = []

    def override_failing_commit_db():

        db = TestingSessionLocal()
        rollback = Mock(
            wraps=db.rollback
        )
        db.rollback = rollback
        db.commit = Mock(
            side_effect=SQLAlchemyError(
                "delete commit failed"
            )
        )
        request_sessions.append(db)

        try:

            yield db

        finally:

            db.close()

    app.dependency_overrides[
        get_db
    ] = override_failing_commit_db

    with patch(
        "app.services.candidate_service.delete_object"
    ) as storage_delete:

        response = client.delete(
            f"/candidates/{candidate_id}"
        )

    assert response.status_code == 500
    storage_delete.assert_called_once_with(
        object_key
    )
    request_sessions[0].rollback.assert_called_once()
    assert candidate_exists(candidate_id) is True
    assert "reconciliation is required" in caplog.text


def test_rollback_failure_does_not_replace_original_database_error(
    caplog
):

    db = Mock()
    candidate = Mock(
        resume_storage_key=None
    )
    original_error = SQLAlchemyError(
        "original delete failure"
    )
    db.rollback.side_effect = SQLAlchemyError(
        "secondary rollback failure"
    )

    with patch(
        "app.repositories.candidate_repository.get_candidate_by_id",
        return_value=candidate
    ), patch(
        "app.repositories.candidate_repository.delete_candidate",
        side_effect=original_error
    ):

        with pytest.raises(SQLAlchemyError) as exc_info:

            candidate_service.delete_candidate(
                db,
                42
            )

    assert exc_info.value is original_error
    db.rollback.assert_called_once()
    assert "rollback failed" in caplog.text
