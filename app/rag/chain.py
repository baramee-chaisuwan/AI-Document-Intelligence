from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

from app.models.rag_model import RecommendationResponse
from app.rag.prompt import (
    assistant_prompt,
    recommendation_prompt,
    resume_summary_prompt,
)

load_dotenv()


llm = None
structured_llm = None


def get_llm():

    global llm

    if llm is None:
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0,
        )

    return llm


def get_structured_llm():

    global structured_llm

    if structured_llm is None:
        structured_llm = get_llm().with_structured_output(
            RecommendationResponse
        )

    return structured_llm


def get_resume_summary_chain():

    return resume_summary_prompt | get_llm()


def get_assistant_chain():

    return assistant_prompt | get_llm()


def get_recommendation_chain():

    return recommendation_prompt | get_structured_llm()