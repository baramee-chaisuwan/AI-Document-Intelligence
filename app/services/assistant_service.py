from app.services.rag_service import ask_rag


def ask_assistant(question: str):

    return ask_rag(question)