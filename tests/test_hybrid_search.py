from app.vector.hybrid_search import hybrid_search


def test_hybrid_search_fastapi_docker():

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


    candidate_ids = [
        meta["candidate_id"]
        for meta in metadatas
    ]


    assert "148" in candidate_ids