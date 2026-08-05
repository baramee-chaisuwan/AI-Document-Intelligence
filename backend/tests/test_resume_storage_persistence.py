import importlib.util
from pathlib import Path
from unittest.mock import Mock, call

from sqlalchemy import String, create_engine
from sqlalchemy.orm import sessionmaker

from app.database.database import Base
from app.database.models import Candidate
from app.models.candidate_model import CandidateResponse


_MIGRATION_PATH = (
    Path(__file__).parents[1]
    / "alembic"
    / "versions"
    / "c3e7a91b4f20_add_resume_storage_metadata.py"
)
_MIGRATION_SPEC = importlib.util.spec_from_file_location(
    "resume_storage_metadata_migration",
    _MIGRATION_PATH,
)
assert _MIGRATION_SPEC is not None
assert _MIGRATION_SPEC.loader is not None
migration = importlib.util.module_from_spec(_MIGRATION_SPEC)
_MIGRATION_SPEC.loader.exec_module(migration)


def _candidate(**storage_fields):
    return Candidate(
        name="Storage Test Candidate",
        summary="Candidate used to verify resume storage persistence.",
        candidate_level="Mid-Level",
        skill_score=70,
        rule_score=72,
        ai_score=74,
        ai_status="success",
        score_breakdown={},
        **storage_fields,
    )


def test_candidate_resume_storage_columns_are_nullable_and_bounded():
    s3_key_column = Candidate.__table__.columns["resume_s3_key"]
    filename_column = Candidate.__table__.columns["resume_filename"]

    assert isinstance(s3_key_column.type, String)
    assert s3_key_column.type.length == 1024
    assert s3_key_column.nullable is True

    assert isinstance(filename_column.type, String)
    assert filename_column.type.length == 255
    assert filename_column.nullable is True


def test_candidate_resume_storage_fields_persist_and_legacy_rows_remain_valid():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(bind=engine)

    with session_factory() as session:
        stored_candidate = _candidate(
            resume_s3_key="resumes/42/document-hash.pdf",
            resume_filename="candidate-resume.pdf",
        )
        legacy_candidate = _candidate()

        session.add_all([stored_candidate, legacy_candidate])
        session.commit()
        session.expire_all()

        persisted = session.get(Candidate, stored_candidate.id)
        persisted_legacy = session.get(Candidate, legacy_candidate.id)

        assert persisted.resume_s3_key == "resumes/42/document-hash.pdf"
        assert persisted.resume_filename == "candidate-resume.pdf"
        assert persisted_legacy.resume_s3_key is None
        assert persisted_legacy.resume_filename is None


def test_public_candidate_response_does_not_expose_storage_metadata():
    assert "resume_s3_key" not in CandidateResponse.model_fields
    assert "resume_filename" not in CandidateResponse.model_fields


def test_resume_storage_migration_revision_chain():
    assert migration.revision == "c3e7a91b4f20"
    assert migration.down_revision == "a8f4c2d9e731"
    assert migration.branch_labels is None
    assert migration.depends_on is None


def test_resume_storage_migration_upgrade_adds_nullable_columns(monkeypatch):
    operation = Mock()
    monkeypatch.setattr(migration, "op", operation)

    migration.upgrade()

    assert operation.add_column.call_count == 2

    table_name, s3_key_column = operation.add_column.call_args_list[0].args
    assert table_name == "candidates"
    assert s3_key_column.name == "resume_s3_key"
    assert isinstance(s3_key_column.type, String)
    assert s3_key_column.type.length == 1024
    assert s3_key_column.nullable is True

    table_name, filename_column = operation.add_column.call_args_list[1].args
    assert table_name == "candidates"
    assert filename_column.name == "resume_filename"
    assert isinstance(filename_column.type, String)
    assert filename_column.type.length == 255
    assert filename_column.nullable is True


def test_resume_storage_migration_downgrade_removes_both_columns(monkeypatch):
    operation = Mock()
    monkeypatch.setattr(migration, "op", operation)

    migration.downgrade()

    assert operation.drop_column.call_args_list == [
        call("candidates", "resume_filename"),
        call("candidates", "resume_s3_key"),
    ]
