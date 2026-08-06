import importlib.util
from pathlib import Path
from unittest.mock import Mock, call

from pgvector.sqlalchemy import Vector


MIGRATION_PATH = (
    Path(__file__).parents[1]
    / "alembic"
    / "versions"
    / "f7c2a9e4b610_add_durable_resume_chunks.py"
)
MIGRATION_SPEC = importlib.util.spec_from_file_location(
    "durable_resume_chunks_migration",
    MIGRATION_PATH
)
assert MIGRATION_SPEC is not None
assert MIGRATION_SPEC.loader is not None
migration = importlib.util.module_from_spec(
    MIGRATION_SPEC
)
MIGRATION_SPEC.loader.exec_module(
    migration
)


def test_rag_migration_revision_chain():

    assert migration.revision == "f7c2a9e4b610"
    assert migration.down_revision == "e6b1c4d8a2f7"


def test_rag_migration_enables_vector_and_creates_table(
    monkeypatch
):

    operation = Mock()
    monkeypatch.setattr(
        migration,
        "op",
        operation
    )

    migration.upgrade()

    operation.execute.assert_called_once_with(
        "CREATE EXTENSION IF NOT EXISTS vector"
    )
    create_table = operation.create_table.call_args
    assert create_table.args[0] == "resume_chunks"

    columns = {
        argument.name: argument
        for argument in create_table.args[1:]
        if hasattr(argument, "type")
    }
    assert isinstance(
        columns["embedding"].type,
        Vector
    )
    assert columns["embedding"].type.dim == 384

    index_calls = operation.create_index.call_args_list
    assert index_calls[0] == call(
        "ix_resume_chunks_candidate_id",
        "resume_chunks",
        ["candidate_id"],
        unique=False
    )
    assert (
        index_calls[1].kwargs[
            "postgresql_using"
        ]
        == "hnsw"
    )
    assert index_calls[1].kwargs[
        "postgresql_ops"
    ] == {
        "embedding": "vector_cosine_ops"
    }


def test_rag_migration_downgrade_removes_application_table(
    monkeypatch
):

    operation = Mock()
    monkeypatch.setattr(
        migration,
        "op",
        operation
    )

    migration.downgrade()

    assert operation.drop_index.call_args_list == [
        call(
            "ix_resume_chunks_embedding_hnsw",
            table_name="resume_chunks",
            postgresql_using="hnsw"
        ),
        call(
            "ix_resume_chunks_candidate_id",
            table_name="resume_chunks"
        )
    ]
    operation.drop_table.assert_called_once_with(
        "resume_chunks"
    )
    operation.execute.assert_not_called()
