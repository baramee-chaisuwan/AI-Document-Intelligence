import importlib.util
from pathlib import Path
from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import CheckConstraint, String, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.dependencies import get_current_user
from app.core import security
from app.core.security import (
    create_access_token,
    hash_password
)
from app.database.database import Base, get_db
from app.database.models import Candidate, User
from app.models.candidate_stage import CandidateStage
from main import app


pytestmark = pytest.mark.real_auth


TEST_JWT_SECRET = (
    "test-only-candidate-stage-secret-that-is-"
    "long-enough-for-authorization-tests"
)

MIGRATION_PATH = (
    Path(__file__).parents[1]
    / "alembic"
    / "versions"
    / "e1b4c7d9a260_add_candidate_stage.py"
)

engine = create_engine(
    "sqlite://",
    connect_args={
        "check_same_thread": False
    },
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
def isolated_candidate_stage_database(monkeypatch):

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
def role_headers():

    headers = {}

    with TestingSessionLocal() as db:
        for role in ("admin", "recruiter"):
            user = User(
                email=f"stage-{role}@example.com",
                full_name=f"Stage {role.title()}",
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


def create_candidate() -> Candidate:

    with TestingSessionLocal() as db:
        candidate = Candidate(
            name="Pipeline Candidate",
            summary="Experienced backend engineer",
            candidate_level="Senior",
            skill_score=81,
            rule_score=72,
            ai_score=88,
            ai_status="success",
            score_breakdown={
                "technical": 88
            }
        )
        db.add(candidate)
        db.commit()
        db.refresh(candidate)
        db.expunge(candidate)

    return candidate


def load_migration():

    spec = importlib.util.spec_from_file_location(
        "candidate_stage_migration",
        MIGRATION_PATH
    )
    assert spec is not None
    assert spec.loader is not None
    migration = importlib.util.module_from_spec(
        spec
    )
    spec.loader.exec_module(migration)

    return migration


def test_candidate_stage_model_defaults_to_applied():

    candidate = create_candidate()

    assert candidate.candidate_stage == (
        CandidateStage.APPLIED.value
    )

    column = Candidate.__table__.columns.candidate_stage
    assert isinstance(column.type, String)
    assert column.type.length == 20
    assert column.nullable is False
    assert column.default.arg == CandidateStage.APPLIED.value
    assert str(column.server_default.arg) == "APPLIED"

    constraints = {
        constraint.name: constraint
        for constraint in Candidate.__table__.constraints
        if isinstance(constraint, CheckConstraint)
    }
    assert "ck_candidates_candidate_stage" in constraints


def test_candidate_stage_migration_backfill_contract(
    monkeypatch
):

    migration = load_migration()
    operation = Mock()
    monkeypatch.setattr(migration, "op", operation)

    assert migration.revision == "e1b4c7d9a260"
    assert migration.down_revision == "d7a9e3c5b142"

    migration.upgrade()

    operation.add_column.assert_called_once()
    added_column = operation.add_column.call_args.args[1]
    assert added_column.name == "candidate_stage"
    assert added_column.nullable is True
    assert str(added_column.server_default.arg) == "'APPLIED'"

    operation.execute.assert_called_once()
    assert "WHERE candidate_stage IS NULL" in str(
        operation.execute.call_args.args[0]
    )

    operation.alter_column.assert_called_once()
    assert (
        operation.alter_column.call_args.kwargs["nullable"]
        is False
    )

    operation.create_check_constraint.assert_called_once()
    constraint_call = (
        operation.create_check_constraint.call_args
    )
    assert constraint_call.args[0] == (
        "ck_candidates_candidate_stage"
    )
    assert constraint_call.args[1] == "candidates"
    assert "'APPLIED'" in constraint_call.args[2]
    operation.create_index.assert_not_called()

    operation.reset_mock()
    migration.downgrade()
    operation.drop_constraint.assert_called_once_with(
        "ck_candidates_candidate_stage",
        "candidates",
        type_="check"
    )
    operation.drop_column.assert_called_once_with(
        "candidates",
        "candidate_stage"
    )


@pytest.mark.parametrize("role", ["recruiter", "admin"])
def test_staff_user_can_update_only_candidate_stage(
    client,
    role_headers,
    role
):

    candidate = create_candidate()

    response = client.put(
        f"/candidates/{candidate.id}/stage",
        json={
            "candidate_stage": "INTERVIEW"
        },
        headers=role_headers[role]
    )

    assert response.status_code == 200
    data = response.json()
    assert data["candidate_stage"] == "INTERVIEW"
    assert data["name"] == candidate.name
    assert data["candidate_level"] == candidate.candidate_level
    assert data["skill_score"] == candidate.skill_score
    assert data["rule_score"] == candidate.rule_score
    assert data["ai_score"] == candidate.ai_score
    assert data["ai_status"] == candidate.ai_status
    assert data["score_breakdown"] == candidate.score_breakdown

    with TestingSessionLocal() as db:
        persisted = db.get(Candidate, candidate.id)
        assert persisted is not None
        assert persisted.candidate_stage == "INTERVIEW"
        assert persisted.skill_score == 81
        assert persisted.rule_score == 72
        assert persisted.ai_score == 88


def test_invalid_candidate_stage_is_rejected(
    client,
    role_headers
):

    candidate = create_candidate()

    response = client.put(
        f"/candidates/{candidate.id}/stage",
        json={
            "candidate_stage": "HIRED"
        },
        headers=role_headers["recruiter"]
    )

    assert response.status_code == 422

    with TestingSessionLocal() as db:
        persisted = db.get(Candidate, candidate.id)
        assert persisted is not None
        assert persisted.candidate_stage == "APPLIED"


def test_candidate_stage_update_requires_authentication(
    client
):

    candidate = create_candidate()

    response = client.put(
        f"/candidates/{candidate.id}/stage",
        json={
            "candidate_stage": "SCREENING"
        }
    )

    assert response.status_code == 401


def test_non_staff_role_cannot_update_candidate_stage(
    client
):

    candidate = create_candidate()
    viewer = User(
        id=999,
        email="viewer@example.com",
        full_name="Read Only User",
        role="viewer",
        is_active=True
    )
    app.dependency_overrides[get_current_user] = (
        lambda: viewer
    )

    response = client.put(
        f"/candidates/{candidate.id}/stage",
        json={
            "candidate_stage": "SCREENING"
        }
    )

    assert response.status_code == 403


def test_candidate_stage_update_returns_not_found(
    client,
    role_headers
):

    response = client.put(
        "/candidates/999999/stage",
        json={
            "candidate_stage": "OFFER"
        },
        headers=role_headers["recruiter"]
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Candidate not found"
    }


def test_candidate_list_and_detail_include_stage(
    client,
    role_headers
):

    candidate = create_candidate()
    headers = role_headers["recruiter"]

    list_response = client.get(
        "/candidates/",
        headers=headers
    )
    detail_response = client.get(
        f"/candidates/{candidate.id}",
        headers=headers
    )

    assert list_response.status_code == 200
    listed_candidate = next(
        item
        for item in list_response.json()
        if item["id"] == candidate.id
    )
    assert listed_candidate["candidate_stage"] == "APPLIED"

    assert detail_response.status_code == 200
    assert detail_response.json()["candidate_stage"] == (
        "APPLIED"
    )
