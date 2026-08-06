from unittest.mock import patch

from app.vector.hybrid_search import (
    RRF_K,
    hybrid_search
)


def test_hybrid_search_preserves_reciprocal_rank_fusion():

    vector_results = {
        "documents": [[
            "Vector-only chunk",
            "Shared chunk"
        ]],
        "metadatas": [[
            {
                "document_id": "1_0",
                "candidate_id": "1"
            },
            {
                "document_id": "2_0",
                "candidate_id": "2"
            }
        ]],
        "distances": [[
            0.05,
            0.10
        ]]
    }
    bm25_results = {
        "documents": [
            "Shared chunk",
            "BM25-only chunk"
        ],
        "metadatas": [
            {
                "document_id": "2_0",
                "candidate_id": "2"
            },
            {
                "document_id": "3_0",
                "candidate_id": "3"
            }
        ],
        "scores": [
            4.2,
            2.1
        ]
    }

    with patch(
        "app.vector.hybrid_search.search_documents",
        return_value=vector_results
    ), patch(
        "app.vector.hybrid_search.search_bm25",
        return_value=bm25_results
    ):

        result = hybrid_search(
            "FastAPI engineer",
            n_results=3
        )

    assert result["documents"][0][0] == "Shared chunk"
    assert result["metadatas"][0][0] == {
        "document_id": "2_0",
        "candidate_id": "2",
        "retrieval_sources": [
            "vector",
            "bm25"
        ],
        "vector_rank": 2,
        "bm25_rank": 1
    }
    expected_score = (
        1 / (RRF_K + 2)
        + 1 / (RRF_K + 1)
    )
    assert result["scores"][0][0] == expected_score


def test_hybrid_search_keeps_existing_result_shape():

    empty_vector = {
        "documents": [[]],
        "metadatas": [[]],
        "distances": [[]]
    }
    empty_bm25 = {
        "documents": [],
        "metadatas": [],
        "scores": []
    }

    with patch(
        "app.vector.hybrid_search.search_documents",
        return_value=empty_vector
    ), patch(
        "app.vector.hybrid_search.search_bm25",
        return_value=empty_bm25
    ):

        result = hybrid_search(
            "no matches"
        )

    assert result == {
        "documents": [[]],
        "metadatas": [[]],
        "scores": [[]]
    }
