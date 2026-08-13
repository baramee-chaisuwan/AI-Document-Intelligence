import json
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from google.api_core import exceptions as google_exceptions
from google.generativeai import protos
from google.generativeai.types import generation_types

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


def _candidate_response(
    *,
    finish_reason="STOP",
    parts=None,
    prompt_block_reason="BLOCK_REASON_UNSPECIFIED",
):
    candidate = SimpleNamespace(
        finish_reason=finish_reason,
        content=SimpleNamespace(parts=parts if parts is not None else []),
    )
    return SimpleNamespace(
        candidates=[candidate],
        prompt_feedback=SimpleNamespace(block_reason=prompt_block_reason),
    )


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


def test_required_response_schema_is_accepted_by_installed_sdk():
    converted = generation_types.to_generation_config_dict({
        "response_mime_type": "application/json",
        "response_schema": extraction_service.RESUME_RESPONSE_SCHEMA,
    })

    schema = converted["response_schema"]
    assert set(schema.required) == set(
        extraction_service.EMPTY_RESUME_DATA
    )
    assert set(schema.properties["education"].items.required) == {
        "institution",
        "degree",
        "start_date",
        "end_date",
    }
    assert set(schema.properties["experience"].items.required) == {
        "title",
        "company",
        "start_date",
        "end_date",
        "description",
    }
    assert set(schema.properties["projects"].items.required) == {
        "name",
        "description",
        "technologies",
    }


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
    model.generate_content.return_value = _candidate_response(
        parts=[SimpleNamespace(
            text='{"name": "Broken", "skills": ["HR",]}'
        )]
    )
    monkeypatch.setattr(extraction_service, "model", model)

    with pytest.raises(
        extraction_service.ResumeExtractionError,
        match="invalid JSON",
    ) as error:
        extraction_service.extract_resume_data("Synthetic resume")

    assert error.value.category == "malformed_json"


def test_empty_candidates_are_classified(monkeypatch):
    model = Mock()
    model.generate_content.return_value = SimpleNamespace(
        candidates=[],
        prompt_feedback=SimpleNamespace(
            block_reason="BLOCK_REASON_UNSPECIFIED"
        ),
    )
    monkeypatch.setattr(extraction_service, "model", model)

    with pytest.raises(extraction_service.ResumeExtractionError) as error:
        extraction_service.extract_resume_data("Synthetic resume")

    assert error.value.category == "empty_candidates"


def test_prompt_block_reason_is_classified_without_prompt_content(monkeypatch):
    model = Mock()
    model.generate_content.return_value = SimpleNamespace(
        candidates=[],
        prompt_feedback=SimpleNamespace(block_reason="SAFETY"),
    )
    monkeypatch.setattr(extraction_service, "model", model)

    with pytest.raises(extraction_service.ResumeExtractionError) as error:
        extraction_service.extract_resume_data("Synthetic resume")

    assert error.value.category == "prompt_blocked"
    assert error.value.safe_metadata["prompt_block_reason"] == "SAFETY"


def test_empty_parts_are_classified(monkeypatch):
    model = Mock()
    model.generate_content.return_value = _candidate_response(parts=[])
    monkeypatch.setattr(extraction_service, "model", model)

    with pytest.raises(extraction_service.ResumeExtractionError) as error:
        extraction_service.extract_resume_data("Synthetic resume")

    assert error.value.category == "empty_parts"


@pytest.mark.parametrize(
    ("finish_reason", "category"),
    [
        (protos.Candidate.FinishReason.MAX_TOKENS, "max_tokens"),
        (protos.Candidate.FinishReason.SAFETY, "safety"),
        (protos.Candidate.FinishReason.SPII, "spii"),
        (protos.Candidate.FinishReason.RECITATION, "recitation"),
        (protos.Candidate.FinishReason.OTHER, "non_success_finish_reason"),
    ],
)
def test_non_success_finish_reasons_are_classified(
    monkeypatch,
    finish_reason,
    category,
):
    model = Mock()
    model.generate_content.return_value = _candidate_response(
        finish_reason=finish_reason,
        parts=[],
    )
    monkeypatch.setattr(extraction_service, "model", model)

    with pytest.raises(extraction_service.ResumeExtractionError) as error:
        extraction_service.extract_resume_data("Synthetic resume")

    assert error.value.category == category


