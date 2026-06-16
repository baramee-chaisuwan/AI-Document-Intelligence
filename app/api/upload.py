from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.pdf_service import (save_uploaded_file,extract_text_from_pdf)

router = APIRouter(
    prefix="/upload",
    tags=["Document Upload"]
)


@router.post("/")
def upload_document(file: UploadFile = File(...)):

    if not file.filename.endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed"
        )

    file_path = f"uploads/{file.filename}"

    save_uploaded_file(file, file_path)

    extracted_text = extract_text_from_pdf(file_path)

    return {
        "filename": file.filename,
        "message": "File uploaded successfully",
        "preview_text": extracted_text[:500]
    }