import google.generativeai as genai
from app.core.config import GEMINI_API_KEY
from app.services.observability_service import observe_operation

model = None


def get_model():
    global model

    if model is None:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-2.5-flash")

    return model


def summarize_document(text):

    prompt = f"""
You are an ATS resume expert.

Summarize in 3–5 sentences.

RULES:
- max 100 words
- no bullets
- no markdown
- plain text only
- summarize the most relevant competencies, experience,
  responsibilities, achievements, tools, certifications,
  leadership, and domain expertise supported by the resume
- mention projects only when they are material to the candidate's evidence

Resume:
{text}
"""

    try:
        with observe_operation("gemini_resume_summarization"):
            response = get_model().generate_content(prompt)
            return response.text.strip()

    except Exception:
        return "Summary generation failed"
