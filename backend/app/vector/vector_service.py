import logging

from app.database.database import SessionLocal
from app.rag.embedding_service import (
    create_embedding,
    normalize_embedding
)
from app.repositories import resume_chunk_repository


logger = logging.getLogger(__name__)


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


def validate_candidate_id(
    value
) -> int:

    if isinstance(value, bool):

        raise ValueError(
            "Candidate ID must be a positive integer"
        )

    try:

        candidate_id = int(
            str(value).strip()
        )

    except (TypeError, ValueError) as error:

        raise ValueError(
            "Candidate ID must be a positive integer"
        ) from error

    if candidate_id <= 0:

        raise ValueError(
            "Candidate ID must be a positive integer"
        )

    return candidate_id


def create_embedding_list(
    text
):

    embedding = create_embedding(
        text
    )

    try:

        return normalize_embedding(
            embedding
        )

    except ValueError as error:

        raise RuntimeError(
            "Embedding result is invalid"
        ) from error


def search_documents(
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
    query_embedding = create_embedding_list(
        query
    )

    try:

        with SessionLocal() as db:

            rows = (
                resume_chunk_repository
                .search_similar_chunks(
                    db,
                    query_embedding,
                    n_results
                )
            )

    except Exception as error:

        logger.exception(
            "PostgreSQL vector search failed"
        )

        raise RuntimeError(
            "Vector search is unavailable"
        ) from error

    return {
        "ids": [[
            chunk.document_id
            for chunk, _ in rows
        ]],
        "documents": [[
            chunk.chunk_text
            for chunk, _ in rows
        ]],
        "metadatas": [[
            _chunk_metadata(chunk)
            for chunk, _ in rows
        ]],
        "distances": [[
            float(distance)
            for _, distance in rows
        ]]
    }


def get_candidate_documents(
    candidate_id: str | int
):

    candidate_id = validate_candidate_id(
        candidate_id
    )

    try:

        with SessionLocal() as db:

            chunks = (
                resume_chunk_repository
                .get_candidate_chunks(
                    db,
                    candidate_id
                )
            )

    except Exception as error:

        logger.exception(
            "Failed to retrieve durable chunks for "
            "candidate_id=%s",
            candidate_id
        )

        raise RuntimeError(
            "Candidate vector documents "
            "could not be retrieved"
        ) from error

    return {
        "ids": [
            chunk.document_id
            for chunk in chunks
        ],
        "documents": [
            chunk.chunk_text
            for chunk in chunks
        ],
        "metadatas": [
            _chunk_metadata(chunk)
            for chunk in chunks
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


def _chunk_metadata(
    chunk
) -> dict[str, str]:

    return {
        "document_id": chunk.document_id,
        "candidate_id": str(
            chunk.candidate_id
        )
    }
