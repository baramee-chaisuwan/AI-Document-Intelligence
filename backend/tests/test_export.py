import os

import pytest
from fastapi.testclient import TestClient

os.environ["TESTING"] = "true"

from main import app


@pytest.fixture
def client():

    with TestClient(app) as test_client:

        yield test_client


def test_export_csv(
    client
):

    response = client.get(
        "/export/csv"
    )

    assert response.status_code == 200

    assert response.headers[
        "content-type"
    ].startswith(
        "text/csv"
    )

    assert (
        "attachment"
        in response.headers[
            "content-disposition"
        ]
    )

    content = (
        response.content.decode(
            "utf-8"
        )
    )

    assert (
        "id"
        in content
    )

    assert (
        "name"
        in content
    )

    assert (
        "candidate_level"
        in content
    )

    assert (
        "skill_score"
        in content
    )