from fastapi import APIRouter

from app.models.assistant_model import (
    AssistantRequest,
    AssistantResponse
)

from app.services.assistant_service import ask_assistant

router = APIRouter(
    prefix="/assistant",
    tags=["AI HR Assistant"]
)


@router.post(
    "/",
    response_model=AssistantResponse
)
def assistant(request: AssistantRequest):

    answer = ask_assistant(request.question)

    return AssistantResponse(
        answer=answer
    )