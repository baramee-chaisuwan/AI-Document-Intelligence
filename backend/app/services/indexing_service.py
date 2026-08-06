import logging

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database.models import ResumeChunk
from app.rag.embedding_service import (
    create_embeddings,
    normalize_embedding
)
from app.rag.text_splitter import split_resume
from app.repositories import resume_chunk_repository


logger = logging.getLogger(__name__)


class ResumeIndexingError(RuntimeError):
    """Raised when resume chunks or embeddings cannot be prepared."""


def index_resume(
    db: Session,
    document_id: str | int,
    resume_text: str
):

    candidate_id = _validate_candidate_id(
        document_id
    )
    chunks = _prepare_chunks(
        resume_text
    )

    logger.info(
        "Starting durable resume indexing: "
        "candidate_id=%s, chunks=%s",
        candidate_id,
        len(chunks)
    )

    try:

        raw_embeddings = create_embeddings(
            chunks
        )
        embeddings = _prepare_embeddings(
            raw_embeddings,
            len(chunks)
        )

    except ResumeIndexingError:

        raise

    except Exception as error:

        logger.exception(
            "Resume embeddings could not be prepared: "
            "candidate_id=%s",
            candidate_id
        )

        raise ResumeIndexingError(
            "Resume embeddings could not be prepared"
        ) from error

    chunk_models = [
        ResumeChunk(
            candidate_id=candidate_id,
            document_id=(
                f"{candidate_id}_{chunk_index}"
            ),
            chunk_index=chunk_index,
            chunk_text=chunk,
            embedding=embedding
        )
        for chunk_index, (
            chunk,
            embedding
        ) in enumerate(
            zip(
                chunks,
                embeddings
            )
        )
    ]

    try:

        resume_chunk_repository.replace_candidate_chunks(
            db,
            candidate_id,
            chunk_models
        )

    except SQLAlchemyError:

        raise

    except Exception as error:

        logger.exception(
            "Durable resume chunks could not be prepared: "
            "candidate_id=%s",
            candidate_id
        )

        raise ResumeIndexingError(
            "Durable resume chunks could not be prepared"
        ) from error

    logger.info(
        "Durable resume indexing prepared: "
        "candidate_id=%s, chunks=%s",
        candidate_id,
        len(chunk_models)
    )

    return {
        "candidate_id": str(candidate_id),
        "chunk_count": len(chunk_models),
        "status": "indexed"
    }


def _validate_candidate_id(
    value
) -> int:

    if isinstance(value, bool):

        raise ResumeIndexingError(
            "Document ID must be a positive integer"
        )

    try:

        candidate_id = int(
            str(value).strip()
        )

    except (TypeError, ValueError) as error:

        raise ResumeIndexingError(
            "Document ID must be a positive integer"
        ) from error

    if candidate_id <= 0:

        raise ResumeIndexingError(
            "Document ID must be a positive integer"
        )

    return candidate_id


def _prepare_chunks(
    resume_text
) -> list[str]:

    if (
        not isinstance(resume_text, str)
        or not resume_text.strip()
    ):

        raise ResumeIndexingError(
            "Resume text is required for indexing"
        )

    try:

        chunks = split_resume(
            resume_text.strip()
        )

    except Exception as error:

        raise ResumeIndexingError(
            "Resume text could not be split"
        ) from error

    if not isinstance(chunks, list):

        raise ResumeIndexingError(
            "Resume splitter returned an invalid result"
        )

    chunks = [
        chunk.strip()
        for chunk in chunks
        if isinstance(chunk, str)
        and chunk.strip()
    ]

    if not chunks:

        raise ResumeIndexingError(
            "Resume did not produce any indexable chunks"
        )

    return chunks


def _prepare_embeddings(
    raw_embeddings,
    expected_count: int
) -> list[list[float]]:

    try:

        values = raw_embeddings.tolist()

    except AttributeError:

        values = raw_embeddings

    if (
        not isinstance(values, list)
        or len(values) != expected_count
    ):

        raise ResumeIndexingError(
            "Embedding count does not match chunk count"
        )

    try:

        return [
            normalize_embedding(
                embedding
            )
            for embedding in values
        ]

    except ValueError as error:

        raise ResumeIndexingError(
            "Resume embedding is invalid"
        ) from error
