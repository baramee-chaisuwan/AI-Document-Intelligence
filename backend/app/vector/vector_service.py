import logging

from app.vector.chroma_client import collection
from app.rag.embedding_service import create_embedding


logger = logging.getLogger(__name__)


DEFAULT_SEARCH_RESULTS = 10
MAX_SEARCH_RESULTS = 50


def validate_text(
    text,
    field_name
):

    if not isinstance(
        text,
        str
    ):

        raise ValueError(
            f"{field_name} must be a string"
        )


    normalized_text = (
        text.strip()
    )


    if not normalized_text:

        raise ValueError(
            f"{field_name} must not be empty"
        )


    return normalized_text


def validate_identifier(
    value,
    field_name
):

    normalized_value = str(
        value or ""
    ).strip()


    if not normalized_value:

        raise ValueError(
            f"{field_name} is required"
        )


    return normalized_value


def create_embedding_list(
    text
):

    embedding = create_embedding(
        text
    )


    if embedding is None:

        raise RuntimeError(
            "Embedding service returned no result"
        )


    try:

        embedding_list = (
            embedding.tolist()
        )

    except AttributeError as error:

        raise RuntimeError(
            "Embedding result has an invalid format"
        ) from error


    if (
        not isinstance(
            embedding_list,
            list
        )
        or not embedding_list
    ):

        raise RuntimeError(
            "Embedding result is empty"
        )


    return embedding_list


def add_document(
    document_id: str,
    candidate_id: str,
    text: str
):

    document_id = (
        validate_identifier(
            document_id,
            "Document ID"
        )
    )


    candidate_id = (
        validate_identifier(
            candidate_id,
            "Candidate ID"
        )
    )


    text = validate_text(
        text,
        "Document text"
    )


    embedding = (
        create_embedding_list(
            text
        )
    )


    try:

        collection.add(
            ids=[
                document_id
            ],
            documents=[
                text
            ],
            embeddings=[
                embedding
            ],
            metadatas=[
                {
                    "document_id": (
                        document_id
                    ),
                    "candidate_id": (
                        candidate_id
                    )
                }
            ]
        )

    except Exception as error:

        logger.exception(
            "Failed to add vector document: "
            "document_id=%s, candidate_id=%s",
            document_id,
            candidate_id
        )

        raise RuntimeError(
            "Vector document could not be added"
        ) from error


def search_documents(
    query: str,
    n_results: int = DEFAULT_SEARCH_RESULTS
):

    query = validate_text(
        query,
        "Search query"
    )


    if (
        not isinstance(
            n_results,
            int
        )
        or isinstance(
            n_results,
            bool
        )
    ):

        raise ValueError(
            "n_results must be an integer"
        )


    if n_results <= 0:

        raise ValueError(
            "n_results must be greater than 0"
        )


    n_results = min(
        n_results,
        MAX_SEARCH_RESULTS
    )


    query_embedding = (
        create_embedding_list(
            query
        )
    )


    try:

        results = collection.query(
            query_embeddings=[
                query_embedding
            ],
            n_results=n_results,
            include=[
                "documents",
                "metadatas",
                "distances"
            ]
        )

    except Exception as error:

        logger.exception(
            "Vector search failed"
        )

        raise RuntimeError(
            "Vector search is unavailable"
        ) from error


    if not isinstance(
        results,
        dict
    ):

        raise RuntimeError(
            "Vector search returned an invalid result"
        )


    return results


def get_candidate_documents(
    candidate_id: str
):

    candidate_id = (
        validate_identifier(
            candidate_id,
            "Candidate ID"
        )
    )


    try:

        results = collection.get(
            where={
                "candidate_id": (
                    candidate_id
                )
            },
            include=[
                "documents",
                "metadatas"
            ]
        )

    except Exception as error:

        logger.exception(
            "Failed to retrieve documents for "
            "candidate_id=%s",
            candidate_id
        )

        raise RuntimeError(
            "Candidate vector documents "
            "could not be retrieved"
        ) from error


    if not isinstance(
        results,
        dict
    ):

        raise RuntimeError(
            "Vector storage returned an invalid result"
        )


    return results


def delete_candidate_documents(
    candidate_id: str
):

    candidate_id = (
        validate_identifier(
            candidate_id,
            "Candidate ID"
        )
    )


    try:

        collection.delete(
            where={
                "candidate_id": (
                    candidate_id
                )
            }
        )

    except Exception as error:

        logger.exception(
            "Failed to delete vector documents for "
            "candidate_id=%s",
            candidate_id
        )

        raise RuntimeError(
            "Candidate vector documents "
            "could not be deleted"
        ) from error


def delete_document(
    document_id: str
):

    document_id = (
        validate_identifier(
            document_id,
            "Document ID"
        )
    )


    try:

        collection.delete(
            ids=[
                document_id
            ]
        )

    except Exception as error:

        logger.exception(
            "Failed to delete vector document: "
            "document_id=%s",
            document_id
        )

        raise RuntimeError(
            "Vector document could not be deleted"
        ) from error