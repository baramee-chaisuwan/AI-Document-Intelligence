from app.vector.vector_service import (add_document,delete_candidate_documents)
from app.rag.text_splitter import split_resume


def index_resume(
    document_id: str,
    resume_text: str,
):
    print(f"Indexing resume: {document_id}")

    chunks = split_resume(resume_text)

    print(f"Chunks: {len(chunks)}")

    for i, chunk in enumerate(chunks):

        add_document(
            document_id=f"{document_id}_{i}",
            candidate_id=document_id,
            text=chunk,
        )

    print("Index completed")