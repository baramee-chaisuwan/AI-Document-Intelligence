import os
from io import BytesIO
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError


os.environ["TESTING"] = "true"

from app.database.database import get_db
from app.services.gcs_storage_service import (
    GCSOperationError,
    StoredGCSObject
)
from app.services.indexing_service import (
    ResumeIndexingError
)
from main import app


@pytest.fixture
def mock_db():

    db = MagicMock()

    def flush_candidate():

        candidate = db.add.call_args.args[0]
        candidate.id = 123

    db.flush.side_effect = flush_candidate

    return db


@pytest.fixture
def client(
    mock_db
):

    def override_get_db():

        yield mock_db

    app.dependency_overrides[
        get_db
    ] = override_get_db

    with TestClient(app) as test_client:

        yield test_client

    app.dependency_overrides.clear()


def test_upload_resume(
    client,
    mock_db
):

    fake_pdf = (
        b"%PDF-1.4\n"
        b"fake resume content"
    )

    resume_data = {
        "name": "Baramee Chaisuwan",
        "skills": [
            "Python",
            "FastAPI",
            "Docker"
        ],
        "languages": [
            "Thai",
            "English"
        ],
        "education": [],
        "experience": [],
        "projects": [
            {
                "name": (
                    "AI Document Intelligence"
                ),
                "description": [
                    "Built an AI-powered ATS"
                ],
                "technologies": [
                    "Python",
                    "FastAPI"
                ]
            }
        ]
    }

    analysis = {
        "candidate_level": "Junior",
        "skill_score": 90,
        "rule_score": 89,
        "ai_score": 95,
        "ai_status": "success",
        "score_breakdown": {
            "python": 8,
            "sql": 8,
            "backend": 7,
            "devops": 7,
            "ai_domain": 8,
            "data_domain": 7,
            "backend_domain": 5,
            "experience": 20,
            "projects": 10,
            "engineering_signal": 9
        },
        "project_count": 1,
        "recommended_roles": [
            "AI/ML Engineer"
        ],
        "strengths": [
            "Strong Python skills"
        ],
        "improvement_areas": []
    }

    operation_order = []

    def add_candidate(candidate):

        operation_order.append("add")

    def flush_candidate():

        operation_order.append("flush")
        candidate = mock_db.add.call_args.args[0]
        candidate.id = 123

    def store_candidate_resume(**kwargs):

        operation_order.append("gcs_upload")

        return StoredGCSObject(
            bucket="ats-resumes-test",
            key="resumes/123/resume-hash.pdf",
            etag="etag-123"
        )

    def commit_candidate():

        candidate = mock_db.add.call_args.args[0]
        assert (
            candidate.resume_storage_key
            == "resumes/123/resume-hash.pdf"
        )
        assert candidate.resume_filename == "resume.pdf"
        operation_order.append("commit")

    def index_candidate(**kwargs):

        operation_order.append("index")

    mock_db.add.side_effect = add_candidate
    mock_db.flush.side_effect = flush_candidate
    mock_db.commit.side_effect = commit_candidate

    with (
        patch(
            "app.api.upload.check_duplicate",
            return_value=None
        ) as mock_duplicate,
        patch(
            "app.api.upload.extract_text_from_pdf",
            return_value="resume text"
        ) as mock_pdf,
        patch(
            "app.api.upload.summarize_document",
            return_value="AI resume summary"
        ) as mock_summary,
        patch(
            "app.api.upload.extract_resume_data",
            return_value=resume_data
        ) as mock_extract,
        patch(
            "app.api.upload.analyze_resume",
            return_value=analysis
        ) as mock_analyze,
        patch(
            "app.api.upload.index_resume",
            side_effect=index_candidate
        ) as mock_index,
        patch(
            "app.api.upload.store_resume",
            side_effect=store_candidate_resume
        ) as mock_store
    ):

        response = client.post(
            "/upload/",
            files={
                "file": (
                    "resume.pdf",
                    BytesIO(fake_pdf),
                    "application/pdf"
                )
            }
        )

    assert response.status_code == 200

    assert response.headers[
        "content-type"
    ].startswith(
        "application/json"
    )

    data = response.json()

    assert (
        data["message"]
        == "File uploaded and indexed successfully"
    )

    assert data["filename"] == "resume.pdf"
    assert data["candidate_id"] == 123
    assert data["summary"] == "AI resume summary"

    assert (
        data["resume_data"]["name"]
        == "Baramee Chaisuwan"
    )

    assert data["resume_data"]["skills"] == [
        "Python",
        "FastAPI",
        "Docker"
    ]

    assert (
        data["analysis"]["candidate_level"]
        == "Junior"
    )

    assert data["analysis"]["ai_status"] == "success"
    assert data["analysis"]["skill_score"] == 90
    assert data["analysis"]["rule_score"] == 89
    assert data["analysis"]["ai_score"] == 95

    mock_duplicate.assert_called_once_with(
        mock_db,
        "Baramee Chaisuwan"
    )

    mock_pdf.assert_called_once()
    mock_summary.assert_called_once_with(
        "resume text"
    )
    mock_extract.assert_called_once_with(
        "resume text"
    )
    mock_analyze.assert_called_once_with(
        resume_data
    )

    mock_db.add.assert_called_once()
    mock_db.flush.assert_called_once()
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_not_called()
    assert operation_order == [
        "add",
        "flush",
        "gcs_upload",
        "index",
        "commit"
    ]

    candidate = mock_db.add.call_args.args[0]
    assert (
        candidate.resume_storage_key
        == "resumes/123/resume-hash.pdf"
    )
    assert candidate.resume_filename == "resume.pdf"

    mock_store.assert_called_once_with(
        document_id=123,
        filename="resume.pdf",
        content=fake_pdf
    )

    mock_index.assert_called_once_with(
        db=mock_db,
        document_id="123",
        resume_text="resume text"
    )


