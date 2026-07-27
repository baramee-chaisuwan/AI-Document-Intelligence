from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session

print("UPLOAD A")
from app.services.pdf_service import extract_text_from_pdf

print("UPLOAD B")
from app.services.gemini_service import summarize_document

print("UPLOAD C")
from app.services.extraction_service import extract_resume_data

print("UPLOAD D")
from app.services.analyzer_service import analyze_resume

print("UPLOAD E")
from app.models.resume_model import ResumeResponse, DuplicateResponse

print("UPLOAD F")
from app.database.database import get_db

print("UPLOAD G")
from app.database.models import Candidate

print("UPLOAD H")
from app.services.indexing_service import index_resume

print("UPLOAD I")
from typing import Union

print("UPLOAD J")


def check_duplicate(db, name: str):
    return (
        db.query(Candidate)
        .filter(Candidate.name == name)
        .first()
    )


router = APIRouter(
    prefix="/upload",
    tags=["Resume Upload"]
)


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

    file_bytes = file.file.read()

    extracted_text = extract_text_from_pdf(file_bytes)[:5000]

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

        index_resume(
            document_id=str(candidate.id),
            resume_text=extracted_text
        )

    return ResumeResponse(
        filename=file.filename,
        message="File uploaded successfully",
        summary=summary,
        resume_data=resume_data,
        analysis=analysis
    )