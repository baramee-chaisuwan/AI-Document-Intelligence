import os
from io import BytesIO
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient


os.environ["TESTING"] = "true"

from app.database.database import get_db
from main import app


@pytest.fixture
def mock_db():

    db = MagicMock()

    def refresh_candidate(candidate):

        candidate.id = 123

    db.refresh.side_effect = refresh_candidate

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
            "app.api.upload.index_resume"
        ) as mock_index
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
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()

    mock_index.assert_called_once_with(
        document_id="123",
        resume_text="resume text"
    )