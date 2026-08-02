from fastapi.testclient import TestClient
from unittest.mock import patch
from io import BytesIO

from main import app

client = TestClient(app)


def test_upload_resume():

    fake_pdf = b"%PDF-1.4 fake"

    with patch(
        "app.api.upload.check_duplicate"
    ) as mock_duplicate, patch(
        "app.api.upload.extract_text_from_pdf"
    ) as mock_pdf, patch(
        "app.api.upload.summarize_document"
    ) as mock_summary, patch(
        "app.api.upload.extract_resume_data"
    ) as mock_extract, patch(
        "app.api.upload.analyze_resume"
    ) as mock_analyze, patch(
        "app.api.upload.index_resume"
    ):

        # บังคับว่าไม่พบข้อมูลซ้ำ
        mock_duplicate.return_value = None

        mock_pdf.return_value = "resume text"

        mock_summary.return_value = "summary"

        mock_extract.return_value = {
            "name": "Baramee Chaisuwan"
        }

        mock_analyze.return_value = {
            "candidate_level": "Junior",
            "skill_score": 90,
            "rule_score": 90,
            "ai_score": 95,
            "ai_status": "Excellent",
            "score_breakdown": {}
        }

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

    data = response.json()

    assert data["message"] == "File uploaded successfully"
    assert data["filename"] == "resume.pdf"