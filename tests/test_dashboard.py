from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_dashboard_summary():
    response = client.get("/dashboard/summary")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/json")

    data = response.json()

    assert isinstance(data, dict)


def test_top_candidates():
    response = client.get("/dashboard/top-candidates")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/json")

    data = response.json()

    assert isinstance(data, list)


def test_score_distribution():
    response = client.get("/dashboard/score-distribution")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/json")

    data = response.json()

    assert isinstance(data, list)


def test_level_distribution():
    response = client.get("/dashboard/level-distribution")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/json")

    data = response.json()

    assert isinstance(data, list)


def test_recent_candidates():
    response = client.get("/dashboard/recent-candidates")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/json")

    data = response.json()

    assert isinstance(data, list)