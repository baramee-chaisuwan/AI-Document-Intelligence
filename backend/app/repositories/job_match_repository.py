from dataclasses import dataclass

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database.models import (
    Candidate,
    ResumeChunk
)


@dataclass(frozen=True)
class CandidateMatchData:

    candidate_id: int
    candidate_name: str
    cosine_distances: list[float | None]
    resume_text: str


def get_candidate_match_data(
    db: Session,
    job_embedding: list[float]
) -> list[CandidateMatchData]:

    cosine_distance = (
        ResumeChunk.embedding.cosine_distance(
            job_embedding
        )
    )

    ranked_chunks = (
        db.query(
            ResumeChunk.candidate_id.label(
                "candidate_id"
            ),
            cosine_distance.label(
                "cosine_distance"
            ),
            func.row_number().over(
                partition_by=(
                    ResumeChunk.candidate_id
                ),
                order_by=(
                    cosine_distance.asc(),
                    ResumeChunk.id.asc()
                )
            ).label("chunk_rank")
        )
        .filter(
            ResumeChunk.embedding.isnot(None)
        )
        .subquery()
    )

    top_chunk_rows = (
        db.query(
            Candidate.id.label("candidate_id"),
            Candidate.name.label(
                "candidate_name"
            ),
            ranked_chunks.c.cosine_distance,
            ranked_chunks.c.chunk_rank
        )
        .join(
            ranked_chunks,
            ranked_chunks.c.candidate_id
            == Candidate.id
        )
        .filter(
            ranked_chunks.c.chunk_rank <= 3
        )
        .order_by(
            Candidate.id.asc(),
            ranked_chunks.c.chunk_rank.asc()
        )
        .all()
    )

    if not top_chunk_rows:
        return []

    candidate_ids = sorted({
        row.candidate_id
        for row in top_chunk_rows
    })

    text_rows = (
        db.query(
            ResumeChunk.candidate_id,
            ResumeChunk.chunk_text
        )
        .filter(
            ResumeChunk.candidate_id.in_(
                candidate_ids
            )
        )
        .order_by(
            ResumeChunk.candidate_id.asc(),
            ResumeChunk.chunk_index.asc(),
            ResumeChunk.id.asc()
        )
        .all()
    )

    candidate_names = {}
    candidate_distances = {
        candidate_id: []
        for candidate_id in candidate_ids
    }
    candidate_texts = {
        candidate_id: []
        for candidate_id in candidate_ids
    }

    for row in top_chunk_rows:
        candidate_names[row.candidate_id] = (
            row.candidate_name
        )
        candidate_distances[
            row.candidate_id
        ].append(row.cosine_distance)

    for row in text_rows:
        if (
            row.candidate_id in candidate_texts
            and isinstance(row.chunk_text, str)
            and row.chunk_text.strip()
        ):
            candidate_texts[
                row.candidate_id
            ].append(row.chunk_text.strip())

    return [
        CandidateMatchData(
            candidate_id=candidate_id,
            candidate_name=(
                candidate_names[candidate_id]
            ),
            cosine_distances=(
                candidate_distances[candidate_id]
            ),
            resume_text="\n".join(
                candidate_texts[candidate_id]
            )
        )
        for candidate_id in candidate_ids
    ]