def test_non_text_parts_are_classified(monkeypatch):
    model = Mock()
    model.generate_content.return_value = _candidate_response(
        parts=[SimpleNamespace(function_call=object())]
    )
    monkeypatch.setattr(extraction_service, "model", model)

    with pytest.raises(extraction_service.ResumeExtractionError) as error:
        extraction_service.extract_resume_data("Synthetic resume")

    assert error.value.category == "no_text_parts"


def test_upstream_timeout_uses_bounded_request_options(monkeypatch):
    model = Mock()
    model.generate_content.side_effect = google_exceptions.DeadlineExceeded(
        "provider detail must remain private"
    )
    monkeypatch.setattr(extraction_service, "model", model)

    with pytest.raises(extraction_service.ResumeExtractionError) as error:
        extraction_service.extract_resume_data("Synthetic resume")

    request_options = model.generate_content.call_args.kwargs[
        "request_options"
    ]
    assert error.value.category == "upstream_or_normalization_failure"
    assert request_options["timeout"] == 60
    assert request_options["retry"]._timeout == 90


def test_diagnostics_are_timed_and_do_not_expose_content(monkeypatch):
    private_resume = "PRIVATE RESUME CONTENT"
    private_generated = "PRIVATE GENERATED CONTENT"
    generated_payload = {
        **TECHNICAL_RESUME,
        "name": private_generated,
    }
    response = _candidate_response(
        parts=[SimpleNamespace(text=json.dumps(generated_payload))]
    )
    events = []
    model = Mock()
    model.generate_content.return_value = response
    monkeypatch.setattr(extraction_service, "model", model)
    monkeypatch.setattr(
        extraction_service,
        "emit_event",
        lambda event, **fields: events.append((event, fields)),
    )

    result = extraction_service.extract_resume_data(private_resume)

    assert result["name"] == private_generated
    event_text = repr(events)
    assert private_resume not in event_text
    assert private_generated not in event_text
    upstream = next(
        fields
        for event, fields in events
        if event == "gemini_resume_extraction_upstream"
    )
    parsing = next(
        fields
        for event, fields in events
        if event == "gemini_resume_extraction_parsing"
    )
    assert upstream["duration_ms"] >= 0
    assert parsing["duration_ms"] >= 0
    assert parsing["candidate_count"] == 1
    assert parsing["finish_reason"] == "STOP"
    assert parsing["parts_count"] == 1
    assert parsing["has_text_part"] is True
    shape = next(
        fields
        for event, fields in events
        if event == "gemini_resume_extraction_shape"
    )
    assert shape["skills_count"] == 2
    assert shape["experience_count"] == 1
    assert shape["meaningful_experience_count"] == 1
    assert shape["projects_count"] == 1
    assert shape["extraction_shape"] == "normal"
    assert set(shape) == {
        "operation",
        "outcome",
        "skills_count",
        "tools_count",
        "certifications_count",
        "achievements_count",
        "responsibilities_count",
        "domain_expertise_count",
        "leadership_experience_count",
        "education_count",
        "experience_count",
        "projects_count",
        "meaningful_experience_count",
        "extraction_shape",
    }


def test_competency_only_extraction_is_classified_as_sparse(monkeypatch):
    events = []
    model = Mock()
    model.generate_content.return_value = SimpleNamespace(text=json.dumps({
        "name": "Synthetic Candidate",
        "skills": ["Stakeholder management"],
    }))
    monkeypatch.setattr(extraction_service, "model", model)
    monkeypatch.setattr(
        extraction_service,
        "emit_event",
        lambda event, **fields: events.append((event, fields)),
    )

    extraction_service.extract_resume_data("Synthetic resume")

    shape = next(
        fields
        for event, fields in events
        if event == "gemini_resume_extraction_shape"
    )
    assert shape["extraction_shape"] == "sparse"
    assert shape["skills_count"] == 1
    assert shape["meaningful_experience_count"] == 0


def test_retry_diagnostic_contains_only_safe_attempt_metadata(monkeypatch):
    events = []
    retry_state = {"attempt_number": 1}
    monkeypatch.setattr(
        extraction_service,
        "emit_event",
        lambda event, **fields: events.append((event, fields)),
    )
    retry_policy = extraction_service._extraction_retry_policy(retry_state)

    retry_policy._on_error(
        google_exceptions.ServiceUnavailable("PRIVATE PROVIDER DETAIL")
    )

    assert retry_state["attempt_number"] == 2
    assert events[0][1]["attempt_number"] == 1
    assert events[0][1]["next_attempt_number"] == 2
    assert events[0][1]["error_category"] == "ServiceUnavailable"
    assert "PRIVATE PROVIDER DETAIL" not in repr(events)


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
