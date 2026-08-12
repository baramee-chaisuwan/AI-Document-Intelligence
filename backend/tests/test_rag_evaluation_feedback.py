import importlib.util
from pathlib import Path
from unittest.mock import Mock, call

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import CheckConstraint, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core import security
from app.core.security import create_access_token, hash_password
from app.database.database import Base, get_db
from app.database.models import RAGEvaluation, User
from app.models.rag_evaluation_model import (
    MAX_FEEDBACK_NOTE_LENGTH
)
from main import app


pytestmark = pytest.mark.real_auth

TEST_JWT_SECRET = (
    "test-only-rag-feedback-secret-that-is-"
    "long-enough-for-authentication"
)
MIGRATION_PATH = (
    Path(__file__).parents[1]
    / "alembic"
    / "versions"
    / "c8f1d2e5a730_add_rag_evaluation_feedback.py"
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


def override_get_db():

    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def isolated_database(monkeypatch):

    Base.metadata.create_all(bind=engine)
    app.dependency_overrides[get_db] = override_get_db
    monkeypatch.setattr(
        security,
        "JWT_SECRET_KEY",
        TEST_JWT_SECRET
    )

    yield

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():

    return TestClient(app)


@pytest.fixture
def staff_headers():

    headers = {}

    with TestingSessionLocal() as db:
        for role in ("admin", "recruiter"):
            user = User(
                email=f"feedback-{role}@example.com",
                full_name=f"Feedback {role.title()}",
                hashed_password=hash_password(
                    "StrongPassword123!"
                ),
                role=role,
                is_active=True
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            headers[role] = {
                "Authorization": (
                    "Bearer "
                    f"{create_access_token(user.id)}"
                )
            }

    return headers


def create_evaluation() -> int:

    with TestingSessionLocal() as db:
        evaluation = RAGEvaluation(
            user_query="Private evaluation query",
            generated_answer="Private generated answer",
            retrieved_documents=[{
                "candidate_id": 7,
                "document_id": "7_0"
            }],
            retrieval_latency_ms=10.0,
            generation_latency_ms=20.0,
            total_latency_ms=30.0,
            retrieved_count=1,
            operation="assistant"
        )
        db.add(evaluation)
        db.commit()
        db.refresh(evaluation)

        return evaluation.id


@pytest.mark.parametrize("role", ["admin", "recruiter"])
def test_staff_updates_feedback_and_response_is_safe(
    client,
    staff_headers,
    role
):

    evaluation_id = create_evaluation()
    response = client.patch(
        f"/rag-evaluations/{evaluation_id}/feedback",
        json={
            "retrieval_rating": 4,
            "answer_rating": 5,
            "feedback_note": (
                "  Relevant evidence and accurate answer  "
            )
        },
        headers=staff_headers[role]
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": evaluation_id,
        "operation": "assistant",
        "retrieval_rating": 4,
        "answer_rating": 5,
        "feedback_note": (
            "Relevant evidence and accurate answer"
        ),
        "evaluated_at": response.json()["evaluated_at"]
    }
    assert response.json()["evaluated_at"] is not None
    assert "user_query" not in response.json()
    assert "generated_answer" not in response.json()
    assert "retrieved_documents" not in response.json()

    with TestingSessionLocal() as db:
        evaluation = db.get(RAGEvaluation, evaluation_id)
        assert evaluation.retrieval_rating == 4
        assert evaluation.answer_rating == 5
        assert evaluation.feedback_note == (
            "Relevant evidence and accurate answer"
        )
        assert evaluation.evaluated_at is not None


@pytest.mark.parametrize(
    "field,value",
    [
        ("retrieval_rating", 0),
        ("retrieval_rating", 6),
        ("answer_rating", 0),
        ("answer_rating", 6)
    ]
)
def test_invalid_rating_is_rejected(
    client,
    staff_headers,
    field,
    value
):

    evaluation_id = create_evaluation()
    payload = {
        "retrieval_rating": 3,
        "answer_rating": 3,
        field: value
    }

    response = client.patch(
        f"/rag-evaluations/{evaluation_id}/feedback",
        json=payload,
        headers=staff_headers["recruiter"]
    )

    assert response.status_code == 422


def test_missing_evaluation_returns_404(
    client,
    staff_headers
):

    response = client.patch(
        "/rag-evaluations/999/feedback",
        json={
            "retrieval_rating": 3,
            "answer_rating": 4
        },
        headers=staff_headers["recruiter"]
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "RAG evaluation not found"
    }


def test_feedback_requires_authenticated_staff(client):

    evaluation_id = create_evaluation()
    response = client.patch(
        f"/rag-evaluations/{evaluation_id}/feedback",
        json={
            "retrieval_rating": 3,
            "answer_rating": 4
        }
    )

    assert response.status_code == 401


def test_legacy_unrated_evaluation_remains_valid():

    evaluation_id = create_evaluation()

    with TestingSessionLocal() as db:
        evaluation = db.get(RAGEvaluation, evaluation_id)
        assert evaluation.retrieval_rating is None
        assert evaluation.answer_rating is None
        assert evaluation.feedback_note is None
        assert evaluation.evaluated_at is None


def test_feedback_note_blank_normalization_and_length_limit(
    client,
    staff_headers
):

    evaluation_id = create_evaluation()
    blank_response = client.patch(
        f"/rag-evaluations/{evaluation_id}/feedback",
        json={
            "retrieval_rating": 3,
            "answer_rating": 4,
            "feedback_note": "   "
        },
        headers=staff_headers["admin"]
    )
    long_response = client.patch(
        f"/rag-evaluations/{evaluation_id}/feedback",
        json={
            "retrieval_rating": 3,
            "answer_rating": 4,
            "feedback_note": (
                "x" * (MAX_FEEDBACK_NOTE_LENGTH + 1)
            )
        },
        headers=staff_headers["admin"]
    )

    assert blank_response.status_code == 200
    assert blank_response.json()["feedback_note"] is None
    assert long_response.status_code == 422


def test_feedback_model_and_migration_contract(monkeypatch):

    table = RAGEvaluation.__table__
    assert table.columns.retrieval_rating.nullable is True
    assert table.columns.answer_rating.nullable is True
    assert table.columns.feedback_note.nullable is True
    assert table.columns.feedback_note.type.length == 1000
    assert table.columns.evaluated_at.nullable is True
    assert {
        constraint.name
        for constraint in table.constraints
        if isinstance(constraint, CheckConstraint)
    } >= {
        "ck_rag_evaluations_retrieval_rating",
        "ck_rag_evaluations_answer_rating"
    }

    spec = importlib.util.spec_from_file_location(
        "rag_evaluation_feedback_migration",
        MIGRATION_PATH
    )
    assert spec is not None and spec.loader is not None
    migration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration)
    operation = Mock()
    monkeypatch.setattr(migration, "op", operation)

    assert migration.revision == "c8f1d2e5a730"
    assert migration.down_revision == "b7e2c9f4a610"

    migration.upgrade()
    assert operation.add_column.call_count == 4
    assert operation.create_check_constraint.call_args_list == [
        call(
            "ck_rag_evaluations_retrieval_rating",
            "rag_evaluations",
            (
                "retrieval_rating IS NULL OR "
                "retrieval_rating BETWEEN 1 AND 5"
            )
        ),
        call(
            "ck_rag_evaluations_answer_rating",
            "rag_evaluations",
            (
                "answer_rating IS NULL OR "
                "answer_rating BETWEEN 1 AND 5"
            )
        )
    ]

    operation.reset_mock()
    migration.downgrade()
    assert operation.drop_constraint.call_count == 2
    assert operation.drop_column.call_count == 4
