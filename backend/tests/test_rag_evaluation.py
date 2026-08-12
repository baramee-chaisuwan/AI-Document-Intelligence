import importlib.util
import json
from pathlib import Path
from unittest.mock import Mock

from sqlalchemy import CheckConstraint, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database.database import Base
from app.database.models import RAGEvaluation
from app.rag import rag_chain
from app.services import rag_evaluation_service


MIGRATION_PATH = (
    Path(__file__).parents[1]
    / "alembic"
    / "versions"
    / "b7e2c9f4a610_add_rag_evaluations.py"
)

engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    bind=engine
)


def setup_function():

    Base.metadata.create_all(bind=engine)


def teardown_function():

    Base.metadata.drop_all(bind=engine)


def retrieval_results():

    return {
        "documents": [["full private resume chunk"]],
        "metadatas": [[{
            "candidate_id": "123",
            "document_id": "123_0",
            "chunk_index": 0,
            "retrieval_sources": ["vector", "bm25"],
            "candidate_name": "Must Not Persist",
            "email": "private@example.com",
            "gcs_object_key": "resumes/private.pdf",
            "authorization": "Bearer private-token",
            "password": "private-password"
        }]],
        "scores": [[0.031]]
    }


def test_evaluation_service_persists_normalized_safe_record():

    with TestingSessionLocal() as db:
        persisted = (
            rag_evaluation_service
            .persist_evaluation_safely(
                db,
                user_query="  Find a Python engineer  ",
                generated_answer={"candidate_id": "123"},
                retrieved_results=retrieval_results(),
                retrieval_latency_ms=-5,
                generation_latency_ms=12.345,
                total_latency_ms=float("nan"),
                operation="recommendation"
            )
        )

        assert persisted is not None
        evaluation_id = persisted.id

    with TestingSessionLocal() as db:
        evaluation = db.get(RAGEvaluation, evaluation_id)

        assert evaluation.user_query == "Find a Python engineer"
        assert json.loads(evaluation.generated_answer) == {
            "candidate_id": "123"
        }
        assert evaluation.operation == "recommendation"
        assert evaluation.retrieval_latency_ms == 0.0
        assert evaluation.generation_latency_ms == 12.35
        assert evaluation.total_latency_ms == 0.0
        assert evaluation.retrieved_count == 1
        assert evaluation.retrieved_documents == [{
            "rank": 1,
            "candidate_id": 123,
            "document_id": "123_0",
            "chunk_index": 0,
            "score": 0.031,
            "retrieval_sources": ["vector", "bm25"]
        }]

        serialized = json.dumps(
            evaluation.retrieved_documents
        )
        assert "full private resume chunk" not in serialized
        assert "candidate_name" not in serialized
        assert "private@example.com" not in serialized
        assert "resumes/private.pdf" not in serialized
        assert "private-token" not in serialized
        assert "private-password" not in serialized


def test_assistant_persists_one_evaluation_after_generation(
    monkeypatch
):

    chain = Mock()
    chain.invoke.return_value = "Supported answer"
    monkeypatch.setattr(
        rag_chain,
        "hybrid_search",
        lambda **kwargs: retrieval_results()
    )
    monkeypatch.setattr(
        rag_chain,
        "get_assistant_rag_chain",
        lambda: chain
    )

    with TestingSessionLocal() as db:
        answer = rag_chain.ask_rag(
            "Who matches?",
            db=db
        )

    assert answer == "Supported answer"

    with TestingSessionLocal() as db:
        evaluations = db.query(RAGEvaluation).all()

        assert len(evaluations) == 1
        assert evaluations[0].user_query == "Who matches?"
        assert evaluations[0].generated_answer == "Supported answer"
        assert evaluations[0].operation == "assistant"
        assert evaluations[0].retrieved_count == 1


