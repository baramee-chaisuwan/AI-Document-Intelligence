import csv
import io

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database.models import Candidate

router = APIRouter(
    prefix="/export",
    tags=["Export"]
)

@router.get(
    "/csv",
    summary="Export candidates to CSV",
    description="Downloads all candidates as a CSV file."
)
def export_candidates_csv(db: Session = Depends(get_db)):
    candidates = db.query(Candidate).all()

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        "id",
        "name",
        "candidate_level",
        "skill_score"
    ])

    for c in candidates:
        writer.writerow([
            c.id,
            c.name,
            c.candidate_level,
            c.skill_score
        ])

    output.seek(0)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=candidates.csv",
        }
    )