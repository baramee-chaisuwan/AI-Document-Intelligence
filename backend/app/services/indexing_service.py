from app.rag.text_splitter import split_resume

from app.vector.vector_service import (
    add_document,
    delete_candidate_documents
)

from app.vector.bm25_service import (
    add_bm25_document,
    delete_bm25_candidate
)

def index_resume(
    document_id: str,
    resume_text: str,
):
    print(f"Indexing resume: {document_id}")

    delete_candidate_documents(
        document_id
    )

    delete_bm25_candidate(
        document_id
    )


    chunks = split_resume(
        resume_text
    )

    print(f"Chunks: {len(chunks)}")


    for i, chunk in enumerate(chunks):

        chunk_id = f"{document_id}_{i}"

        add_document(
            document_id=chunk_id,
            candidate_id=document_id,
            text=chunk,
        )

        add_bm25_document(
            document_id=chunk_id,
            candidate_id=document_id,
            text=chunk,
        )

    print("Index completed")