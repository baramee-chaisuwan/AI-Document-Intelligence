from fastapi import APIRouter
from pydantic import BaseModel

from app.services.langchain_service import (
    summarize_resume_with_langchain
)

router = APIRouter(
    prefix="/langchain",
    tags=["LangChain Demo"]
)


class ResumeRequest(BaseModel):
    resume: str


@router.post("/summary")
def summary(
    request: ResumeRequest
):

    return {
        "summary":
        summarize_resume_with_langchain(
            request.resume
        )
    }