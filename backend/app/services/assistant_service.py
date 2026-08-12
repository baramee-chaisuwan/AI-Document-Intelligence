from app.rag.rag_chain import ask_rag
from sqlalchemy.orm import Session

def ask_assistant(
    question: str,
    db: Session | None = None
):
    return ask_rag(question, db=db)
