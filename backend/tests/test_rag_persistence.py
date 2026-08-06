from contextlib import contextmanager
from types import SimpleNamespace
from unittest.mock import Mock, patch

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database.database import Base
from app.database.models import (
    Candidate,
    ResumeChunk
)
from app.rag.embedding_service import (
    EMBEDDING_DIMENSION,
    normalize_embedding
)
from app.services import candidate_service
from app.services.indexing_service import (
    ResumeIndexingError,
    index_resume
)
from app.vector import bm25_service
from app.vector import vector_service


engine = create_engine(
    "sqlite://",
    connect_args={
        "check_same_thread": False
    },
    poolclass=StaticPool
)


@event.listens_for(engine, "connect")
def enable_sqlite_foreign_keys(
    dbapi_connection,
    connection_record
):

    cursor = dbapi_connection.cursor()
    cursor.execute(
        "PRAGMA foreign_keys=ON"
    )
    cursor.close()


TestingSessionLocal = sessionmaker(
    autoflush=False,
    expire_on_commit=False,
    bind=engine
)


@pytest.fixture(autouse=True)
def isolated_database():

    Base.metadata.create_all(
        bind=engine
    )

    yield

    Base.metadata.drop_all(
        bind=engine
    )


def create_candidate(db):

    candidate = Candidate(
        name="Durable RAG Candidate",
        summary="Candidate for durable RAG tests",
        candidate_level="Mid-Level",
        skill_score=80,
        rule_score=80,
        ai_score=80,
        ai_status="success",
        score_breakdown={}
    )
    db.add(candidate)
    db.flush()

    return candidate


def embedding(value=0.0):

    return [
        value
        for _ in range(
            EMBEDDING_DIMENSION
        )
    ]


def test_resume_chunk_model_is_provider_neutral_and_bounded():

    table = ResumeChunk.__table__

    assert table.columns["embedding"].type.dim == 384
    assert table.columns["chunk_text"].nullable is False
    assert table.columns["document_id"].unique is True

    foreign_key = next(
        iter(
            table.columns[
                "candidate_id"
            ].foreign_keys
        )
    )
    assert foreign_key.target_fullname == "candidates.id"
    assert foreign_key.ondelete == "CASCADE"

    constraint_names = {
        constraint.name
        for constraint in table.constraints
    }
    assert "uq_resume_chunks_candidate_chunk" in constraint_names
    assert "ck_resume_chunks_chunk_index" in constraint_names


def test_embedding_dimension_and_values_are_validated():

    assert len(
        normalize_embedding(
            embedding(0.25)
        )
    ) == 384

    with pytest.raises(ValueError):

        normalize_embedding(
            [0.0] * 383
        )

    with pytest.raises(ValueError):

        normalize_embedding(
            [float("nan")] * 384
        )


def test_index_resume_persists_ordered_chunks_and_embeddings():

    with TestingSessionLocal() as db:

        candidate = create_candidate(db)

        with patch(
            "app.services.indexing_service.split_resume",
            return_value=[
                "First durable chunk",
                "Second durable chunk"
            ]
        ), patch(
            "app.services.indexing_service.create_embeddings",
            return_value=[
                embedding(0.1),
                embedding(0.2)
            ]
        ):

            result = index_resume(
                db,
                candidate.id,
                "resume text"
            )

        db.commit()
        candidate_id = candidate.id

    with TestingSessionLocal() as db:

        chunks = (
            db.query(ResumeChunk)
            .filter(
                ResumeChunk.candidate_id
                == candidate_id
            )
            .order_by(
                ResumeChunk.chunk_index
            )
            .all()
        )

        assert result == {
            "candidate_id": str(candidate_id),
            "chunk_count": 2,
            "status": "indexed"
        }
        assert [
            chunk.document_id
            for chunk in chunks
        ] == [
            f"{candidate_id}_0",
            f"{candidate_id}_1"
        ]
        assert [
            chunk.chunk_text
            for chunk in chunks
        ] == [
            "First durable chunk",
            "Second durable chunk"
        ]
        assert all(
            len(chunk.embedding) == 384
            for chunk in chunks
        )


