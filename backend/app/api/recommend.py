from fastapi import (
    APIRouter,
    Depends
)

from app.api.dependencies import (
    get_current_staff_user
)
from app.models.rag_model import (
    RagRequest,
    RecommendationResponse
)


router = APIRouter(
    prefix="/recommend",
    tags=["Recommendation"]
)


def ask_recommendation(
    question: str
):

    from app.services.rag_service import (
        ask_recommendation as service
    )

    return service(
        question
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
    request: RagRequest
):
    """
    Compare indexed candidates against a job requirement
    and return the best-supported recommendation.
    """

    return ask_recommendation(
        request.question
    )
