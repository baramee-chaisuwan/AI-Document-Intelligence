from langchain_core.output_parsers import StrOutputParser

from app.rag.chain import (
    get_assistant_chain,
    get_recommendation_chain
)

from app.vector.hybrid_search import hybrid_search
from app.vector.vector_service import get_candidate_documents


assistant_rag_chain = None


def get_assistant_rag_chain():

    global assistant_rag_chain

    if assistant_rag_chain is None:
        assistant_rag_chain = (
            get_assistant_chain()
            | StrOutputParser()
        )

    return assistant_rag_chain


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



def build_full_candidate_context(candidate_id):

    result = get_candidate_documents(
        candidate_id
    )

    documents = result["documents"]


    if not documents:
        return ""


    return f"""
Candidate ID: {candidate_id}

Resume:
{"\n".join(documents)}

--------------------
"""



def ask_rag(question: str):

    results = hybrid_search(
        query=question,
        n_results=3
    )


    metadatas = results["metadatas"][0]


    if not metadatas:
        return "I couldn't find that information in the resume."


    candidate_id = metadatas[0]["candidate_id"]


    context = build_full_candidate_context(
        candidate_id
    )


    if not context.strip():
        return "I couldn't find that information in the resume."


    return get_assistant_rag_chain().invoke(
        {
            "resume": context,
            "question": question
        }
    )



def ask_recommendation(question: str):

    results = hybrid_search(
        query=RECOMMENDATION_SEARCH_QUERY,
        n_results=10
    )


    metadatas = results["metadatas"][0]


    if not metadatas:
        return {
            "candidate_id": "N/A",
            "candidate_name": "No Candidate Found",
            "match_score": 0,
            "strengths": [],
            "relevant_experience": [],
            "reason": "No candidate information was found in the resume database."
        }


    candidate_ids = list(
        dict.fromkeys(
            [
                meta["candidate_id"]
                for meta in metadatas
            ]
        )
    )


    context = ""


    for candidate_id in candidate_ids:

        context += build_full_candidate_context(
            candidate_id
        )


    answer = get_recommendation_chain().invoke(
        {
            "resume": context,
            "question": question
        }
    )


    return answer.model_dump()