from app.rag.rag_chain import (ask_rag,ask_recommendation)

def ask_resume(question: str):

    answer = ask_rag(question)

    return {
        "answer": answer
    }

def recommend_candidate(question: str):

    return ask_recommendation(question)