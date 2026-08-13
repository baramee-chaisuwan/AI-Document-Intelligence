import json
import logging
import re
import time
import google.generativeai as genai
from google.api_core import exceptions as google_exceptions
from google.api_core.retry import Retry, if_exception_type

from app.core.config import GEMINI_API_KEY
from app.services.observability_service import (
    duration_ms,
    emit_event,
    observe_operation,
)

logger = logging.getLogger(__name__)

genai.configure(
    api_key=GEMINI_API_KEY
)


model = genai.GenerativeModel(
    "gemini-2.5-flash"
)


EMPTY_RESUME_DATA = {
    "name": "",
    "skills": [],
    "tools": [],
    "certifications": [],
    "achievements": [],
    "responsibilities": [],
    "domain_expertise": [],
    "leadership_experience": [],
    "languages": [],
    "education": [],
    "experience": [],
    "projects": []
}


class ResumeExtractionError(RuntimeError):
    """Raised when Gemini does not return a usable resume object."""

    def __init__(
        self,
        message,
        *,
        category="resume_extraction_failure",
        safe_metadata=None,
    ):
        super().__init__(message)
        self.category = category
        self.safe_metadata = safe_metadata or {}


GEMINI_EXTRACTION_RPC_TIMEOUT_SECONDS = 60
GEMINI_EXTRACTION_RETRY_TIMEOUT_SECONDS = 90
GEMINI_EXTRACTION_MAXIMUM_BACKOFF_SECONDS = 8


STRING_ARRAY_SCHEMA = {
    "type": "ARRAY",
    "items": {"type": "STRING"},
}


RESUME_RESPONSE_SCHEMA = {
    "type": "OBJECT",
    "required": [
        "name",
        "skills",
        "tools",
        "certifications",
        "achievements",
        "responsibilities",
        "domain_expertise",
        "leadership_experience",
        "languages",
        "education",
        "experience",
        "projects",
    ],
    "properties": {
        "name": {"type": "STRING"},
        "skills": STRING_ARRAY_SCHEMA,
        "tools": STRING_ARRAY_SCHEMA,
        "certifications": STRING_ARRAY_SCHEMA,
        "achievements": STRING_ARRAY_SCHEMA,
        "responsibilities": STRING_ARRAY_SCHEMA,
        "domain_expertise": STRING_ARRAY_SCHEMA,
        "leadership_experience": STRING_ARRAY_SCHEMA,
        "languages": STRING_ARRAY_SCHEMA,
        "education": {
            "type": "ARRAY",
            "items": {
                "type": "OBJECT",
                "required": [
                    "institution",
                    "degree",
                    "start_date",
                    "end_date",
                ],
                "properties": {
                    "institution": {"type": "STRING"},
                    "degree": {"type": "STRING"},
                    "start_date": {"type": "STRING"},
                    "end_date": {"type": "STRING"},
                },
            },
        },
        "experience": {
            "type": "ARRAY",
            "items": {
                "type": "OBJECT",
                "required": [
                    "title",
                    "company",
                    "start_date",
                    "end_date",
                    "description",
                ],
                "properties": {
                    "title": {"type": "STRING"},
                    "company": {"type": "STRING"},
                    "start_date": {"type": "STRING"},
                    "end_date": {"type": "STRING"},
                    "description": STRING_ARRAY_SCHEMA,
                },
            },
        },
        "projects": {
            "type": "ARRAY",
            "items": {
                "type": "OBJECT",
                "required": [
                    "name",
                    "description",
                    "technologies",
                ],
                "properties": {
                    "name": {"type": "STRING"},
                    "description": STRING_ARRAY_SCHEMA,
                    "technologies": STRING_ARRAY_SCHEMA,
                },
            },
        },
    },
}


JSON_FENCE_PATTERN = re.compile(
    r"^\s*```(?:json)?\s*(.*?)\s*```\s*$",
    re.IGNORECASE | re.DOTALL,
)


