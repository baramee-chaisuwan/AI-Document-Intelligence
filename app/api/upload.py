from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from app.services.pdf_service import (save_uploaded_file,extract_text_from_pdf)
from app.services.gemini_service import summarize_document
from app.services.extraction_service import extract_resume_data
from app.services.analyzer_service import analyze_resume
from app.models.resume_model import ResumeResponse, DuplicateResponse
from app.database.database import get_db
from app.database.models import Candidate
from typing import Union

def check_duplicate(db, name: str):
    return (
        db.query(Candidate)
        .filter(Candidate.name == name)
        .first()
    )

router = APIRouter(prefix="/upload",tags=["Document Upload"])

@router.post(
    "/",
    response_model=Union[ResumeResponse, DuplicateResponse]
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

    extracted_text = extract_text_from_pdf(file_path)[:5000]

    summary = summarize_document(extracted_text)
    resume_data = extract_resume_data(extracted_text)
    analysis = analyze_resume(resume_data)

    existing = None
    if resume_data.get("name") and resume_data["name"] != "Unknown":
        existing = check_duplicate(db, resume_data["name"])

    if existing:
        return DuplicateResponse(
            status="duplicate",
            message="Candidate already exists",
            existing_id=existing.id,
            filename=file.filename
        )

    if (
        resume_data["name"] != "Unknown"
        and analysis["candidate_level"] != "Unknown"
    ):

        candidate = Candidate(
            name=resume_data["name"],
            summary=summary,
            candidate_level=analysis["candidate_level"],
            skill_score=analysis["skill_score"],
            rule_score=analysis["rule_score"],
            ai_score=analysis["ai_score"],
            ai_status=analysis["ai_status"],
            score_breakdown=analysis["score_breakdown"]
        )

        db.add(candidate)
        db.commit()
        db.refresh(candidate)

    return ResumeResponse(
        filename=file.filename,
        message="File uploaded successfully",
        summary=summary,
        resume_data=resume_data,
        analysis=analysis
    )