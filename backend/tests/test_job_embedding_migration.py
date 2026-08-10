import importlib.util
from pathlib import Path
from unittest.mock import Mock

from pgvector.sqlalchemy import Vector

from app.database.models import Job


MIGRATION_PATH = (
    Path(__file__).parents[1]
    / "alembic"
    / "versions"
    / "d7a9e3c5b142_add_job_embedding.py"
)


def load_migration():

    spec = importlib.util.spec_from_file_location(
        "job_embedding_migration",
        MIGRATION_PATH
    )
    assert spec is not None
    assert spec.loader is not None
    migration = importlib.util.module_from_spec(
        spec
    )
    spec.loader.exec_module(migration)

    return migration


def test_job_embedding_model_contract():

    embedding = Job.__table__.columns.embedding

    assert isinstance(embedding.type, Vector)
    assert embedding.type.dim == 384
    assert embedding.nullable is True


def test_job_embedding_migration_contract(
    monkeypatch
):

    migration = load_migration()
    operation = Mock()
    monkeypatch.setattr(
        migration,
        "op",
        operation
    )

    assert migration.revision == "d7a9e3c5b142"
    assert migration.down_revision == "c4f8a2d1e730"

    migration.upgrade()
    operation.add_column.assert_called_once()
    add_column = operation.add_column.call_args
    assert add_column.args[0] == "jobs"
    embedding = add_column.args[1]
    assert embedding.name == "embedding"
    assert isinstance(embedding.type, Vector)
    assert embedding.type.dim == 384
    assert embedding.nullable is True
    operation.create_index.assert_not_called()

    operation.reset_mock()
    migration.downgrade()
    operation.drop_column.assert_called_once_with(
        "jobs",
        "embedding"
    )
