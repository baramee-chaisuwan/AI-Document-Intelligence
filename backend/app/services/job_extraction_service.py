import json
import logging

from app.models.job_model import JobRequirements
from app.services.gemini_service import get_model


logger = logging.getLogger(__name__)


REQUIREMENT_FIELDS = (
    "required_skills",
    "preferred_skills",
    "experience_requirements",
    "responsibilities"
)


class JobRequirementExtractionError(RuntimeError):
    """Raised when structured Job requirements cannot be produced."""


def extract_job_requirements(
    description: str
) -> dict[str, list[str]]:

    if (
        not isinstance(description, str)
        or not description.strip()
    ):
        raise JobRequirementExtractionError(
            "Job description is required"
        )

    prompt = f"""
You are an ATS job-description parser.

Extract only requirements explicitly supported by the job description.

Rules:
- Return only valid JSON.
- Do not include markdown or explanations.
- Do not invent or infer unstated requirements.
- Preserve concrete skills, experience requirements, and responsibilities.
- Use an empty array when a category is missing.
- Return exactly these four fields:

{{
    "required_skills": [],
    "preferred_skills": [],
    "experience_requirements": [],
    "responsibilities": []
}}

Job description begins below.

<job_description>
{description.strip()}
</job_description>
"""

    try:
        response = get_model().generate_content(
            prompt,
            generation_config={
                "temperature": 0,
                "response_mime_type": (
                    "application/json"
                )
            }
        )

        if (
            not response
            or not response.text
            or not response.text.strip()
        ):
            raise JobRequirementExtractionError(
                "Gemini returned an empty response"
            )

        parsed = json.loads(response.text)

        return normalize_job_requirements(parsed)

    except JobRequirementExtractionError:
        raise

    except (
        json.JSONDecodeError,
        TypeError,
        ValueError
    ) as error:
        logger.warning(
            "Gemini returned invalid Job requirements"
        )
        raise JobRequirementExtractionError(
            "Job requirements were invalid"
        ) from error

    except Exception as error:
        logger.exception(
            "Job requirement extraction failed"
        )
        raise JobRequirementExtractionError(
            "Job requirement extraction is unavailable"
        ) from error


def normalize_job_requirements(
    parsed
) -> dict[str, list[str]]:

    if not isinstance(parsed, dict):
        raise ValueError(
            "Job requirements must be an object"
        )

    normalized = {
        field: _normalize_requirement_list(
            parsed.get(field),
            field
        )
        for field in REQUIREMENT_FIELDS
    }

    return JobRequirements(
        **normalized
    ).model_dump()


def _normalize_requirement_list(
    value,
    field: str
) -> list[str]:

    if value is None:
        return []

    if not isinstance(value, list):
        raise ValueError(
            f"{field} must be a list"
        )

    normalized_items = []
    seen = set()

    for item in value:
        if not isinstance(item, str):
            raise ValueError(
                f"{field} items must be strings"
            )

        normalized_item = " ".join(
            item.split()
        )

        if not normalized_item:
            continue

        comparison_key = (
            normalized_item.casefold()
        )

        if comparison_key in seen:
            continue

        seen.add(comparison_key)
        normalized_items.append(
            normalized_item
        )

    return normalized_items
