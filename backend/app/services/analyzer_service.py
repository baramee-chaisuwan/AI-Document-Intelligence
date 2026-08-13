import json
import logging
import re
from datetime import datetime

import google.generativeai as genai

from app.core.config import GEMINI_API_KEY
from app.services.scoring_service import calculate_skill_score
from app.services.observability_service import (
    observe_operation,
    observed_operation
)


logger = logging.getLogger(__name__)


genai.configure(
    api_key=GEMINI_API_KEY
)

model = genai.GenerativeModel(
    "gemini-2.5-flash"
)


RULE_WEIGHT = 0.8
AI_WEIGHT = 0.2


PRESENT_DATE_VALUES = [
    "present",
    "current",
    "now",
    "ปัจจุบัน"
]


DATE_FORMATS = [
    "%Y-%m-%d",
    "%Y-%m",
    "%m/%Y",
    "%Y",
    "%b %Y",
    "%B %Y",
    "%b, %Y",
    "%B, %Y"
]


def safe_get(
    data,
    key
):

    if not isinstance(
        data,
        dict
    ):
        return []

    value = data.get(
        key,
        []
    )

    if not isinstance(
        value,
        list
    ):
        return []

    return value


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

        text = str(
            item or ""
        ).strip()

        if text:
            result.append(
                text
            )

    return result


def is_intern(
    exp
):

    if not isinstance(
        exp,
        dict
    ):
        return False

    title = str(
        exp.get(
            "title",
            ""
        ) or ""
    ).lower()

    company = str(
        exp.get(
            "company",
            ""
        ) or ""
    ).lower()

    internship_keywords = [
        "intern",
        "internship",
        "trainee",
        "co-op",
        "coop"
    ]

    for keyword in internship_keywords:

        if (
            keyword in title
            or keyword in company
        ):
            return True

    return False


def parse_date(
    value
):

    date_text = str(
        value or ""
    ).strip()

    if not date_text:
        return None

    if date_text.lower() in PRESENT_DATE_VALUES:
        return datetime.now()

    date_text = re.sub(
        r"\s+",
        " ",
        date_text
    )

    for date_format in DATE_FORMATS:

        try:

            return datetime.strptime(
                date_text,
                date_format
            )

        except ValueError:

            continue

    year_match = re.search(
        r"\b(19|20)\d{2}\b",
        date_text
    )

    if year_match:

        try:

            return datetime(
                int(
                    year_match.group()
                ),
                1,
                1
            )

        except ValueError:

            return None

    return None


def calculate_month_difference(
    start_date,
    end_date
):

    if (
        start_date is None
        or end_date is None
    ):
        return 0

    if end_date < start_date:
        return 0

    months = (
        (end_date.year - start_date.year)
        * 12
    )

    months += (
        end_date.month
        - start_date.month
    )

    if end_date.day >= start_date.day:
        months += 1

    return max(
        months,
        0
    )


def calculate_experience_months(
    experiences
):

    total_months = 0

    for exp in experiences:

        if not isinstance(
            exp,
            dict
        ):
            continue

        if is_intern(
            exp
        ):
            continue

        start_date = parse_date(
            exp.get(
                "start_date"
            )
        )

        end_date = parse_date(
            exp.get(
                "end_date"
            )
        )

        total_months += (
            calculate_month_difference(
                start_date,
                end_date
            )
        )

    return total_months


def determine_candidate_level(
    experiences
):

    internships = 0

    for exp in experiences:

        if is_intern(
            exp
        ):
            internships += 1

    experience_months = (
        calculate_experience_months(
            experiences
        )
    )

    experience_years = (
        experience_months / 12
    )

    if experience_years >= 5:
        return "Senior"

    if experience_years >= 2:
        return "Mid-Level"

    if (
        experience_months > 0
        or internships >= 1
    ):
        return "Junior"

    return "Entry-Level"


