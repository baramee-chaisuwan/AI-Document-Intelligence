from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_export_csv():
    response = client.get("/export/csv")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")
    assert "attachment" in response.headers["content-disposition"]