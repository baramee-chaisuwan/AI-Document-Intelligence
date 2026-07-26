from fastapi.testclient import TestClient
from unittest.mock import patch

from main import app

client = TestClient(app)


def test_recommend_candidate():

    with patch(
        "app.api.recommend.ask_recommendation"
    ) as mock_recommend:

        mock_recommend.return_value = {
            "candidate_id": "148",
            "candidate_name": "Baramee Chaisuwan",
            "match_score": 95,
            "strengths": [
                "Python",
                "FastAPI",
                "LLM",
                "Docker"
            ],
            "relevant_experience": [
                "AI Document Intelligence ATS Resume Screening System"
            ],
            "reason": "Strong match for AI Engineer role"
        }

        response = client.post(
            "/recommend/",
            json={
                "question":
                "AI Engineer requiring Python FastAPI LLM Docker Machine Learning"
            }
        )

    assert response.status_code == 200

    data = response.json()

    assert "candidate_id" in data
    assert "candidate_name" in data
    assert "match_score" in data
    assert "strengths" in data
    assert "relevant_experience" in data
    assert "reason" in data

    assert data["candidate_id"] == "148"
    assert data["match_score"] > 80