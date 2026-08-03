import logging
import re
import threading

from rank_bm25 import BM25Okapi

from app.vector.bm25_storage import (
    save_bm25_data,
    load_bm25_data
)

logger = logging.getLogger(__name__)

documents, metadatas = load_bm25_data()

bm25_index = None
bm25_lock = threading.Lock()

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

def validate_loaded_data():

    global documents
    global metadatas

    if not isinstance(
        documents,
        list
    ):

        documents = []

    if not isinstance(
        metadatas,
        list
    ):

        metadatas = []

    if len(documents) != len(metadatas):

        logger.error(
            "BM25 documents and metadata lengths do not match. "
            "documents=%s, metadatas=%s",
            len(documents),
            len(metadatas)
        )

        valid_length = min(
            len(documents),
            len(metadatas)
        )

        documents = documents[
            :valid_length
        ]

        metadatas = metadatas[
            :valid_length
        ]

def rebuild_index():

    global bm25_index

    validate_loaded_data()

    valid_documents = []

    for document in documents:

        if isinstance(
            document,
            str
        ) and document.strip():

            valid_documents.append(
                tokenize(
                    document
                )
            )

        else:

            valid_documents.append(
                []
            )

    if (
        valid_documents
        and any(
            tokens
            for tokens in valid_documents
        )
    ):

        bm25_index = BM25Okapi(
            valid_documents
        )

    else:

        bm25_index = None

validate_loaded_data()
rebuild_index()

def add_bm25_document(
    document_id: str,
    candidate_id: str,
    text: str
):

    add_bm25_documents(
        [
            {
                "document_id": document_id,
                "candidate_id": candidate_id,
                "text": text
            }
        ]
    )

def add_bm25_documents(
    items
):

    global documents
    global metadatas

    if not isinstance(
        items,
        list
    ):

        raise ValueError(
            "BM25 items must be a list"
        )

    if not items:

        raise ValueError(
            "At least one BM25 item is required"
        )

    new_documents = []
    new_metadatas = []

    for item in items:

        if not isinstance(
            item,
            dict
        ):

            raise ValueError(
                "Each BM25 item must be an object"
            )

        document_id = (
            validate_identifier(
                item.get(
                    "document_id"
                ),
                "Document ID"
            )
        )

        candidate_id = (
            validate_identifier(
                item.get(
                    "candidate_id"
                ),
                "Candidate ID"
            )
        )

        text = validate_text(
            item.get(
                "text"
            ),
            "Document text"
        )

        new_documents.append(
            text
        )

        new_metadatas.append(
            {
                "document_id": (
                    document_id
                ),
                "candidate_id": (
                    candidate_id
                )
            }
        )

    with bm25_lock:

        documents.extend(
            new_documents
        )

        metadatas.extend(
            new_metadatas
        )

        rebuild_index()

        try:

            save_bm25_data(
                documents,
                metadatas
            )

        except Exception as error:

            del documents[
                -len(new_documents):
            ]


            del metadatas[
                -len(new_metadatas):
            ]


            rebuild_index()


            logger.exception(
                "BM25 data could not be saved"
            )


            raise RuntimeError(
                "BM25 documents could not be added"
            ) from error

def search_bm25(
    query: str,
    n_results: int = 10
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

    query_tokens = tokenize(
        query
    )

    if not query_tokens:

        return {
            "documents": [],
            "metadatas": [],
            "scores": []
        }

    with bm25_lock:

        if bm25_index is None:

            return {
                "documents": [],
                "metadatas": [],
                "scores": []
            }

        scores = bm25_index.get_scores(
            query_tokens
        )

        ranked = sorted(
            range(
                len(scores)
            ),
            key=lambda index: scores[index],
            reverse=True
        )

        top_indices = []

        for index in ranked:

            if scores[index] <= 0:

                continue

            top_indices.append(
                index
            )

            if len(
                top_indices
            ) >= n_results:

                break

        return {
            "documents": [
                documents[index]
                for index in top_indices
            ],
            "metadatas": [
                metadatas[index]
                for index in top_indices
            ],
            "scores": [
                float(
                    scores[index]
                )
                for index in top_indices
            ]
        }

def delete_bm25_candidate(
    candidate_id: str
):

    global documents
    global metadatas

    candidate_id = (
        validate_identifier(
            candidate_id,
            "Candidate ID"
        )
    )

    with bm25_lock:

        old_documents = list(
            documents
        )

        old_metadatas = list(
            metadatas
        )

        filtered_documents = []
        filtered_metadatas = []


        for document, metadata in zip(
            documents,
            metadatas
        ):

            metadata_candidate_id = str(
                metadata.get(
                    "candidate_id",
                    ""
                )
            ).strip()

            if (
                metadata_candidate_id
                != candidate_id
            ):

                filtered_documents.append(
                    document
                )

                filtered_metadatas.append(
                    metadata
                )

        documents = filtered_documents
        metadatas = filtered_metadatas

        rebuild_index()

        try:

            save_bm25_data(
                documents,
                metadatas
            )

        except Exception as error:

            documents = old_documents
            metadatas = old_metadatas

            rebuild_index()

            logger.exception(
                "BM25 candidate deletion could not be saved: "
                "candidate_id=%s",
                candidate_id
            )

            raise RuntimeError(
                "BM25 candidate documents "
                "could not be deleted"
            ) from error