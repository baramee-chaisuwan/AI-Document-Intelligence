from app.vector.vector_service import (
    add_document,
    delete_document
)

from app.services.hybrid_search_service import hybrid_search


def test_hybrid_search_fastapi_docker():

    delete_document(
        "test_resume_001"
    )

    add_document(
        document_id="test_resume_001",
        candidate_id="test_candidate_001",
        text="""
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
    )


    result = hybrid_search(
        query="FastAPI Docker AI Engineer",
        n_results=5
    )


    assert "documents" in result
    assert "metadatas" in result
    assert "scores" in result


    documents = result["documents"][0]
    metadatas = result["metadatas"][0]


    assert len(documents) > 0
    assert len(metadatas) > 0