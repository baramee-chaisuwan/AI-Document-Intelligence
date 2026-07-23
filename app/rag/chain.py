from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

from app.rag.prompt import (
    resume_summary_prompt,
    assistant_prompt,
    recommendation_prompt
)

from app.models.rag_model import RecommendationResponse


load_dotenv()


llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0
)


recommendation_llm = llm.with_structured_output(
    RecommendationResponse
)


resume_summary_chain = resume_summary_prompt | llm

assistant_chain = assistant_prompt | llm

recommendation_chain = (recommendation_prompt | recommendation_llm)