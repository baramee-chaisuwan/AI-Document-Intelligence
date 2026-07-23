from fastapi import APIRouter

from app.models.rag_model import (RagRequest,RecommendationResponse)

from app.services.rag_service import ask_recommendation


router = APIRouter(
    prefix="/recommend",
    tags=["Recommendation"]
)


@router.post(
    "/",
    response_model=RecommendationResponse
)
def recommend(request: RagRequest):

    return ask_recommendation(
        request.question
    )