def test_recommendation_persists_one_labeled_evaluation(
    monkeypatch
):

    chain = Mock()
    chain.invoke.return_value = {
        "candidate_id": "123",
        "candidate_name": "Selected Candidate",
        "match_score": 90,
        "strengths": ["Python"],
        "relevant_experience": ["Backend systems"],
        "reason": "Supported by retrieved evidence"
    }
    monkeypatch.setattr(
        rag_chain,
        "hybrid_search",
        lambda **kwargs: retrieval_results()
    )
    monkeypatch.setattr(
        rag_chain,
        "get_candidate_documents",
        lambda candidate_id: {
            "documents": ["private candidate context"]
        }
    )
    monkeypatch.setattr(
        rag_chain,
        "get_recommendation_chain",
        lambda: chain
    )

    with TestingSessionLocal() as db:
        answer = rag_chain.ask_recommendation(
            "Recommend a Python engineer",
            db=db
        )

    assert answer["candidate_id"] == "123"

    with TestingSessionLocal() as db:
        evaluations = db.query(RAGEvaluation).all()

        assert len(evaluations) == 1
        assert evaluations[0].operation == "recommendation"
        assert evaluations[0].retrieved_count == 1
        assert "private candidate context" not in (
            json.dumps(evaluations[0].retrieved_documents)
        )


def test_evaluation_failure_preserves_successful_rag_answer(
    monkeypatch
):

    chain = Mock()
    chain.invoke.return_value = "Successful answer"
    monkeypatch.setattr(
        rag_chain,
        "hybrid_search",
        lambda **kwargs: retrieval_results()
    )
    monkeypatch.setattr(
        rag_chain,
        "get_assistant_rag_chain",
        lambda: chain
    )
    monkeypatch.setattr(
        rag_evaluation_service.rag_evaluation_repository,
        "create_rag_evaluation",
        Mock(side_effect=RuntimeError("database detail"))
    )

    with TestingSessionLocal() as db:
        rollback = Mock(wraps=db.rollback)
        db.rollback = rollback

        answer = rag_chain.ask_rag(
            "Who matches?",
            db=db
        )

        assert answer == "Successful answer"
        assert rollback.call_count == 1
        assert db.query(RAGEvaluation).count() == 0


def test_rag_evaluation_model_and_migration_contract(monkeypatch):

    table = RAGEvaluation.__table__
    expected_columns = {
        "id",
        "user_query",
        "generated_answer",
        "retrieved_documents",
        "retrieval_latency_ms",
        "generation_latency_ms",
        "total_latency_ms",
        "retrieved_count",
        "operation",
        "retrieval_rating",
        "answer_rating",
        "feedback_note",
        "evaluated_at",
        "created_at"
    }

    assert set(table.columns.keys()) == expected_columns
    assert table.columns.user_query.nullable is False
    assert table.columns.generated_answer.nullable is False
    assert table.columns.retrieved_documents.nullable is False
    assert table.columns.created_at.nullable is False
    assert "ix_rag_evaluations_created_at" in {
        index.name for index in table.indexes
    }
    assert {
        constraint.name
        for constraint in table.constraints
        if isinstance(constraint, CheckConstraint)
    } >= {
        "ck_rag_evaluations_operation",
        "ck_rag_evaluations_retrieved_count",
        "ck_rag_evaluations_nonnegative_latency"
    }

    spec = importlib.util.spec_from_file_location(
        "rag_evaluation_migration",
        MIGRATION_PATH
    )
    assert spec is not None and spec.loader is not None
    migration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration)
    operation = Mock()
    monkeypatch.setattr(migration, "op", operation)

    assert migration.revision == "b7e2c9f4a610"
    assert migration.down_revision == "a3d8c6e1f520"

    migration.upgrade()
    operation.create_table.assert_called_once()
    operation.create_index.assert_called_once_with(
        "ix_rag_evaluations_created_at",
        "rag_evaluations",
        ["created_at"],
        unique=False
    )

    operation.reset_mock()
    migration.downgrade()
    operation.drop_index.assert_called_once()
    operation.drop_table.assert_called_once_with(
        "rag_evaluations"
    )
