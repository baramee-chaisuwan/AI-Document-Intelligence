import importlib.util
from pathlib import Path
from unittest.mock import Mock, call

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text
)

from app.database.models import Job


MIGRATION_PATH = (
    Path(__file__).parents[1]
    / "alembic"
    / "versions"
    / "c4f8a2d1e730_add_jobs_table.py"
)


def load_migration():

    spec = importlib.util.spec_from_file_location(
        "jobs_migration",
        MIGRATION_PATH
    )
    assert spec is not None
    assert spec.loader is not None
    migration = importlib.util.module_from_spec(
        spec
    )
    spec.loader.exec_module(migration)

    return migration


def test_job_model_contract():

    columns = Job.__table__.columns

    assert isinstance(columns.id.type, Integer)
    assert isinstance(columns.title.type, String)
    assert columns.title.type.length == 255
    assert isinstance(columns.description.type, Text)
    assert isinstance(
        columns.extracted_requirements.type,
        JSON
    )
    assert columns.extracted_requirements.nullable is False
    assert isinstance(columns.created_by.type, Integer)
    assert isinstance(columns.created_at.type, DateTime)
    assert columns.created_at.type.timezone is True

    foreign_key = next(
        iter(columns.created_by.foreign_keys)
    )
    assert isinstance(foreign_key, ForeignKey)
    assert foreign_key.target_fullname == "users.id"
    assert foreign_key.ondelete == "RESTRICT"


def test_job_migration_revision_and_operations(
    monkeypatch
):

    migration = load_migration()
    operation = Mock()
    monkeypatch.setattr(
        migration,
        "op",
        operation
    )

    assert migration.revision == "c4f8a2d1e730"
    assert migration.down_revision == "b9d6f2a7c410"

    migration.upgrade()
    operation.create_table.assert_called_once()
    assert (
        operation.create_table.call_args.args[0]
        == "jobs"
    )
    assert operation.create_index.call_args_list == [
        call(
            "ix_jobs_created_by",
            "jobs",
            ["created_by"],
            unique=False
        )
    ]

    operation.reset_mock()
    migration.downgrade()
    assert operation.drop_index.call_args_list == [
        call(
            "ix_jobs_created_by",
            table_name="jobs"
        )
    ]
    operation.drop_table.assert_called_once_with(
        "jobs"
    )
