from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_update_candidate():

    candidates = client.get("/candidates").json()

    if not candidates:
        return

    candidate_id = candidates[0]["id"]

    payload = {
        "candidate_level": "Senior",
        "skill_score": 99
    }

    response = client.put(
        f"/candidates/{candidate_id}",
        json=payload
    )

    assert response.status_code == 200

    data = response.json()

    assert data["candidate_level"] == "Senior"
    assert data["skill_score"] == 99