def inspect_resume_response(response):
    """Inspect response shape and return text privately plus safe metadata."""

    response_text_accessible = False
    direct_text = None

    try:
        direct_text = response.text
        response_text_accessible = True
    except (AttributeError, ValueError):
        pass

    candidates_attribute_available = True

    try:
        response_candidates = getattr(response, "candidates")
    except (AttributeError, ValueError):
        candidates_attribute_available = False
        response_candidates = []

    try:
        response_candidates = list(response_candidates or [])
    except TypeError:
        candidates_attribute_available = False
        response_candidates = []

    prompt_block_reason = _prompt_block_reason(response)
    metadata = {
        "candidate_count": len(response_candidates),
        "finish_reason": None,
        "parts_count": 0,
        "has_text_part": False,
        "response_text_accessible": response_text_accessible,
        "prompt_block_reason": prompt_block_reason,
        "schema_enabled": True,
        **_usage_metadata(response),
    }
    model_version = getattr(response, "model_version", None)
    if isinstance(model_version, str) and model_version:
        metadata["model_version"] = model_version

    if candidates_attribute_available and not response_candidates:
        category = (
            "prompt_blocked"
            if prompt_block_reason
            and prompt_block_reason
            != "BLOCK_REASON_UNSPECIFIED"
            else "empty_candidates"
        )
        raise ResumeExtractionError(
            "Gemini returned no resume candidates",
            category=category,
            safe_metadata=metadata,
        )

    text_candidates = []
    if isinstance(direct_text, str) and direct_text.strip():
        text_candidates.append(direct_text)

    parts = []
    finish_reasons = []

    if not candidates_attribute_available:
        try:
            parts.extend(response.parts or [])
        except (AttributeError, TypeError, ValueError):
            pass

    for candidate in response_candidates:
        finish_reasons.append(
            _enum_name(
                getattr(candidate, "finish_reason", None)
            )
        )
        content = getattr(candidate, "content", None)
        content_parts = getattr(content, "parts", [])
        try:
            parts.extend(content_parts or [])
        except TypeError:
            continue

    finish_reasons = [
        reason
        for reason in finish_reasons
        if reason
    ]
    metadata["finish_reason"] = (
        finish_reasons[0]
        if len(finish_reasons) == 1
        else finish_reasons or None
    )
    metadata["parts_count"] = len(parts)

    if response_candidates:
        finish_category = _finish_reason_category(
            finish_reasons
        )
        if finish_category:
            raise ResumeExtractionError(
                "Gemini stopped resume extraction before completion",
                category=finish_category,
                safe_metadata=metadata,
            )

        if not parts:
            raise ResumeExtractionError(
                "Gemini returned an empty resume candidate",
                category="empty_parts",
                safe_metadata=metadata,
            )

    part_texts = []

    for part in parts:
        try:
            text = getattr(part, "text", None)
        except (AttributeError, ValueError):
            continue

        if isinstance(text, str) and text.strip():
            part_texts.append(text)

    metadata["has_text_part"] = bool(part_texts)

    if response_candidates and not part_texts:
        raise ResumeExtractionError(
            "Gemini returned no textual resume content",
            category="no_text_parts",
            safe_metadata=metadata,
        )

    text_candidates.extend(part_texts)

    if len(part_texts) > 1:
        text_candidates.append("".join(part_texts))

    if not text_candidates:
        raise ResumeExtractionError(
            "Gemini returned no textual resume content",
            category="no_text_parts",
            safe_metadata=metadata,
        )

    return list(dict.fromkeys(text_candidates)), metadata


def parse_resume_response(response):
    """Parse strict or harmlessly wrapped JSON from a Gemini response."""

    decoder = json.JSONDecoder()
    response_texts, metadata = inspect_resume_response(response)

    for response_text in response_texts:
        stripped = response_text.strip()
        fenced = JSON_FENCE_PATTERN.match(stripped)
        variants = [stripped]

        if fenced:
            variants.insert(0, fenced.group(1).strip())

        for variant in variants:
            try:
                parsed = json.loads(variant)
            except json.JSONDecodeError:
                parsed = None

            if isinstance(parsed, dict):
                parsed = _unwrap_resume_object(parsed)
                if _is_resume_object(parsed):
                    return parsed

            for index, character in enumerate(variant):
                if character != "{":
                    continue

                try:
                    parsed, _ = decoder.raw_decode(variant[index:])
                except json.JSONDecodeError:
                    continue

                if isinstance(parsed, dict):
                    parsed = _unwrap_resume_object(parsed)
                    if _is_resume_object(parsed):
                        return parsed

    raise ResumeExtractionError(
        "Resume extraction returned invalid JSON",
        category="malformed_json",
        safe_metadata=metadata,
    )


