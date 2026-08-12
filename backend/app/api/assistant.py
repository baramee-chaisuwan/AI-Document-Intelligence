from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)
from sqlalchemy.orm import Session

from app.api.dependencies import (
    get_current_staff_user
)
from app.models.assistant_model import (
    AssistantRequest,
    AssistantResponse
)
from app.database.database import get_db


router = APIRouter(
    prefix="/assistant",
    tags=["AI HR Assistant"]
)


def ask_assistant(
    question: str,
    db: Session
):

    from app.services.assistant_service import (
        ask_assistant as service
    )

    return service(question, db=db)


@router.post(
    "/",
    dependencies=[
        Depends(get_current_staff_user)
    ],
    response_model=AssistantResponse
)
def assistant_chat(
    request: AssistantRequest,
    db: Session = Depends(get_db)
):
    """
    Ask the AI HR assistant about indexed resumes.
    """

    try:

        answer = ask_assistant(
            request.question,
            db
        )

    except Exception:

        raise HTTPException(
            status_code=500,
            detail="Assistant is currently unavailable."
        )

    return AssistantResponse(
        answer=answer
    )
