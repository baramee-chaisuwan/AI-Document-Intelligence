from app.rag.rag_chain import ask_recommendation

def recommend_candidate(question: str):
    return ask_recommendation(question)