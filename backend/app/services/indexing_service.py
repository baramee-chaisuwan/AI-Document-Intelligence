import logging

from app.rag.text_splitter import split_resume

from app.vector.vector_service import (
    add_document,
    delete_candidate_documents
)

from app.vector.bm25_service import (
    add_bm25_document,
    delete_bm25_candidate
)

logger = logging.getLogger(__name__)

def cleanup_candidate_index(
    document_id
):

    cleanup_errors = []

    try:

        delete_candidate_documents(
            document_id
        )

    except Exception as error:

        cleanup_errors.append(
            f"ChromaDB cleanup failed: {error}"
        )

    try:

        delete_bm25_candidate(
            document_id
        )

    except Exception as error:

        cleanup_errors.append(
            f"BM25 cleanup failed: {error}"
        )

    if cleanup_errors:

        logger.error(
            "Index cleanup failed for candidate_id=%s: %s",
            document_id,
            " | ".join(cleanup_errors)
        )

        return False

    return True

def index_resume(
    document_id: str,
    resume_text: str,
):

    document_id = str(
        document_id or ""
    ).strip()

    if not document_id:

        raise ValueError(
            "Document ID is required"
        )

    if not resume_text or not resume_text.strip():

        raise ValueError(
            "Resume text is required for indexing"
        )

    chunks = split_resume(
        resume_text.strip()
    )


    if not isinstance(
        chunks,
        list
    ):

        raise ValueError(
            "Resume splitter returned an invalid result"
        )

    chunks = [
        chunk.strip()
        for chunk in chunks
        if isinstance(chunk, str)
        and chunk.strip()
    ]

    if not chunks:

        raise ValueError(
            "Resume did not produce any indexable chunks"
        )

    logger.info(
        "Starting resume indexing: candidate_id=%s, chunks=%s",
        document_id,
        len(chunks)
    )

    cleanup_success = (
        cleanup_candidate_index(
            document_id
        )
    )

    if not cleanup_success:

        raise RuntimeError(
            "Existing candidate index could not be cleared"
        )

    try:

        for index, chunk in enumerate(
            chunks
        ):

            chunk_id = (
                f"{document_id}_{index}"
            )


            add_document(
                document_id=chunk_id,
                candidate_id=document_id,
                text=chunk
            )


            add_bm25_document(
                document_id=chunk_id,
                candidate_id=document_id,
                text=chunk
            )

    except Exception as error:

        logger.exception(
            "Resume indexing failed: candidate_id=%s",
            document_id
        )

        cleanup_candidate_index(
            document_id
        )

        raise RuntimeError(
            "Resume indexing failed and partial index cleanup was attempted"
        ) from error

    logger.info(
        "Resume indexing completed: candidate_id=%s, chunks=%s",
        document_id,
        len(chunks)
    )

    return {
        "candidate_id": document_id,
        "chunk_count": len(chunks),
        "status": "indexed"
    }