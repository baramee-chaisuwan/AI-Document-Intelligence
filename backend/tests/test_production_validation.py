import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.models.assistant_model import AssistantRequest
from app.models.candidate_update_model import CandidateUpdate
from app.models.job_model import JobCreateRequest
from app.models.search_model import SearchRequest
from main import app


@pytest.fixture
def client():

    return TestClient(app)


@pytest.mark.parametrize(
    "model,field",
    [
        (AssistantRequest, "question"),
        (SearchRequest, "query")
    ]
)
def test_ai_query_models_trim_and_reject_unsafe_sizes(
    model,
    field
):

    value = model(**{field: "  useful query  "})
    assert getattr(value, field) == "useful query"

    with pytest.raises(ValidationError):
        model(**{field: "   "})

    with pytest.raises(ValidationError):
        model(**{field: "x" * 2001})


def test_job_description_has_production_size_limit():

    with pytest.raises(ValidationError):
        JobCreateRequest(
            title="Engineer",
            description="x" * 10001
        )


def test_candidate_update_normalizes_and_bounds_values():

    update = CandidateUpdate(
        candidate_level="  Senior  ",
        skill_score=100
    )
    assert update.candidate_level == "Senior"
    assert update.skill_score == 100

    with pytest.raises(ValidationError):
        CandidateUpdate(candidate_level="   ")

    with pytest.raises(ValidationError):
        CandidateUpdate(skill_score=-1)

    with pytest.raises(ValidationError):
        CandidateUpdate(skill_score=101)


@pytest.mark.parametrize(
    "path",
    [
        "/candidates/?skip=-1",
        "/candidates/?limit=0",
        "/candidates/?limit=101",
        "/candidates/ranking?limit=101",
        "/dashboard/top-candidates?limit=0",
        "/dashboard/recent-candidates?limit=101",
        "/candidates/search?min_score=-1",
        "/candidates/search?min_score=101"
    ]
)
def test_collection_query_limits_are_bounded(
    client,
    path
):

    response = client.get(path)

    assert response.status_code == 422
