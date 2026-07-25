from rank_bm25 import BM25Okapi

from app.vector.bm25_storage import (
    save_bm25_data,
    load_bm25_data
)

documents, metadatas = load_bm25_data()

bm25_index = None

def tokenize(text: str):
    return text.lower().split()


def rebuild_index():

    global bm25_index

    if documents:

        tokenized_documents = [
            tokenize(doc)
            for doc in documents
        ]

        bm25_index = BM25Okapi(
            tokenized_documents
        )

    else:
        bm25_index = None

rebuild_index()

def add_bm25_document(
    document_id: str,
    candidate_id: str,
    text: str
):

    documents.append(text)

    metadatas.append(
        {
            "document_id": document_id,
            "candidate_id": candidate_id
        }
    )

    rebuild_index()

    save_bm25_data(
        documents,
        metadatas
    )

def search_bm25(
    query: str,
    n_results: int = 10
):

    if bm25_index is None:

        return {
            "documents": [],
            "metadatas": [],
            "scores": []
        }


    scores = bm25_index.get_scores(
        tokenize(query)
    )

    ranked = sorted(
        range(len(scores)),
        key=lambda i: scores[i],
        reverse=True
    )

    top_indices = ranked[:n_results]

    return {

        "documents": [
            documents[i]
            for i in top_indices
        ],

        "metadatas": [
            metadatas[i]
            for i in top_indices
        ],

        "scores": [
            scores[i]
            for i in top_indices
        ]
    }

def delete_bm25_candidate(
    candidate_id: str
):

    global documents
    global metadatas

    filtered_docs = []
    filtered_meta = []


    for doc, meta in zip(
        documents,
        metadatas
    ):

        if meta["candidate_id"] != candidate_id:

            filtered_docs.append(doc)
            filtered_meta.append(meta)


    documents = filtered_docs
    metadatas = filtered_meta

    rebuild_index()

    save_bm25_data(
        documents,
        metadatas
    )