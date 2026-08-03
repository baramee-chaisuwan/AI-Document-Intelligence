from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from app.api.dependencies import (
    get_current_staff_user
)
from app.models.assistant_model import (
    AssistantRequest,
    AssistantResponse
)


router = APIRouter(
    prefix="/assistant",
    tags=["AI HR Assistant"]
)


def ask_assistant(
    question: str
):

    from app.services.assistant_service import (
        ask_assistant as service
    )

    return service(question)


@router.post(
    "/",
    dependencies=[
        Depends(get_current_staff_user)
    ],
    response_model=AssistantResponse
)
def assistant_chat(
    request: AssistantRequest
):
    """
    Ask the AI HR assistant about indexed resumes.
    """

    try:

        answer = ask_assistant(
            request.question
        )

    except Exception:

        raise HTTPException(
            status_code=500,
            detail="Assistant is currently unavailable."
        )

    return AssistantResponse(
        answer=answer
    )
