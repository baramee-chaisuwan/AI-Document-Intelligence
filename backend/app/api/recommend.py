from fastapi import (
    APIRouter,
    Depends
)
from sqlalchemy.orm import Session

from app.api.dependencies import (
    get_current_staff_user
)
from app.models.rag_model import (
    RagRequest,
    RecommendationResponse
)
from app.database.database import get_db


router = APIRouter(
    prefix="/recommend",
    tags=["Recommendation"]
)


def ask_recommendation(
    question: str,
    db: Session
):

    from app.services.rag_service import (
        ask_recommendation as service
    )

    return service(
        question,
        db=db
    )


@router.post(
    "/",
    dependencies=[
        Depends(get_current_staff_user)
    ],
    response_model=RecommendationResponse,
    summary="Recommend the best matching candidate"
)
def recommend_candidate(
    request: RagRequest,
    db: Session = Depends(get_db)
):
    """
    Compare indexed candidates against a job requirement
    and return the best-supported recommendation.
    """

    return ask_recommendation(
        request.question,
        db
    )
