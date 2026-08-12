import os
from unittest.mock import ANY, patch

import pytest
from fastapi.testclient import TestClient


os.environ["TESTING"] = "true"

from main import app


@pytest.fixture
def client():

    with TestClient(app) as test_client:

        yield test_client


def test_assistant_rag(
    client
):

    expected_answer = (
        "AI Document Intelligence ATS Resume Screening System "
        "was built by Baramee."
    )

    with patch(
        "app.api.assistant.ask_assistant",
        return_value=expected_answer
    ) as mock_assistant:

        response = client.post(
            "/assistant/",
            json={
                "question": (
                    "Who built AI Document Intelligence "
                    "ATS Resume Screening System?"
                )
            }
        )

    assert response.status_code == 200

    assert response.headers[
        "content-type"
    ].startswith(
        "application/json"
    )

    data = response.json()

    assert data == {
        "answer": expected_answer
    }

    mock_assistant.assert_called_once_with(
        (
            "Who built AI Document Intelligence "
            "ATS Resume Screening System?"
        ),
        ANY
    )
