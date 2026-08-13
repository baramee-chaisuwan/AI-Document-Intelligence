import json
import logging
import re
import google.generativeai as genai

from app.core.config import GEMINI_API_KEY
from app.services.observability_service import observe_operation

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


STRING_ARRAY_SCHEMA = {
    "type": "ARRAY",
    "items": {"type": "STRING"},
}


RESUME_RESPONSE_SCHEMA = {
    "type": "OBJECT",
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


def response_text_candidates(response):
    """Return response text variants without logging resume content."""

    candidates = []

    try:
        direct_text = response.text
    except (AttributeError, ValueError):
        direct_text = None

    if isinstance(direct_text, str) and direct_text.strip():
        candidates.append(direct_text)

    parts = []

    try:
        parts.extend(response.parts or [])
    except (AttributeError, ValueError, TypeError):
        pass

    try:
        response_candidates = getattr(response, "candidates", [])
    except (AttributeError, ValueError):
        response_candidates = []

    try:
        response_candidates = list(response_candidates or [])
    except TypeError:
        response_candidates = []

    for candidate in response_candidates:
        content = getattr(candidate, "content", None)
        content_parts = getattr(content, "parts", [])
        try:
            parts.extend(content_parts or [])
        except TypeError:
            continue

    part_texts = []

    for part in parts:
        try:
            text = getattr(part, "text", None)
        except (AttributeError, ValueError):
            continue
        if isinstance(text, str) and text.strip():
            part_texts.append(text)

    candidates.extend(part_texts)

    if len(part_texts) > 1:
        candidates.append("".join(part_texts))

    return list(dict.fromkeys(candidates))


def parse_resume_response(response):
    """Parse strict or harmlessly wrapped JSON from a Gemini response."""

    decoder = json.JSONDecoder()

    for response_text in response_text_candidates(response):
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
        "Resume extraction returned invalid JSON"
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
- Extract evidence-supported professional competencies in skills.
- Extract tools and technologies in tools, regardless of profession.
- Preserve certifications, licenses, measurable achievements,
  responsibilities, domain expertise, and leadership experience.
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

            response = model.generate_content(
                prompt,
                generation_config={
                    "temperature": 0,
                    "response_mime_type": (
                        "application/json"
                    ),
                    "response_schema": RESUME_RESPONSE_SCHEMA,
                }
            )

            if not response:

                raise ValueError(
                    "Gemini returned an empty response"
                )

            parsed = parse_resume_response(response)

            return normalize_resume_data(
                parsed
            )

    except ResumeExtractionError:
        raise

    except Exception as error:

        raise ResumeExtractionError(
            "Resume extraction service failed"
        ) from error
