from datetime import datetime

from sqlalchemy.orm import Session

from app.database.models import RAGEvaluation


def create_rag_evaluation(
    db: Session,
    evaluation: RAGEvaluation
) -> RAGEvaluation:

    db.add(evaluation)
    db.commit()
    db.refresh(evaluation)

    return evaluation


def get_rag_evaluation_by_id(
    db: Session,
    evaluation_id: int
) -> RAGEvaluation | None:

    return db.get(
        RAGEvaluation,
        evaluation_id
    )


def update_rag_evaluation_feedback(
    db: Session,
    evaluation: RAGEvaluation,
    *,
    retrieval_rating: int,
    answer_rating: int,
    feedback_note: str | None,
    evaluated_at: datetime
) -> RAGEvaluation:

    evaluation.retrieval_rating = retrieval_rating
    evaluation.answer_rating = answer_rating
    evaluation.feedback_note = feedback_note
    evaluation.evaluated_at = evaluated_at

    db.commit()
    db.refresh(evaluation)

    return evaluation
