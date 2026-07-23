from fastapi import APIRouter

from app.models.rag_model import (
    RagRequest,
    RagResponse
)

from app.services.rag_service import ask_resume


router = APIRouter(
    prefix="/rag",
    tags=["RAG"]
)


@router.post(
    "/",
    response_model=RagResponse
)
def rag(request: RagRequest):

    return ask_resume(
        request.question
    )