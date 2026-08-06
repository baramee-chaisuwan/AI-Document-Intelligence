import re

from rank_bm25 import BM25Okapi

from app.database.database import SessionLocal
from app.repositories import resume_chunk_repository


DEFAULT_SEARCH_RESULTS = 10
MAX_SEARCH_RESULTS = 50


def validate_text(
    text,
    field_name
):

    if not isinstance(text, str):

        raise ValueError(
            f"{field_name} must be a string"
        )

    normalized_text = text.strip()

    if not normalized_text:

        raise ValueError(
            f"{field_name} must not be empty"
        )

    return normalized_text


def tokenize(
    text: str
):

    normalized_text = str(
        text or ""
    ).lower()

    return re.findall(
        r"[a-z0-9ก-๙+#.\-]+",
        normalized_text
    )


def search_bm25(
    query: str,
    n_results: int = DEFAULT_SEARCH_RESULTS
):

    query = validate_text(
        query,
        "Search query"
    )
    n_results = _validate_n_results(
        n_results
    )

    with SessionLocal() as db:

        chunks = resume_chunk_repository.get_all_chunks(
            db
        )

    return search_bm25_chunks(
        query,
        chunks,
        n_results
    )


def search_bm25_chunks(
    query: str,
    chunks,
    n_results: int = DEFAULT_SEARCH_RESULTS
):

    query_tokens = tokenize(
        query
    )

    if not query_tokens or not chunks:

        return _empty_results()

    documents = [
        chunk.chunk_text
        for chunk in chunks
    ]
    tokenized_documents = [
        tokenize(document)
        for document in documents
    ]

    if not any(tokenized_documents):

        return _empty_results()

    bm25_index = BM25Okapi(
        tokenized_documents
    )
    scores = bm25_index.get_scores(
        query_tokens
    )
    ranked = sorted(
        range(len(scores)),
        key=lambda index: scores[index],
        reverse=True
    )
    top_indices = [
        index
        for index in ranked
        if scores[index] > 0
    ][
        :n_results
    ]

    return {
        "documents": [
            documents[index]
            for index in top_indices
        ],
        "metadatas": [
            {
                "document_id": (
                    chunks[index].document_id
                ),
                "candidate_id": str(
                    chunks[index].candidate_id
                )
            }
            for index in top_indices
        ],
        "scores": [
            float(scores[index])
            for index in top_indices
        ]
    }


def _validate_n_results(
    n_results
) -> int:

    if (
        not isinstance(n_results, int)
        or isinstance(n_results, bool)
    ):

        raise ValueError(
            "n_results must be an integer"
        )

    if n_results <= 0:

        raise ValueError(
            "n_results must be greater than 0"
        )

    return min(
        n_results,
        MAX_SEARCH_RESULTS
    )


def _empty_results():

    return {
        "documents": [],
        "metadatas": [],
        "scores": []
    }
