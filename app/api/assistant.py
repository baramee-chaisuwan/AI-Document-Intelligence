from fastapi import APIRouter

from app.models.assistant_model import (
    AssistantRequest,
    AssistantResponse
)


router = APIRouter(
    prefix="/assistant",
    tags=["AI HR Assistant"]
)


@router.post(
    "/",
    response_model=AssistantResponse
)
def assistant(request: AssistantRequest):

    from app.services.assistant_service import ask_assistant

    answer = ask_assistant(
        request.question
    )

    return AssistantResponse(
        answer=answer
    )