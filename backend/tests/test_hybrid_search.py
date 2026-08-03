from uuid import uuid4

from app.vector.bm25_service import (
    add_bm25_document,
    delete_bm25_candidate
)
from app.vector.hybrid_search import (
    hybrid_search
)
from app.vector.vector_service import (
    add_document,
    delete_candidate_documents
)


def test_hybrid_search_fastapi_docker():

    candidate_id = (
        f"test_candidate_{uuid4().hex}"
    )

    document_id = (
        f"{candidate_id}_0"
    )

    resume_text = """
    Baramee Chaisuwan

    AI Engineer

    Skills:
    Python
    FastAPI
    Docker
    Machine Learning
    LLM
    RAG
    """

    try:

        add_document(
            document_id=document_id,
            candidate_id=candidate_id,
            text=resume_text
        )

        add_bm25_document(
            document_id=document_id,
            candidate_id=candidate_id,
            text=resume_text
        )


        result = hybrid_search(
            query="FastAPI Docker AI Engineer",
            n_results=10
        )


        assert "documents" in result
        assert "metadatas" in result
        assert "scores" in result


        documents = result["documents"][0]
        metadatas = result["metadatas"][0]
        scores = result["scores"][0]


        assert len(documents) > 0

        assert len(documents) == len(
            metadatas
        )

        assert len(documents) == len(
            scores
        )


        matched_results = [
            (
                document,
                metadata,
                score
            )
            for (
                document,
                metadata,
                score
            ) in zip(
                documents,
                metadatas,
                scores
            )
            if (
                metadata.get("candidate_id")
                == candidate_id
            )
        ]


        assert matched_results


        matched_document = (
            matched_results[0][0]
        )

        matched_score = (
            matched_results[0][2]
        )


        assert "FastAPI" in matched_document
        assert "Docker" in matched_document

        assert 0 <= matched_score <= 1

    finally:

        delete_candidate_documents(
            candidate_id
        )

        delete_bm25_candidate(
            candidate_id
        )