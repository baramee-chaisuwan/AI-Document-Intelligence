import os

import pytest
from fastapi.testclient import TestClient

os.environ["TESTING"] = "true"

from main import app


@pytest.fixture
def client():

    with TestClient(app) as test_client:

        yield test_client


def assert_json_response(response):

    assert response.status_code == 200

    assert response.headers[
        "content-type"
    ].startswith(
        "application/json"
    )


def test_dashboard_summary(
    client
):

    response = client.get(
        "/dashboard/summary"
    )

    assert_json_response(
        response
    )

    data = response.json()

    assert isinstance(
        data,
        dict
    )

    assert "total_candidates" in data
    assert "average_score" in data
    assert "top_candidate" in data
    assert "top_score" in data


def test_top_candidates(
    client
):

    response = client.get(
        "/dashboard/top-candidates"
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
        assert "ai_score" in candidate


def test_score_distribution(
    client
):

    response = client.get(
        "/dashboard/score-distribution"
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

        item = data[0]

        assert "score_range" in item
        assert "count" in item


def test_level_distribution(
    client
):

    response = client.get(
        "/dashboard/level-distribution"
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

        item = data[0]

        assert "level" in item
        assert "count" in item


def test_recent_candidates(
    client
):

    response = client.get(
        "/dashboard/recent-candidates"
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
        assert "ai_score" in candidate