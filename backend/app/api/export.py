import csv
import io
from datetime import datetime

from fastapi import (
    APIRouter,
    Depends
)
from fastapi.responses import (
    StreamingResponse
)
from sqlalchemy.orm import Session

from app.api.dependencies import (
    get_current_admin_user
)
from app.database.database import get_db
from app.database.models import Candidate

router = APIRouter(
    prefix="/export",
    tags=["Export"]
)

DANGEROUS_CSV_PREFIXES = (
    "=",
    "+",
    "-",
    "@"
)

def sanitize_csv_value(
    value
):

    if value is None:
        return ""


    text = str(
        value
    )


    stripped_text = (
        text.lstrip()
    )


    if stripped_text.startswith(
        DANGEROUS_CSV_PREFIXES
    ):

        return "'" + text


    return text

@router.get(
    "/csv",
    dependencies=[
        Depends(get_current_admin_user)
    ],
    summary="Export candidates to CSV",
    description=(
        "Downloads all candidates "
        "as a UTF-8 CSV file."
    )
)
def export_candidates_csv(
    db: Session = Depends(get_db)
):

    candidates = (
        db.query(Candidate)
        .order_by(
            Candidate.skill_score.desc(),
            Candidate.id.asc()
        )
        .all()
    )

    output = io.StringIO(
        newline=""
    )

    output.write(
        "\ufeff"
    )


    writer = csv.writer(
        output,
        quoting=csv.QUOTE_MINIMAL
    )

    writer.writerow([
        "id",
        "name",
        "candidate_level",
        "skill_score",
        "rule_score",
        "ai_score",
        "ai_status",
        "summary",
        "created_at",
        "updated_at"
    ])

    for candidate in candidates:

        writer.writerow([
            candidate.id,
            sanitize_csv_value(
                candidate.name
            ),
            sanitize_csv_value(
                candidate.candidate_level
            ),
            candidate.skill_score,
            candidate.rule_score,
            candidate.ai_score,
            sanitize_csv_value(
                candidate.ai_status
            ),
            sanitize_csv_value(
                candidate.summary
            ),
            (
                candidate.created_at.isoformat()
                if candidate.created_at
                else ""
            ),
            (
                candidate.updated_at.isoformat()
                if candidate.updated_at
                else ""
            )
        ])

    output.seek(
        0
    )

    filename = (
        "candidates_"
        + datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )
        + ".csv"
    )

    response = StreamingResponse(
        iter([
            output.getvalue()
        ]),
        media_type=(
            "text/csv; charset=utf-8"
        ),
        headers={
            "Content-Disposition": (
                f'attachment; filename="{filename}"'
            ),
            "Cache-Control": "no-store"
        }
    )

    return response
