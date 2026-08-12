from app.rag.rag_chain import ask_recommendation as rag_ask_recommendation
from sqlalchemy.orm import Session

def ask_recommendation(
    question: str,
    db: Session | None = None
):
    return rag_ask_recommendation(question, db=db)