def _post_resume_with_mocked_pipeline(
    client,
    *,
    store_result=None,
    store_error=None,
    cleanup_error=None,
    index_error=None
):

    fake_pdf = (
        b"%PDF-1.4\n"
        b"transaction test resume"
    )

    resume_data = {
        "name": "Transaction Test Candidate",
        "skills": ["Python"]
    }

    analysis = {
        "candidate_level": "Junior",
        "skill_score": 80,
        "rule_score": 81,
        "ai_score": 82,
        "ai_status": "success",
        "score_breakdown": {}
    }

    with (
        patch(
            "app.api.upload.check_duplicate",
            return_value=None
        ),
        patch(
            "app.api.upload.extract_text_from_pdf",
            return_value="transaction resume text"
        ),
        patch(
            "app.api.upload.extract_resume_data",
            return_value=resume_data
        ),
        patch(
            "app.api.upload.summarize_document",
            return_value="Transaction test summary"
        ),
        patch(
            "app.api.upload.analyze_resume",
            return_value=analysis
        ),
        patch(
            "app.api.upload.index_resume",
            side_effect=index_error
        ) as mock_index,
        patch(
            "app.api.upload.store_resume",
            return_value=store_result,
            side_effect=store_error
        ) as mock_store,
        patch(
            "app.api.upload.delete_stored_resume",
            side_effect=cleanup_error
        ) as mock_delete
    ):

        response = client.post(
            "/upload/",
            files={
                "file": (
                    "transaction-resume.pdf",
                    BytesIO(fake_pdf),
                    "application/pdf"
                )
            }
        )

    return {
        "response": response,
        "store": mock_store,
        "delete": mock_delete,
        "index": mock_index,
        "file_bytes": fake_pdf
    }


def test_gcs_upload_failure_rolls_back_without_committing(
    client,
    mock_db
):

    result = _post_resume_with_mocked_pipeline(
        client,
        store_error=GCSOperationError(
            "GCS upload failed"
        )
    )

    assert result["response"].status_code == 503
    assert result["response"].json() == {
        "detail": (
            "Resume storage service "
            "is unavailable"
        )
    }
    mock_db.add.assert_called_once()
    mock_db.flush.assert_called_once()
    mock_db.rollback.assert_called_once()
    mock_db.commit.assert_not_called()
    result["delete"].assert_not_called()
    result["index"].assert_not_called()


def test_commit_failure_rolls_back_and_deletes_uploaded_object(
    client,
    mock_db
):

    object_key = (
        "resumes/123/transaction-resume-hash.pdf"
    )
    mock_db.commit.side_effect = SQLAlchemyError(
        "commit failed"
    )

    result = _post_resume_with_mocked_pipeline(
        client,
        store_result=StoredGCSObject(
            bucket="ats-resumes-test",
            key=object_key,
            etag="etag-123"
        )
    )

    assert result["response"].status_code == 500
    assert result["response"].json() == {
        "detail": "Candidate could not be saved"
    }
    mock_db.flush.assert_called_once()
    mock_db.commit.assert_called_once()
    mock_db.rollback.assert_called_once()
    result["delete"].assert_called_once_with(
        object_key
    )
    result["index"].assert_called_once_with(
        db=mock_db,
        document_id="123",
        resume_text="transaction resume text"
    )


def test_cleanup_failure_does_not_replace_commit_failure(
    client,
    mock_db,
    caplog
):

    object_key = (
        "resumes/123/cleanup-failure-hash.pdf"
    )
    mock_db.commit.side_effect = SQLAlchemyError(
        "original commit failure"
    )

    result = _post_resume_with_mocked_pipeline(
        client,
        store_result=StoredGCSObject(
            bucket="ats-resumes-test",
            key=object_key,
            etag="etag-123"
        ),
        cleanup_error=GCSOperationError(
            "cleanup failed"
        )
    )

    assert result["response"].status_code == 500
    assert result["response"].json() == {
        "detail": "Candidate could not be saved"
    }
    result["delete"].assert_called_once_with(
        object_key
    )
    assert "GCS compensation failed" in caplog.text


def test_indexing_failure_rolls_back_and_deletes_uploaded_object(
    client,
    mock_db
):

    object_key = "resumes/123/indexing-failure-hash.pdf"

    result = _post_resume_with_mocked_pipeline(
        client,
        store_result=StoredGCSObject(
            bucket="ats-resumes-test",
            key=object_key,
            etag="etag-123"
        ),
        index_error=ResumeIndexingError(
            "embedding unavailable"
        )
    )

    assert result["response"].status_code == 503
    assert result["response"].json() == {
        "detail": (
            "Resume indexing service is unavailable"
        )
    }
    mock_db.rollback.assert_called_once()
    mock_db.commit.assert_not_called()
    result["delete"].assert_called_once_with(
        object_key
    )
