from app.vector.chroma_client import collection
from app.rag.embedding_service import create_embedding


def add_document(document_id: str, text: str):

    embedding = create_embedding(text)

    collection.add(
        ids=[document_id],
        documents=[text],
        embeddings=[embedding.tolist()]
    )

def search_documents(query: str, n_results: int = 3):

    query_embedding = create_embedding(query)

    results = collection.query(
        query_embeddings=[query_embedding.tolist()],
        n_results=n_results
    )

    return results

def delete_document(document_id: str):

    collection.delete(
        ids=[document_id]
    )