import google.generativeai as genai
from app.core.config import GEMINI_API_KEY

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")


def summarize_document(text):

    prompt = f"""
You are an ATS resume expert.

Summarize in 3–5 sentences.

RULES:
- max 100 words
- no bullets
- no markdown
- plain text only
- MUST mention projects if present

Resume:
{text}
"""

    try:
        response = model.generate_content(prompt)
        return response.text.strip()

    except Exception as e:
        print("SUMMARY ERROR:", e)
        return "Summary generation failed"