def _finish_reason_category(finish_reasons):
    categories = {
        "MAX_TOKENS": "max_tokens",
        "SAFETY": "safety",
        "SPII": "spii",
        "RECITATION": "recitation",
    }

    for reason in finish_reasons:
        if reason in categories:
            return categories[reason]

        if reason != "STOP":
            return "non_success_finish_reason"

    return None


def _enum_name(value):
    if value is None:
        return None

    name = getattr(value, "name", None)
    if isinstance(name, str):
        return name

    text = str(value).strip()
    if "." in text:
        text = text.rsplit(".", 1)[-1]

    return text or None


def _prompt_block_reason(response):
    try:
        prompt_feedback = response.prompt_feedback
        block_reason = prompt_feedback.block_reason
    except (AttributeError, ValueError):
        return None

    return _enum_name(block_reason)


def _usage_metadata(response):
    try:
        usage = response.usage_metadata
    except (AttributeError, ValueError):
        return {}

    fields = (
        "prompt_token_count",
        "candidates_token_count",
        "total_token_count",
        "cached_content_token_count",
    )

    return {
        field: value
        for field in fields
        if isinstance((value := getattr(usage, field, None)), int)
    }


def _safe_candidate_count(response):
    try:
        return len(list(response.candidates or []))
    except (AttributeError, TypeError, ValueError):
        return None


def _extraction_retry_policy(retry_state):
    def on_error(error):
        emit_event(
            "gemini_resume_extraction_retry",
            operation="gemini_resume_extraction",
            outcome="retrying",
            attempt_number=retry_state["attempt_number"],
            next_attempt_number=retry_state["attempt_number"] + 1,
            error_category=type(error).__name__,
            schema_enabled=True,
        )
        retry_state["attempt_number"] += 1

    return Retry(
        predicate=if_exception_type(
            google_exceptions.ServiceUnavailable
        ),
        initial=1.0,
        maximum=GEMINI_EXTRACTION_MAXIMUM_BACKOFF_SECONDS,
        multiplier=2.0,
        timeout=GEMINI_EXTRACTION_RETRY_TIMEOUT_SECONDS,
        on_error=on_error,
    )


def _unwrap_resume_object(parsed):
    wrapper_keys = ("resume", "resume_data", "data", "result")

    if len(parsed) == 1:
        key = next(iter(parsed))
        value = parsed[key]
        if key in wrapper_keys and isinstance(value, dict):
            return value

    return parsed


def _is_resume_object(parsed):
    return bool(
        isinstance(parsed, dict)
        and set(parsed).intersection(EMPTY_RESUME_DATA)
    )


def normalize_string(
    value
):

    if value is None:
        return ""

    return str(value).strip()


def normalize_string_list(
    value
):

    if not isinstance(
        value,
        list
    ):
        return []


    result = []


    for item in value:

        normalized_item = (
            normalize_string(
                item
            )
        )


        if normalized_item:

            result.append(
                normalized_item
            )


    return result


def normalize_education(
    value
):

    if not isinstance(
        value,
        list
    ):
        return []


    education_list = []


    for item in value:

        if not isinstance(
            item,
            dict
        ):
            continue


        education_list.append({
            "institution": normalize_string(
                item.get(
                    "institution"
                )
            ),
            "degree": normalize_string(
                item.get(
                    "degree"
                )
            ),
            "start_date": normalize_string(
                item.get(
                    "start_date"
                )
            ),
            "end_date": normalize_string(
                item.get(
                    "end_date"
                )
            )
        })


    return education_list


def normalize_experience(
    value
):

    if not isinstance(
        value,
        list
    ):
        return []


    experience_list = []


    for item in value:

        if not isinstance(
            item,
            dict
        ):
            continue


        experience_list.append({
            "title": normalize_string(
                item.get(
                    "title"
                )
            ),
            "company": normalize_string(
                item.get(
                    "company"
                )
            ),
            "start_date": normalize_string(
                item.get(
                    "start_date"
                )
            ),
            "end_date": normalize_string(
                item.get(
                    "end_date"
                )
            ),
            "description": normalize_string_list(
                item.get(
                    "description"
                )
            )
        })


    return experience_list


