from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_get_candidates():
    response = client.get("/candidates")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/json")

    data = response.json()

    assert isinstance(data, list)

    if data:
        assert "id" in data[0]
        assert "name" in data[0]


def test_get_candidate_stats():
    response = client.get("/candidates/stats")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/json")

    data = response.json()

    assert "total_candidates" in data
    assert "average_skill_score" in data


def test_get_ranking():
    response = client.get("/candidates/ranking")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/json")

    data = response.json()

    assert isinstance(data, list)

    if data:
        assert "name" in data[0]
        assert "skill_score" in data[0]


def test_search_candidates():
    response = client.get("/candidates/search")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/json")

    data = response.json()

    assert isinstance(data, list)

    if data:
        assert "name" in data[0]