import os

import pytest
from fastapi.testclient import TestClient

os.environ["TESTING"] = "true"

from main import app


@pytest.fixture
def client():

    with TestClient(app) as test_client:

        yield test_client


def test_update_candidate(
    client
):

    response = client.get(
        "/candidates/"
    )

    assert response.status_code == 200

    candidates = response.json()

    if not candidates:

        pytest.skip(
            "No candidates available."
        )

    candidate_id = candidates[0]["id"]

    payload = {

        "candidate_level": "Senior",

        "skill_score": 99,

    }

    response = client.put(

        f"/candidates/{candidate_id}",

        json=payload,

    )

    assert response.status_code == 200

    candidate = response.json()

    assert candidate["id"] == candidate_id
    assert candidate["candidate_level"] == "Senior"
    assert candidate["skill_score"] == 99

    assert "rule_score" in candidate
    assert "ai_score" in candidate
    assert "ai_status" in candidate