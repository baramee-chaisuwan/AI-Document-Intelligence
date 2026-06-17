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
    You are an AI document analyst.

    Summarize the following document and provide:

    1. Main Purpose
    2. Key Skills
    3. Experience
    4. Education
    5. Important Highlights
    6. Summary

    Document:

    {text}
    """

    response = model.generate_content(prompt)

    return response.text