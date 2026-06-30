from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_get_candidate_by_id():

    candidates = client.get("/candidates").json()

    if not candidates:
        return

    candidate_id = candidates[0]["id"]

    response = client.get(f"/candidates/{candidate_id}")

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == candidate_id