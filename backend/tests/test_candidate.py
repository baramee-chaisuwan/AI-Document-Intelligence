import os

import pytest
from fastapi.testclient import TestClient


os.environ["TESTING"] = "true"

from main import app


@pytest.fixture
def client():

    with TestClient(app) as test_client:

        yield test_client


def assert_json_response(
    response
):

    assert response.status_code == 200

    assert response.headers[
        "content-type"
    ].startswith(
        "application/json"
    )


def test_get_candidates(
    client
):

    response = client.get(
        "/candidates/"
    )

    assert_json_response(
        response
    )

    data = response.json()

    assert isinstance(
        data,
        list
    )


    if data:

        candidate = data[0]

        assert "id" in candidate
        assert "name" in candidate
        assert "candidate_level" in candidate
        assert "skill_score" in candidate
        assert "rule_score" in candidate
        assert "ai_score" in candidate
        assert "ai_status" in candidate


def test_get_candidate_stats(
    client
):

    response = client.get(
        "/candidates/stats"
    )

    assert_json_response(
        response
    )

    data = response.json()

    assert "total_candidates" in data
    assert "average_ai_score" in data

    assert isinstance(
        data["total_candidates"],
        int
    )

    assert data[
        "total_candidates"
    ] >= 0

    assert isinstance(
        data["average_ai_score"],
        (
            int,
            float
        )
    )

    assert (
        0
        <= data["average_ai_score"]
        <= 100
    )


def test_get_ranking(
    client
):

    response = client.get(
        "/candidates/ranking"
    )

    assert_json_response(
        response
    )

    data = response.json()

    assert isinstance(
        data,
        list
    )


    if data:

        candidate = data[0]

        assert "id" in candidate
        assert "name" in candidate
        assert "skill_score" in candidate


        scores = [
            item["skill_score"]
            for item in data
        ]


        assert scores == sorted(
            scores,
            reverse=True
        )


def test_search_candidates(
    client
):

    response = client.get(
        "/candidates/search"
    )

    assert_json_response(
        response
    )

    data = response.json()

    assert isinstance(
        data,
        list
    )


    for candidate in data:

        assert "id" in candidate
        assert "name" in candidate
        assert "candidate_level" in candidate
        assert "skill_score" in candidate