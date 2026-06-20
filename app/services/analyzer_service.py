import json
import google.generativeai as genai

from app.core.config import GEMINI_API_KEY

genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel("gemini-2.5-flash")


def analyze_resume(resume_data):

    prompt = f"""
    Analyze this candidate resume.

    Return JSON only.

    Rules:
    - candidate_level = Entry-Level, Junior, Mid-Level, Senior
    - skill_score = 0-100
    - recommended_roles = maximum 3 items
    - strengths = maximum 3 items
    - improvement_areas = maximum 3 items
    - Keep every item short (1 sentence)

    {{
        "candidate_level": "",
        "skill_score": 0,
        "recommended_roles": [],
        "strengths": [],
        "improvement_areas": []
    }}

    Resume Data:

    {resume_data}
    """

    response = model.generate_content(prompt)

    result = response.text

    result = result.replace(
        "```json",
        ""
    )

    result = result.replace(
        "```",
        ""
    )

    result = result.strip()

    return json.loads(result)