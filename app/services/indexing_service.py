from app.vector.vector_service import add_document

def index_resume(document_id: str, resume_text: str):
    print(f"Indexing resume: {document_id}")

    add_document(
        document_id=document_id,
        text=resume_text,
    )

    print("Index completed")