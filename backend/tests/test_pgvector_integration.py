import os

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.models import (
    Candidate,
    ResumeChunk
)
from app.repositories.resume_chunk_repository import (
    search_similar_chunks
)


PGVECTOR_TEST_DATABASE_URL = os.getenv(
    "PGVECTOR_TEST_DATABASE_URL"
)


pytestmark = pytest.mark.skipif(
    not PGVECTOR_TEST_DATABASE_URL,
    reason=(
        "PGVECTOR_TEST_DATABASE_URL is required for "
        "the disposable pgvector integration test"
    )
)


def vector(axis: int):

    values = [0.0] * 384
    values[axis] = 1.0

    return values


def test_pgvector_cosine_search_and_database_cascade():

    engine = create_engine(
        PGVECTOR_TEST_DATABASE_URL
    )
    connection = engine.connect()
    transaction = connection.begin()
    session_factory = sessionmaker(
        bind=connection,
        expire_on_commit=False
    )
    db = session_factory()

    try:

        first = Candidate(
            name="Pgvector Candidate One",
            summary="First candidate",
            candidate_level="Senior",
            skill_score=90,
            rule_score=90,
            ai_score=90,
            ai_status="success",
            score_breakdown={}
        )
        second = Candidate(
            name="Pgvector Candidate Two",
            summary="Second candidate",
            candidate_level="Junior",
            skill_score=50,
            rule_score=50,
            ai_score=50,
            ai_status="success",
            score_breakdown={}
        )
        db.add_all([
            first,
            second
        ])
        db.flush()
        db.add_all([
            ResumeChunk(
                candidate_id=first.id,
                document_id=f"{first.id}_0",
                chunk_index=0,
                chunk_text="nearest chunk",
                embedding=vector(0)
            ),
            ResumeChunk(
                candidate_id=second.id,
                document_id=f"{second.id}_0",
                chunk_index=0,
                chunk_text="distant chunk",
                embedding=vector(1)
            )
        ])
        db.flush()

        results = search_similar_chunks(
            db,
            vector(0),
            2
        )

        assert results[0][0].candidate_id == first.id
        assert float(results[0][1]) == pytest.approx(0.0)
        assert float(results[1][1]) == pytest.approx(1.0)

        db.delete(first)
        db.flush()

        assert (
            db.query(ResumeChunk)
            .filter(
                ResumeChunk.candidate_id == first.id
            )
            .count()
            == 0
        )

    finally:

        db.close()
        transaction.rollback()
        connection.close()
        engine.dispose()