def clean_recommended_roles(
    roles
):

    if not isinstance(
        roles,
        list
    ):
        return []

    clean_roles = []
    seen = set()

    for role in roles:

        role = str(
            role or ""
        ).strip()

        if (
            not role
            or len(role) > 100
        ):
            continue

        if "intern" in role.lower():
            continue

        comparison_key = role.casefold()

        if comparison_key in seen:
            continue

        seen.add(comparison_key)
        clean_roles.append(role)

        if len(clean_roles) >= 5:
            break


    return clean_roles


def normalize_ai_score(
    value,
    fallback_score
):

    try:

        ai_score = float(
            value
        )

    except (
        TypeError,
        ValueError
    ):

        ai_score = fallback_score

    ai_score = max(
        0,
        min(
            ai_score,
            100
        )
    )

    return round(
        ai_score
    )


@observed_operation("resume_analysis_scoring")
def analyze_resume(
    resume_data
):

    if not isinstance(
        resume_data,
        dict
    ):

        raise ValueError(
            "Resume data must be an object"
        )

    score_data = calculate_skill_score(
        resume_data
    )

    rule_score = score_data.get(
        "skill_score",
        0
    )

    experiences = safe_get(
        resume_data,
        "experience"
    )

    projects = safe_get(
        resume_data,
        "projects"
    )

    candidate_level = (
        determine_candidate_level(
            experiences
        )
    )

    prompt = f"""
You are an experienced recruiter reviewing a candidate resume.

Return only valid JSON.

Rules:

- Recommend only roles directly supported by the resume evidence.
- Infer role names from the candidate's documented competencies,
  experience, responsibilities, achievements, tools, certifications,
  leadership, and domain expertise.
- Do not recommend internship roles.
- Do not invent unsupported job titles or professional evidence.
- Base all findings only on the provided resume data.
- Keep strengths and improvement areas concise.
- Evaluate evidence without favoring a particular professional domain.
- ai_score must be an integer from 0 to 100.
- Do not determine candidate seniority. The application calculates it.

Return exactly this JSON structure:

{{
    "ai_score": 0,
    "recommended_roles": [],
    "strengths": [],
    "improvement_areas": []
}}

Resume data:

<resume_data>
{json.dumps(resume_data, ensure_ascii=False)}
</resume_data>
"""

    try:

        with observe_operation("gemini_resume_analysis"):

            response = model.generate_content(
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

                raise ValueError(
                    "Gemini returned an empty response"
                )

            analysis = json.loads(
                response.text
            )

            if not isinstance(
                analysis,
                dict
            ):

                raise ValueError(
                    "Gemini analysis must be an object"
                )

        ai_score = normalize_ai_score(
            analysis.get(
                "ai_score"
            ),
            rule_score
        )

        skill_score = round(
            (
                rule_score
                * RULE_WEIGHT
            )
            +
            (
                ai_score
                * AI_WEIGHT
            )
        )

        return {
            "candidate_level": candidate_level,
            "rule_score": rule_score,
            "ai_score": ai_score,
            "skill_score": skill_score,
            "score_breakdown": score_data.get(
                "score_breakdown",
                {}
            ),
            "project_count": len(
                projects
            ),
            "ai_status": "success",
            "recommended_roles": (
                clean_recommended_roles(
                    analysis.get(
                        "recommended_roles"
                    )
                )
            ),
            "strengths": normalize_string_list(
                analysis.get(
                    "strengths"
                )
            ),
            "improvement_areas": (
                normalize_string_list(
                    analysis.get(
                        "improvement_areas"
                    )
                )
            )
        }

    except Exception as error:

        return {
            "candidate_level": candidate_level,
            "rule_score": rule_score,
            "ai_score": 0,
            "skill_score": rule_score,
            "score_breakdown": score_data.get(
                "score_breakdown",
                {}
            ),
            "project_count": len(
                projects
            ),
            "ai_status": "fallback",
            "recommended_roles": [],
            "strengths": [],
            "improvement_areas": [],
            "ai_error": str(
                error
            )
        }
