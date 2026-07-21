from app.vector.vector_service import search_documents
from app.database.models import Candidate


def semantic_search(query: str, db):

    results = search_documents(query)

    formatted_results = []

    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    for metadata, distance in zip(
        metadatas,
        distances
    ):

        candidate = (
            db.query(Candidate)
            .filter(Candidate.id == int(metadata["candidate_id"]))
            .first()
        )

        if candidate:

            formatted_results.append(
                {
                    "id": candidate.id,
                    "name": candidate.name,
                    "summary": candidate.summary,
                    "candidate_level": candidate.candidate_level,
                    "skill_score": candidate.skill_score,
                    "rule_score": candidate.rule_score,
                    "ai_score": candidate.ai_score,
                    "distance": round(distance, 4)
                }
            )

    return formatted_results