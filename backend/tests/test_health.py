import os

from fastapi.testclient import TestClient

os.environ["TESTING"] = "true"

from main import app

def test_health():

    with TestClient(app) as client:

        response = client.get(
            "/health"
        )

    assert response.status_code == 200