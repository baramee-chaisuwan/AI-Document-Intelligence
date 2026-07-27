from fastapi import APIRouter

from app.models.assistant_model import (
    AssistantRequest,
    AssistantResponse
)

router = APIRouter(
    prefix="/assistant",
    tags=["AI HR Assistant"]
)

def ask_assistant(question: str):
    from app.services.assistant_service import ask_assistant as service

    return service(question)

@router.post(
    "/",
    response_model=AssistantResponse
)
def assistant(request: AssistantRequest):

    answer = ask_assistant(
        request.question
    )

    return AssistantResponse(
        answer=answer
    )