import os
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

os.environ["TESTING"] = "true"

from main import app


@pytest.fixture
def client():

    with TestClient(app) as test_client:

        yield test_client


def test_recommend_candidate(
    client
):

    recommendation = {

        "candidate_id": "148",

        "candidate_name": "Baramee Chaisuwan",

        "match_score": 95,

        "strengths": [
            "Python",
            "FastAPI",
            "LLM",
            "Docker",
        ],

        "relevant_experience": [
            (
                "AI Document Intelligence "
                "ATS Resume Screening System"
            )
        ],

        "reason": (
            "Strong match for AI Engineer role"
        ),

    }

    question = (
        "AI Engineer requiring "
        "Python FastAPI LLM Docker "
        "Machine Learning"
    )

    with patch(
        "app.api.recommend.ask_recommendation",
        return_value=recommendation
    ) as mock_recommend:

        response = client.post(
            "/recommend/",
            json={
                "question": question
            }
        )

    assert response.status_code == 200

    assert response.headers[
        "content-type"
    ].startswith(
        "application/json"
    )

    data = response.json()

    assert data == recommendation

    assert data["candidate_id"] == "148"
    assert data["candidate_name"] == (
        "Baramee Chaisuwan"
    )

    assert data["match_score"] == 95
    assert data["match_score"] >= 80

    assert len(
        data["strengths"]
    ) == 4

    assert len(
        data["relevant_experience"]
    ) == 1

    mock_recommend.assert_called_once_with(
        question
    )