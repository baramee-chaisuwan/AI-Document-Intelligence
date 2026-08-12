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
