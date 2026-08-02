from app.rag.rag_chain import ask_rag

def ask_assistant(question: str):
    return ask_rag(question)