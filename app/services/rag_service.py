from app.rag.rag_chain import ask_recommendation as rag_ask_recommendation


def ask_recommendation(question: str):
    return rag_ask_recommendation(question)