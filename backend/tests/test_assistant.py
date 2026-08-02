from fastapi.testclient import TestClient
from unittest.mock import patch

from main import app

client = TestClient(app)


def test_assistant_rag():

    with patch(
        "app.api.assistant.ask_assistant"
    ) as mock_assistant:

        mock_assistant.return_value = (
            "AI Document Intelligence ATS Resume Screening System "
            "was built by Baramee."
        )

        response = client.post(
            "/assistant/",
            json={
                "question":
                "Who built AI Document Intelligence ATS Resume Screening System?"
            }
        )

    assert response.status_code == 200

    data = response.json()

    assert "answer" in data
    assert "Baramee" in data["answer"]