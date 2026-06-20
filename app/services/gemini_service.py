import google.generativeai as genai

from app.core.config import GEMINI_API_KEY

genai.configure(
    api_key=GEMINI_API_KEY
)

model = genai.GenerativeModel(
    "gemini-2.5-flash"
)


def summarize_document(text):

    prompt = f"""
    Summarize this resume in 3-5 sentences only.

    Focus on:
    - Candidate background
    - Main skills
    - Most relevant experience

    Rules:
    - Maximum 100 words
    - No bullet points
    - No headings
    - No markdown
    - Return plain text only

    Resume:

    {text}
    """

    response = model.generate_content(prompt)

    return response.text.strip()