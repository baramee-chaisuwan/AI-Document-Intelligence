from langchain_core.output_parsers import StrOutputParser

from app.rag.chain import (
    assistant_chain,
    recommendation_chain
)

from app.vector.hybrid_search import hybrid_search


assistant_rag_chain = (
    assistant_chain
    | StrOutputParser()
)


RECOMMENDATION_SEARCH_QUERY = """
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


def build_candidate_context(results):

    candidates = {}
    candidate_count = {}

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]


    for document, metadata in zip(
        documents,
        metadatas
    ):

        candidate_id = metadata["candidate_id"]


        if candidate_count.get(candidate_id, 0) >= 2:
            continue


        candidates.setdefault(
            candidate_id,
            []
        ).append(document)


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

    results = hybrid_search(
        query=question,
        n_results=3
    )


    documents = results["documents"][0]


    # Prevent LLM hallucination when no resume context exists
    if not documents:
        return "I couldn't find that information in the resume."


    context = "\n\n".join(
        documents
    )


    return assistant_rag_chain.invoke(
        {
            "resume": context,
            "question": question
        }
    )



def ask_recommendation(question: str):

    results = hybrid_search(
        query=RECOMMENDATION_SEARCH_QUERY,
        n_results=15
    )


    context = build_candidate_context(
        results
    )


    if not context.strip():

        return {
            "candidate_id": "N/A",
            "candidate_name": "No Candidate Found",
            "match_score": 0,
            "strengths": [],
            "relevant_experience": [],
            "reason": "No candidate information was found in the resume database."
        }


    answer = recommendation_chain.invoke(
        {
            "resume": context,
            "question": question
        }
    )


    return answer.model_dump()