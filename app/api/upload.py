from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from app.services.pdf_service import (save_uploaded_file,extract_text_from_pdf)
from app.services.gemini_service import summarize_document
from app.services.extraction_service import extract_resume_data
from app.services.analyzer_service import analyze_resume
from app.models.resume_model import ResumeResponse
from app.database.database import get_db
from app.database.models import Candidate

router = APIRouter(prefix="/upload",tags=["Document Upload"])

@router.post(
    "/",
    response_model=ResumeResponse
)
def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):

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

    resume_data = extract_resume_data(extracted_text)

    analysis = analyze_resume(resume_data)

    if (
        resume_data["name"] != "Unknown"
        and analysis["candidate_level"] != "Unknown"
    ):

        candidate = Candidate(
            name=resume_data["name"],
            summary=summary,
            candidate_level=analysis["candidate_level"],
            skill_score=analysis["skill_score"]
        )

        db.add(candidate)
        db.commit()
        db.refresh(candidate)

    return {
        "filename": file.filename,
        "message": "File uploaded successfully",
        "summary": summary,
        "resume_data": resume_data,
        "analysis": analysis
    }