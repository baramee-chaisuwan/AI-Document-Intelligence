from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.pdf_service import (save_uploaded_file,extract_text_from_pdf)
from app.services.gemini_service import summarize_document
from app.services.extraction_service import (extract_resume_data)

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

    extracted_text = extracted_text[:5000]

    summary = summarize_document(extracted_text)

    if not summary:
        raise HTTPException(
            status_code=400,
            detail="Failed to generate summary"
        )

    resume_data = extract_resume_data(extracted_text)

    return {
        "filename": file.filename,
        "message": "File uploaded successfully",
        "summary": summary,
        "resume_data": resume_data
    }