def test_index_resume_rejects_incompatible_embedding_dimension():

    with TestingSessionLocal() as db:

        candidate = create_candidate(db)

        with patch(
            "app.services.indexing_service.split_resume",
            return_value=["one chunk"]
        ), patch(
            "app.services.indexing_service.create_embeddings",
            return_value=[[0.0] * 383]
        ):

            with pytest.raises(ResumeIndexingError):

                index_resume(
                    db,
                    candidate.id,
                    "resume text"
                )

        assert (
            db.query(ResumeChunk).count()
            == 0
        )


def test_bm25_reconstructs_from_durable_chunk_rows():

    chunks = [
        SimpleNamespace(
            document_id="1_0",
            candidate_id=1,
            chunk_text="Python FastAPI Docker"
        ),
        SimpleNamespace(
            document_id="2_0",
            candidate_id=2,
            chunk_text="Accounting finance payroll"
        ),
        SimpleNamespace(
            document_id="3_0",
            candidate_id=3,
            chunk_text="Healthcare nursing compliance"
        )
    ]

    result = bm25_service.search_bm25_chunks(
        "FastAPI Docker",
        chunks,
        n_results=2
    )

    assert result["documents"] == [
        "Python FastAPI Docker"
    ]
    assert result["metadatas"] == [
        {
            "document_id": "1_0",
            "candidate_id": "1"
        }
    ]
    assert result["scores"][0] > 0


def test_bm25_search_reloads_postgresql_source_each_time():

    chunks = [
        SimpleNamespace(
            document_id="1_0",
            candidate_id=1,
            chunk_text="FastAPI PostgreSQL"
        )
    ]

    @contextmanager
    def session_factory():

        yield Mock()

    with patch(
        "app.vector.bm25_service.SessionLocal",
        side_effect=session_factory
    ) as sessions, patch(
        "app.vector.bm25_service."
        "resume_chunk_repository.get_all_chunks",
        return_value=chunks
    ) as load_chunks:

        first = bm25_service.search_bm25(
            "FastAPI"
        )
        second = bm25_service.search_bm25(
            "FastAPI"
        )

    assert first == second
    assert sessions.call_count == 2
    assert load_chunks.call_count == 2


def test_vector_search_uses_repository_cosine_results():

    chunk = SimpleNamespace(
        document_id="1_0",
        candidate_id=1,
        chunk_text="FastAPI vector search"
    )

    @contextmanager
    def session_factory():

        yield Mock()

    with patch(
        "app.vector.vector_service.create_embedding",
        return_value=embedding(0.1)
    ), patch(
        "app.vector.vector_service.SessionLocal",
        side_effect=session_factory
    ), patch(
        "app.vector.vector_service."
        "resume_chunk_repository.search_similar_chunks",
        return_value=[
            (chunk, 0.125)
        ]
    ) as search_chunks:

        result = vector_service.search_documents(
            "FastAPI",
            n_results=5
        )

    assert result == {
        "ids": [["1_0"]],
        "documents": [["FastAPI vector search"]],
        "metadatas": [[{
            "document_id": "1_0",
            "candidate_id": "1"
        }]],
        "distances": [[0.125]]
    }
    assert search_chunks.call_args.args[2] == 5
    assert len(search_chunks.call_args.args[1]) == 384


def test_candidate_deletion_cascades_durable_chunks():

    with TestingSessionLocal() as db:

        candidate = create_candidate(db)
        db.add(
            ResumeChunk(
                candidate_id=candidate.id,
                document_id=f"{candidate.id}_0",
                chunk_index=0,
                chunk_text="durable chunk",
                embedding=embedding(0.1)
            )
        )
        db.commit()
        candidate_id = candidate.id

    with TestingSessionLocal() as db:

        candidate_service.delete_candidate(
            db,
            candidate_id
        )

    with TestingSessionLocal() as db:

        assert db.get(Candidate, candidate_id) is None
        assert (
            db.query(ResumeChunk)
            .filter(
                ResumeChunk.candidate_id
                == candidate_id
            )
            .count()
            == 0
        )