def normalize_projects(
    value
):

    if not isinstance(
        value,
        list
    ):
        return []


    project_list = []


    for item in value:

        if not isinstance(
            item,
            dict
        ):
            continue


        project_list.append({
            "name": normalize_string(
                item.get(
                    "name"
                )
            ),
            "description": normalize_string_list(
                item.get(
                    "description"
                )
            ),
            "technologies": normalize_string_list(
                item.get(
                    "technologies"
                )
            )
        })


    return project_list


def normalize_resume_data(
    parsed
):

    if not isinstance(
        parsed,
        dict
    ):

        raise ValueError(
            "Resume extraction result must be an object"
        )


    return {
        "name": normalize_string(
            parsed.get(
                "name"
            )
        ),
        "skills": normalize_string_list(
            parsed.get(
                "skills"
            )
        ),
        "tools": normalize_string_list(
            parsed.get(
                "tools"
            )
        ),
        "certifications": normalize_string_list(
            parsed.get(
                "certifications"
            )
        ),
        "achievements": normalize_string_list(
            parsed.get(
                "achievements"
            )
        ),
        "responsibilities": normalize_string_list(
            parsed.get(
                "responsibilities"
            )
        ),
        "domain_expertise": normalize_string_list(
            parsed.get(
                "domain_expertise"
            )
        ),
        "leadership_experience": normalize_string_list(
            parsed.get(
                "leadership_experience"
            )
        ),
        "languages": normalize_string_list(
            parsed.get(
                "languages"
            )
        ),
        "education": normalize_education(
            parsed.get(
                "education"
            )
        ),
        "experience": normalize_experience(
            parsed.get(
                "experience"
            )
        ),
        "projects": normalize_projects(
            parsed.get(
                "projects"
            )
        )
    }


def extraction_shape_metadata(normalized):
    """Return privacy-safe counts describing normalized extraction shape."""

    list_fields = (
        "skills",
        "tools",
        "certifications",
        "achievements",
        "responsibilities",
        "domain_expertise",
        "leadership_experience",
        "education",
        "experience",
        "projects",
    )
    counts = {
        f"{field}_count": len(normalized.get(field, []))
        if isinstance(normalized.get(field), list)
        else 0
        for field in list_fields
    }
    meaningful_experience_count = sum(
        bool(
            item.get("title")
            or item.get("company")
            or item.get("description")
        )
        for item in normalized.get("experience", [])
        if isinstance(item, dict)
    )
    counts["meaningful_experience_count"] = (
        meaningful_experience_count
    )

    supporting_evidence_count = (
        meaningful_experience_count
        + counts["certifications_count"]
        + counts["achievements_count"]
        + counts["responsibilities_count"]
        + counts["leadership_experience_count"]
        + counts["education_count"]
        + counts["projects_count"]
    )
    counts["extraction_shape"] = (
        "sparse"
        if supporting_evidence_count == 0
        else "normal"
    )
    return counts


