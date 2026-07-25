from app.vector.vector_service import search_documents
from app.vector.bm25_service import search_bm25

def normalize_scores(scores):

    if not scores:
        return []

    max_score = max(scores)

    if max_score == 0:
        return [0 for _ in scores]

    return [
        score / max_score
        for score in scores
    ]

def hybrid_search(
    query: str,
    n_results: int = 10
):

    vector_results = search_documents(
        query=query,
        n_results=n_results
    )


    bm25_results = search_bm25(
        query=query,
        n_results=n_results
    )


    combined = []

    vector_scores = [
        1 / (1 + distance)
        for distance in vector_results["distances"][0]
    ]

    vector_scores = normalize_scores(
        vector_scores
    )


    for doc, meta, score in zip(
        vector_results["documents"][0],
        vector_results["metadatas"][0],
        vector_scores
    ):

        combined.append(
            {
                "document": doc,
                "metadata": meta,
                "score": score,
                "source": "vector"
            }
        )

    bm25_scores = normalize_scores(
        bm25_results["scores"]
    )


    for doc, meta, score in zip(
        bm25_results["documents"],
        bm25_results["metadatas"],
        bm25_scores
    ):

        combined.append(
            {
                "document": doc,
                "metadata": meta,
                "score": score,
                "source": "bm25"
            }
        )

    combined.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    top_results = combined[:n_results]

    return {
        "documents": [
            [
                item["document"]
                for item in top_results
            ]
        ],

        "metadatas": [
            [
                item["metadata"]
                for item in top_results
            ]
        ],

        "scores": [
            [
                item["score"]
                for item in top_results
            ]
        ]
    }