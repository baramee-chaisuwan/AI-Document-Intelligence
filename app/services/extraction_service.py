import json
import google.generativeai as genai
from app.core.config import GEMINI_API_KEY

genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel("gemini-2.5-flash")

def extract_resume_data(text):

    prompt = f"""
    Extract information from this resume.

    Return JSON only.

    {{
        "name": "",
        "skills": [],
        "education": [],
        "experience": []
    }}

    Resume:

    {text}
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