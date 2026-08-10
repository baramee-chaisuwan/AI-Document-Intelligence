import json
from unittest.mock import Mock

import pytest

from app.services import job_extraction_service
from app.services.job_extraction_service import (
    JobRequirementExtractionError,
    extract_job_requirements,
    normalize_job_requirements
)


def gemini_response(payload):

    return Mock(
        text=json.dumps(payload)
    )


def test_extract_job_requirements_returns_structured_data(
    monkeypatch
):

    model = Mock()
    model.generate_content.return_value = (
        gemini_response({
            "required_skills": ["Python", "PostgreSQL"],
            "preferred_skills": ["FastAPI"],
            "experience_requirements": [
                "3 years of backend experience"
            ],
            "responsibilities": [
                "Build reliable APIs"
            ]
        })
    )
    monkeypatch.setattr(
        job_extraction_service,
        "get_model",
        lambda: model
    )

    result = extract_job_requirements(
        "We require Python and PostgreSQL."
    )

    assert result == {
        "required_skills": ["Python", "PostgreSQL"],
        "preferred_skills": ["FastAPI"],
        "experience_requirements": [
            "3 years of backend experience"
        ],
        "responsibilities": [
            "Build reliable APIs"
        ]
    }
    generation_config = (
        model.generate_content.call_args.kwargs[
            "generation_config"
        ]
    )
    assert generation_config["temperature"] == 0
    assert (
        generation_config["response_mime_type"]
        == "application/json"
    )


def test_missing_categories_normalize_to_empty_lists():

    result = normalize_job_requirements({
        "required_skills": ["Python"]
    })

    assert result == {
        "required_skills": ["Python"],
        "preferred_skills": [],
        "experience_requirements": [],
        "responsibilities": []
    }


def test_requirement_values_are_trimmed_and_deduplicated():

    result = normalize_job_requirements({
        "required_skills": [
            "  Python  ",
            "python",
            "PostgreSQL\n",
            "   "
        ],
        "responsibilities": [
            "Build   reliable APIs",
            "build reliable apis"
        ]
    })

    assert result["required_skills"] == [
        "Python",
        "PostgreSQL"
    ]
    assert result["responsibilities"] == [
        "Build reliable APIs"
    ]


@pytest.mark.parametrize(
    "payload",
    [
        [],
        {"required_skills": "Python"},
        {"required_skills": ["Python", 3]}
    ]
)
def test_invalid_structured_output_is_rejected(
    payload
):

    with pytest.raises(ValueError):
        normalize_job_requirements(payload)


def test_invalid_gemini_json_is_handled_safely(
    monkeypatch
):

    model = Mock()
    model.generate_content.return_value = Mock(
        text="not-json"
    )
    monkeypatch.setattr(
        job_extraction_service,
        "get_model",
        lambda: model
    )

    with pytest.raises(
        JobRequirementExtractionError
    ):
        extract_job_requirements(
            "Build reliable APIs."
        )
