from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_staff_user
from app.database.database import get_db
from app.models.rag_evaluation_model import (
    RAGEvaluationFeedbackRequest,
    RAGEvaluationFeedbackResponse
)
from app.services import rag_evaluation_service


router = APIRouter(
    prefix="/rag-evaluations",
    tags=["RAG Evaluations"]
)


@router.patch(
    "/{evaluation_id:int}/feedback",
    dependencies=[
        Depends(get_current_staff_user)
    ],
    response_model=RAGEvaluationFeedbackResponse,
    summary="Add human feedback to a RAG evaluation"
)
def update_rag_evaluation_feedback(
    evaluation_id: int,
    feedback: RAGEvaluationFeedbackRequest,
    db: Session = Depends(get_db)
):

    return (
        rag_evaluation_service
        .update_evaluation_feedback(
            db,
            evaluation_id,
            feedback
        )
    )
