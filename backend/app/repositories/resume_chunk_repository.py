from sqlalchemy.orm import Session

from app.database.models import ResumeChunk


def replace_candidate_chunks(
    db: Session,
    candidate_id: int,
    chunks: list[ResumeChunk]
) -> None:

    (
        db.query(ResumeChunk)
        .filter(
            ResumeChunk.candidate_id == candidate_id
        )
        .delete(
            synchronize_session=False
        )
    )

    db.add_all(
        chunks
    )
    db.flush()


def search_similar_chunks(
    db: Session,
    query_embedding: list[float],
    limit: int
):

    cosine_distance = (
        ResumeChunk.embedding.cosine_distance(
            query_embedding
        )
    )

    return (
        db.query(
            ResumeChunk,
            cosine_distance.label(
                "distance"
            )
        )
        .order_by(
            cosine_distance.asc(),
            ResumeChunk.id.asc()
        )
        .limit(limit)
        .all()
    )


def get_candidate_chunks(
    db: Session,
    candidate_id: int
):

    return (
        db.query(ResumeChunk)
        .filter(
            ResumeChunk.candidate_id == candidate_id
        )
        .order_by(
            ResumeChunk.chunk_index.asc(),
            ResumeChunk.id.asc()
        )
        .all()
    )


def get_all_chunks(
    db: Session
):

    return (
        db.query(ResumeChunk)
        .order_by(
            ResumeChunk.candidate_id.asc(),
            ResumeChunk.chunk_index.asc(),
            ResumeChunk.id.asc()
        )
        .all()
    )
