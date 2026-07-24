from langchain_core.output_parsers import StrOutputParser

from app.rag.chain import (
    assistant_chain,
    recommendation_chain
)

from app.vector.vector_service import search_documents


def build_candidate_context(results):

    candidates = {}
    candidate_count = {}

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]

    for document, metadata in zip(documents, metadatas):

        candidate_id = metadata["candidate_id"]

        if candidate_count.get(candidate_id, 0) >= 2:
            continue

        if candidate_id not in candidates:
            candidates[candidate_id] = []

        candidates[candidate_id].append(document)

        candidate_count[candidate_id] = (
            candidate_count.get(candidate_id, 0) + 1
        )

    context = ""

    for candidate_id, chunks in candidates.items():

        context += f"""
Candidate ID: {candidate_id}

Resume:
{"\n".join(chunks)}

--------------------
"""

    return context


def ask_rag(question: str):

    results = search_documents(
        query=question,
        n_results=3
    )

    context = "\n\n".join(
        results["documents"][0]
    )

    chain = (
        assistant_chain
        | StrOutputParser()
    )

    answer = chain.invoke(
        {
            "resume": context,
            "question": question
        }
    )

    return answer


def ask_recommendation(question: str):

    search_query = """
AI Engineer
Python
Machine Learning
Deep Learning
Generative AI
LLM
NLP
FastAPI
Docker
SQL
Backend Development
MLOps
"""

    results = search_documents(
        query=search_query,
        n_results=15
    )

    context = build_candidate_context(results)

    chain = recommendation_chain

    answer = chain.invoke(
        {
            "resume": context,
            "question": question
        }
    )

    return answer.model_dump()