def extract_resume_data(
    text
):

    if not text or not text.strip():

        raise ValueError(
            "Resume text is empty"
        )


    prompt = f"""
You are an ATS resume parser.

Extract only information explicitly stated in the resume.

Rules:

- Return only valid JSON.
- Do not include markdown.
- Do not include explanations.
- Do not summarize or rewrite resume content.
- Do not invent missing information.
- Use an empty string or empty array when information is missing.
- Preserve every work experience and every relevant project.
- Preserve bullet points as separate array items.
- Keep each work or project bullet in its original description array even
  when the same evidence is also classified into a top-level array.
- Extract evidence-supported professional competencies in skills.
- Extract tools and technologies in tools, regardless of profession.
- Copy explicitly stated certifications and licenses into certifications.
- Copy quantified outcomes or other measurable achievements into
  achievements.
- Copy duties, ownership, and accountable work into responsibilities.
- Copy team leadership, mentoring, supervision, and organizational leadership
  into leadership_experience.
- Copy profession-specific knowledge areas into domain_expertise.
- Classification duplicates evidence; it must never remove that evidence from
  experience[].description or projects[].description.
- For example, keep "Reduced time-to-hire by 35%" in its experience
  description and also include it in achievements.
- Keep "Led a team of 5 recruiters" in its experience description and also
  include it in leadership_experience.
- Keep "Managed employee onboarding and policy compliance" in its experience
  description and also include it in responsibilities.
- Include explicitly listed credentials such as SHRM-CP, PMP, CPA, or CCNP in
  certifications.
- Apply these evidence rules equally to technical, operational, and business
  professions.
- Do not invent or infer evidence that is not explicitly stated.
- Do not force nontechnical evidence into a technology category.
- Extract spoken languages only in the languages field.

Return exactly this JSON structure:

{{
    "name": "",
    "skills": [],
    "tools": [],
    "certifications": [],
    "achievements": [],
    "responsibilities": [],
    "domain_expertise": [],
    "leadership_experience": [],
    "languages": [],
    "education": [
        {{
            "institution": "",
            "degree": "",
            "start_date": "",
            "end_date": ""
        }}
    ],
    "experience": [
        {{
            "title": "",
            "company": "",
            "start_date": "",
            "end_date": "",
            "description": []
        }}
    ],
    "projects": [
        {{
            "name": "",
            "description": [],
            "technologies": []
        }}
    ]
}}

Resume content begins below.

<resume>
{text}
</resume>
"""

    try:

        with observe_operation("gemini_resume_extraction"):

            retry_state = {
                "attempt_number": 1
            }
            upstream_started_at = time.perf_counter()

            try:
                response = model.generate_content(
                    prompt,
                    generation_config={
                        "temperature": 0,
                        "response_mime_type": (
                            "application/json"
                        ),
                        "response_schema": RESUME_RESPONSE_SCHEMA,
                    },
                    request_options={
                        "retry": _extraction_retry_policy(
                            retry_state
                        ),
                        "timeout": (
                            GEMINI_EXTRACTION_RPC_TIMEOUT_SECONDS
                        ),
                    },
                )
            except Exception as error:
                emit_event(
                    "gemini_resume_extraction_upstream",
                    severity="ERROR",
                    operation="gemini_resume_extraction",
                    outcome="failure",
                    duration_ms=duration_ms(
                        upstream_started_at
                    ),
                    attempt_number=(
                        retry_state["attempt_number"]
                    ),
                    error_category=type(error).__name__,
                    schema_enabled=True,
                )
                raise

            emit_event(
                "gemini_resume_extraction_upstream",
                operation="gemini_resume_extraction",
                outcome="success",
                duration_ms=duration_ms(
                    upstream_started_at
                ),
                attempt_number=retry_state["attempt_number"],
                candidate_count=_safe_candidate_count(
                    response
                ),
                schema_enabled=True,
            )

            parsing_started_at = time.perf_counter()

            try:
                if not response:
                    raise ResumeExtractionError(
                        "Gemini returned an empty response",
                        category="empty_response",
                        safe_metadata={
                            "candidate_count": 0,
                            "parts_count": 0,
                            "has_text_part": False,
                            "response_text_accessible": False,
                            "schema_enabled": True,
                        },
                    )

                parsed = parse_resume_response(response)
                normalized = normalize_resume_data(parsed)
                shape_metadata = extraction_shape_metadata(
                    normalized
                )
            except ResumeExtractionError as error:
                emit_event(
                    "gemini_resume_extraction_parsing",
                    severity="ERROR",
                    operation="gemini_resume_extraction",
                    outcome="failure",
                    duration_ms=duration_ms(
                        parsing_started_at
                    ),
                    response_category=error.category,
                    error_category=type(error).__name__,
                    **error.safe_metadata,
                )
                raise
            except Exception as error:
                emit_event(
                    "gemini_resume_extraction_parsing",
                    severity="ERROR",
                    operation="gemini_resume_extraction",
                    outcome="failure",
                    duration_ms=duration_ms(
                        parsing_started_at
                    ),
                    response_category="normalization_failure",
                    error_category=type(error).__name__,
                    schema_enabled=True,
                )
                raise

            _, response_metadata = inspect_resume_response(
                response
            )
            emit_event(
                "gemini_resume_extraction_parsing",
                operation="gemini_resume_extraction",
                outcome="success",
                duration_ms=duration_ms(
                    parsing_started_at
                ),
                response_category="valid_json",
                **response_metadata,
            )
            emit_event(
                "gemini_resume_extraction_shape",
                operation="gemini_resume_extraction",
                outcome="success",
                **shape_metadata,
            )

            return normalized

    except ResumeExtractionError:
        raise

    except Exception as error:

        raise ResumeExtractionError(
            "Resume extraction service failed",
            category="upstream_or_normalization_failure",
        ) from error
