import json
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from app.services import extraction_service


TECHNICAL_RESUME = {
    "name": "Avery Chen",
    "skills": ["Python", "Machine Learning"],
    "experience": [{
        "title": "AI Engineer",
        "company": "Example Labs",
        "start_date": "2022-01",
        "end_date": "Present",
        "description": ["Built production APIs"],
    }],
    "projects": [{
        "name": "Document Intelligence",
        "description": ["Built a resume parser"],
        "technologies": ["FastAPI"],
    }],
}


def _extract(monkeypatch, response):
    model = Mock()
    model.generate_content.return_value = response
    monkeypatch.setattr(extraction_service, "model", model)

    result = extraction_service.extract_resume_data("Synthetic resume")
    return result, model.generate_content.call_args.kwargs["generation_config"]


def test_extracts_valid_json_with_structured_response_schema(monkeypatch):
    result, generation_config = _extract(
        monkeypatch,
        SimpleNamespace(text=json.dumps(TECHNICAL_RESUME)),
    )

    assert result["name"] == "Avery Chen"
    assert result["skills"] == ["Python", "Machine Learning"]
    assert result["experience"][0]["title"] == "AI Engineer"
    assert generation_config["response_mime_type"] == "application/json"
    assert generation_config["response_schema"] == (
        extraction_service.RESUME_RESPONSE_SCHEMA
    )


@pytest.mark.parametrize(
    "response_text",
    [
        "```json\n" + json.dumps(TECHNICAL_RESUME) + "\n```",
        "  \n" + json.dumps(TECHNICAL_RESUME) + "\n  ",
        "Resume JSON follows:\n" + json.dumps(TECHNICAL_RESUME) + "\nEnd.",
        json.dumps({"resume_data": TECHNICAL_RESUME}),
    ],
)
def test_extracts_harmlessly_wrapped_json(monkeypatch, response_text):
    result, _ = _extract(
        monkeypatch,
        SimpleNamespace(text=response_text),
    )

    assert result["name"] == "Avery Chen"


def test_extracts_json_from_response_parts_when_text_is_unavailable(monkeypatch):
    class PartsOnlyResponse:
        parts = [SimpleNamespace(text=json.dumps(TECHNICAL_RESUME))]

        @property
        def text(self):
            raise ValueError("Multiple response parts")

    result, _ = _extract(monkeypatch, PartsOnlyResponse())

    assert result["projects"][0]["technologies"] == ["FastAPI"]


def test_malformed_json_still_fails_with_controlled_error(monkeypatch):
    model = Mock()
    model.generate_content.return_value = SimpleNamespace(
        text='{"name": "Broken", "skills": ["HR",]}'
    )
    monkeypatch.setattr(extraction_service, "model", model)

    with pytest.raises(
        extraction_service.ResumeExtractionError,
        match="invalid JSON",
    ):
        extraction_service.extract_resume_data("Synthetic resume")


def test_new_cross_domain_fields_are_normalized(monkeypatch):
    payload = {
        "name": "Taylor Morgan",
        "tools": [" Workday ", ""],
        "certifications": ["SHRM-SCP"],
        "achievements": ["Reduced time-to-hire by 38%"],
        "responsibilities": ["Owned regional people strategy"],
        "domain_expertise": ["Human resources"],
        "leadership_experience": ["Led a team of 12"],
    }

    result, _ = _extract(
        monkeypatch,
        SimpleNamespace(text=json.dumps(payload)),
    )

    assert result["tools"] == ["Workday"]
    assert result["certifications"] == ["SHRM-SCP"]
    assert result["achievements"] == ["Reduced time-to-hire by 38%"]
    assert result["responsibilities"] == ["Owned regional people strategy"]
    assert result["domain_expertise"] == ["Human resources"]
    assert result["leadership_experience"] == ["Led a team of 12"]


def test_existing_technical_resume_fields_remain_compatible(monkeypatch):
    result, _ = _extract(
        monkeypatch,
        SimpleNamespace(text=json.dumps(TECHNICAL_RESUME)),
    )

    assert result["skills"] == ["Python", "Machine Learning"]
    assert result["projects"] == [{
        "name": "Document Intelligence",
        "description": ["Built a resume parser"],
        "technologies": ["FastAPI"],
    }]
    assert result["tools"] == []
