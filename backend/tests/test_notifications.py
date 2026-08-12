import importlib.util
from datetime import timedelta
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core import security
from app.core.security import create_access_token, hash_password
from app.database.database import Base, get_db
from app.database.models import (
    Candidate,
    Notification,
    ResumeProcessingJob,
    User,
    utc_now,
)
from app.models.notification_type import NotificationType
from app.services import (
    notification_service,
    processing_job_service,
    resume_processing_worker,
)
from app.services.resume_processing_worker import (
    ResumeWorkerError,
    WorkerOutcome,
)
from main import app


pytestmark = pytest.mark.real_auth

TEST_JWT_SECRET = (
    "test-only-notification-secret-that-is-long-enough-for-tests"
)
MIGRATION_PATH = (
    Path(__file__).parents[1]
    / "alembic"
    / "versions"
    / "d2f6a9b3c840_add_notifications.py"
)

engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    bind=engine,
)


def override_get_db():
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def isolated_notification_database(monkeypatch):
    Base.metadata.create_all(bind=engine)
    app.dependency_overrides[get_db] = override_get_db
    monkeypatch.setattr(security, "JWT_SECRET_KEY", TEST_JWT_SECRET)

    yield

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def users_and_headers():
    result = {}

    with TestingSessionLocal() as db:
        for label in ("first", "second"):
            user = User(
                email=f"notification-{label}@example.com",
                full_name=f"Notification {label.title()}",
                hashed_password=hash_password("StrongPassword123!"),
                role="recruiter",
                is_active=True,
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            result[label] = {
                "id": user.id,
                "headers": {
                    "Authorization": (
                        f"Bearer {create_access_token(user.id)}"
                    )
                },
            }

    return result


def create_candidate(db, name="Notification Candidate"):
    candidate = Candidate(
        name=name,
        summary="Synthetic backend engineer",
        candidate_level="Senior",
        skill_score=90,
        rule_score=88,
        ai_score=92,
        ai_status="success",
        score_breakdown={},
    )
    db.add(candidate)
    db.commit()
    db.refresh(candidate)
    return candidate


def create_notification(db, user_id, *, title, created_at):
    notification = Notification(
        user_id=user_id,
        type=NotificationType.CANDIDATE_STAGE_CHANGED.value,
        title=title,
        message="Candidate moved to Interview.",
        created_at=created_at,
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification


def test_notification_creation_and_list_are_user_isolated_and_newest_first(
    client,
    users_and_headers,
):
    now = utc_now()

    with TestingSessionLocal() as db:
        older = create_notification(
            db,
            users_and_headers["first"]["id"],
            title="Older",
            created_at=now - timedelta(minutes=1),
        )
        newer = create_notification(
            db,
            users_and_headers["first"]["id"],
            title="Newer",
            created_at=now,
        )
        create_notification(
            db,
            users_and_headers["second"]["id"],
            title="Other user",
            created_at=now + timedelta(minutes=1),
        )

    response = client.get(
        "/notifications",
        headers=users_and_headers["first"]["headers"],
    )

    assert response.status_code == 200
    assert [item["id"] for item in response.json()["notifications"]] == [
        newer.id,
        older.id,
    ]
    assert response.json()["unread_count"] == 2


def test_notification_endpoints_require_authentication(client):
    assert client.get("/notifications").status_code == 401
    assert client.patch("/notifications/read-all").status_code == 401


def test_mark_read_rejects_other_user_and_marks_owner_notification(
    client,
    users_and_headers,
):
    with TestingSessionLocal() as db:
        notification = create_notification(
            db,
            users_and_headers["first"]["id"],
            title="Unread",
            created_at=utc_now(),
        )

    denied = client.patch(
        f"/notifications/{notification.id}/read",
        headers=users_and_headers["second"]["headers"],
    )
    allowed = client.patch(
        f"/notifications/{notification.id}/read",
        headers=users_and_headers["first"]["headers"],
    )

    assert denied.status_code == 404
    assert allowed.status_code == 200
    assert allowed.json()["is_read"] is True


def test_mark_all_read_only_updates_current_user(
    client,
    users_and_headers,
):
    with TestingSessionLocal() as db:
        first = create_notification(
            db,
            users_and_headers["first"]["id"],
            title="First",
            created_at=utc_now(),
        )
        second = create_notification(
            db,
            users_and_headers["second"]["id"],
            title="Second",
            created_at=utc_now(),
        )

    response = client.patch(
        "/notifications/read-all",
        headers=users_and_headers["first"]["headers"],
    )

    assert response.status_code == 200
    assert response.json() == {"marked_read": 1}

    with TestingSessionLocal() as db:
        assert db.get(Notification, first.id).is_read is True
        assert db.get(Notification, second.id).is_read is False


def test_candidate_stage_change_creates_actor_notification(
    client,
    users_and_headers,
):
    with TestingSessionLocal() as db:
        candidate = create_candidate(db)

    response = client.put(
        f"/candidates/{candidate.id}/stage",
        json={"candidate_stage": "INTERVIEW"},
        headers=users_and_headers["first"]["headers"],
    )

    assert response.status_code == 200

    with TestingSessionLocal() as db:
        notification = db.query(Notification).one()
        assert notification.user_id == users_and_headers["first"]["id"]
        assert notification.candidate_id == candidate.id
        assert notification.type == "CANDIDATE_STAGE_CHANGED"


def test_notification_failure_does_not_break_stage_change(
    client,
    users_and_headers,
    monkeypatch,
):
    with TestingSessionLocal() as db:
        candidate = create_candidate(db)

    def fail_notification(*args, **kwargs):
        raise RuntimeError("notification database unavailable")

    monkeypatch.setattr(
        notification_service.notification_repository,
        "create_notification",
        fail_notification,
    )

    response = client.put(
        f"/candidates/{candidate.id}/stage",
        json={"candidate_stage": "OFFER"},
        headers=users_and_headers["first"]["headers"],
    )

    assert response.status_code == 200

    with TestingSessionLocal() as db:
        assert db.get(Candidate, candidate.id).candidate_stage == "OFFER"
        assert db.query(Notification).count() == 0


def worker_message(job_id):
    return {
        "version": 1,
        "processing_job_id": job_id,
        "gcs_object_key": "resumes/synthetic/resume.pdf",
    }


def worker_candidate_processor(db, object_key):
    candidate = Candidate(
        name="Worker Candidate",
        summary="Synthetic worker candidate",
        candidate_level="Senior",
        skill_score=90,
        rule_score=88,
        ai_score=92,
        ai_status="success",
        score_breakdown={},
        resume_storage_key=object_key,
    )
    db.add(candidate)
    db.flush()
    return candidate


def test_worker_completion_notifies_owner_once_on_duplicate_delivery(
    users_and_headers,
):
    with TestingSessionLocal() as db:
        job = processing_job_service.create_processing_job(
            db,
            requested_by=users_and_headers["first"]["id"],
        )
        first = resume_processing_worker.handle_resume_processing_message(
            db,
            worker_message(job.id),
            processor=worker_candidate_processor,
        )
        duplicate = resume_processing_worker.handle_resume_processing_message(
            db,
            worker_message(job.id),
            processor=worker_candidate_processor,
        )

        assert first.outcome == WorkerOutcome.COMPLETED
        assert duplicate.outcome == WorkerOutcome.ALREADY_COMPLETED
        notifications = db.query(Notification).all()
        assert len(notifications) == 1
        assert notifications[0].type == "RESUME_PROCESSING_COMPLETED"
        assert notifications[0].candidate_id == first.candidate_id


def test_worker_terminal_failure_notifies_owner(users_and_headers):
    with TestingSessionLocal() as db:
        job = processing_job_service.create_processing_job(
            db,
            requested_by=users_and_headers["first"]["id"],
        )

        with pytest.raises(ResumeWorkerError):
            resume_processing_worker.handle_resume_processing_message(
                db,
                worker_message(job.id),
                processor=lambda *_: (_ for _ in ()).throw(
                    RuntimeError("synthetic processing failure")
                ),
            )

        persisted_job = db.get(ResumeProcessingJob, job.id)
        notification = db.query(Notification).one()
        assert persisted_job.status == "FAILED"
        assert notification.type == "RESUME_PROCESSING_FAILED"
        assert notification.candidate_id is None


def test_worker_completion_survives_notification_failure(
    users_and_headers,
    monkeypatch,
):
    def fail_notification(*args, **kwargs):
        raise RuntimeError("notification database unavailable")

    monkeypatch.setattr(
        notification_service.notification_repository,
        "create_notification",
        fail_notification,
    )

    with TestingSessionLocal() as db:
        job = processing_job_service.create_processing_job(
            db,
            requested_by=users_and_headers["first"]["id"],
        )
        result = resume_processing_worker.handle_resume_processing_message(
            db,
            worker_message(job.id),
            processor=worker_candidate_processor,
        )

        persisted_job = db.get(ResumeProcessingJob, job.id)
        assert result.outcome == WorkerOutcome.COMPLETED
        assert persisted_job.status == "COMPLETED"
        assert result.candidate_id is not None
        assert db.get(Candidate, result.candidate_id) is not None
        assert db.query(Notification).count() == 0


def test_notification_migration_contract():
    spec = importlib.util.spec_from_file_location(
        "notification_migration",
        MIGRATION_PATH,
    )
    assert spec is not None
    assert spec.loader is not None
    migration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration)

    assert migration.revision == "d2f6a9b3c840"
    assert migration.down_revision == "c8f1d2e5a730"

    table = Notification.__table__
    assert table.columns.user_id.nullable is False
    assert table.columns.candidate_id.nullable is True
    assert table.columns.is_read.nullable is False
    assert table.columns.event_key.unique is True
    assert ResumeProcessingJob.__table__.columns.requested_by.nullable is True
