import logging
import threading

from langchain_google_genai import (
    ChatGoogleGenerativeAI
)

from app.core.config import GEMINI_API_KEY
from app.models.rag_model import (
    RecommendationResponse
)
from app.rag.prompt import (
    assistant_prompt,
    recommendation_prompt,
    resume_summary_prompt
)


logger = logging.getLogger(__name__)


MODEL_NAME = "gemini-2.5-flash"


llm = None
structured_llm = None

llm_lock = threading.Lock()
structured_llm_lock = threading.Lock()


def get_llm():

    global llm

    if llm is None:

        with llm_lock:

            if llm is None:

                if not GEMINI_API_KEY:

                    raise RuntimeError(
                        "GEMINI_API_KEY is not configured"
                    )

                try:

                    llm = ChatGoogleGenerativeAI(
                        model=MODEL_NAME,
                        temperature=0,
                        google_api_key=GEMINI_API_KEY
                    )

                except Exception as error:

                    logger.exception(
                        "Gemini LLM could not be initialized"
                    )

                    raise RuntimeError(
                        "Gemini LLM is unavailable"
                    ) from error

    return llm


def get_structured_llm():

    global structured_llm

    if structured_llm is None:

        with structured_llm_lock:

            if structured_llm is None:

                try:

                    structured_llm = (
                        get_llm()
                        .with_structured_output(
                            RecommendationResponse
                        )
                    )

                except Exception as error:

                    logger.exception(
                        "Structured Gemini LLM "
                        "could not be initialized"
                    )

                    raise RuntimeError(
                        "Structured Gemini LLM "
                        "is unavailable"
                    ) from error

    return structured_llm


def get_resume_summary_chain():

    return (
        resume_summary_prompt
        | get_llm()
    )


def get_assistant_chain():

    return (
        assistant_prompt
        | get_llm()
    )


def get_recommendation_chain():

    return (
        recommendation_prompt
        | get_structured_llm()
    )