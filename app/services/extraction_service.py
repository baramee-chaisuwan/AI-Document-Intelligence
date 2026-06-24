import json
import google.generativeai as genai
from app.core.config import GEMINI_API_KEY

genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel("gemini-2.5-flash")

def extract_resume_data(text):

    prompt = f"""
    Extract information from this resume.

    Place spoken languages in "languages".
    Do not include languages in "skills".

    Return JSON only matching exactly this schema:

    {{
        "name": "",
        "skills": [],
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
        ]
    }}

    Resume:

    {text}
    """

    try:

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

    except Exception as e:

        print("EXTRACTION ERROR:", e)

        if "429" in str(e):
            print("RATE LIMIT DETECTED")

        if "API key" in str(e):
            print("INVALID API KEY")

        return {
            "name": "Unknown",
            "skills": [],
            "languages": [],
            "education": [],
            "experience": []
        }