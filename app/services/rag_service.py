from app.rag.rag_chain import ask_rag


def ask_resume(question: str):

    answer = ask_rag(question)

    return {
        "answer": answer
    }