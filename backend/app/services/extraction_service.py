import json
import logging
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

            parsed = json.loads(
                response.text
            )

            return normalize_resume_data(
                parsed
            )

    except json.JSONDecodeError as error:

        raise RuntimeError(
            "Resume extraction returned invalid JSON"
        ) from error

    except Exception as error:

        raise RuntimeError(
            "Resume extraction service failed"
        ) from error
