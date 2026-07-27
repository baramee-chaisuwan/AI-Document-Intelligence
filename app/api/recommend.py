from fastapi import APIRouter

from app.models.rag_model import (
    RagRequest,
    RecommendationResponse
)


router = APIRouter(
    prefix="/recommend",
    tags=["Recommendation"]
)


@router.post(
    "/",
    response_model=RecommendationResponse
)
def recommend(request: RagRequest):

    from app.services.rag_service import ask_recommendation

    return ask_recommendation(
        request.question
    )