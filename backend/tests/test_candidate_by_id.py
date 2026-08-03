import os

import pytest
from fastapi.testclient import TestClient

os.environ["TESTING"] = "true"

from main import app


@pytest.fixture
def client():

    with TestClient(app) as test_client:

        yield test_client


def test_get_candidate_by_id(
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

    response = client.get(
        f"/candidates/{candidate_id}"
    )

    assert response.status_code == 200

    candidate = response.json()

    assert candidate["id"] == candidate_id
    assert "name" in candidate
    assert "candidate_level" in candidate
    assert "skill_score" in candidate
    assert "rule_score" in candidate
    assert "ai_score" in candidate
    assert "ai_status" in candidate