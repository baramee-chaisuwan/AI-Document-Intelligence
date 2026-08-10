import importlib.util
from pathlib import Path
from unittest.mock import Mock

from sqlalchemy import DateTime, ForeignKey, Integer, String

from app.database.models import PasswordResetToken, User


MIGRATION_PATH = (
    Path(__file__).parents[1]
    / "alembic"
    / "versions"
    / "b9d6f2a7c410_add_password_reset_tokens.py"
)


def load_migration():
    spec = importlib.util.spec_from_file_location(
        "password_reset_migration",
        MIGRATION_PATH
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_password_reset_model_contract():
    columns = PasswordResetToken.__table__.columns
    assert isinstance(columns.id.type, Integer)
    assert isinstance(columns.user_id.type, Integer)
    assert isinstance(columns.otp_hash.type, String)
    assert columns.otp_hash.type.length == 255
    assert isinstance(columns.expires_at.type, DateTime)
    assert columns.expires_at.type.timezone is True
    assert columns.created_at.type.timezone is True
    assert columns.consumed_at.type.timezone is True
    assert columns.failed_attempts.nullable is False
    foreign_key = next(iter(columns.user_id.foreign_keys))
    assert isinstance(foreign_key, ForeignKey)
    assert foreign_key.target_fullname == "users.id"
    assert "token_version" in User.__table__.columns


def test_password_reset_migration_revision_and_operations(
    monkeypatch
):
    migration = load_migration()
    operation = Mock()
    monkeypatch.setattr(migration, "op", operation)

    assert migration.revision == "b9d6f2a7c410"
    assert migration.down_revision == "f7c2a9e4b610"

    migration.upgrade()
    operation.add_column.assert_called_once()
    operation.create_table.assert_called_once()
    assert operation.create_index.call_count == 3

    operation.reset_mock()
    migration.downgrade()
    assert operation.drop_index.call_count == 3
    operation.drop_table.assert_called_once_with(
        "password_reset_tokens"
    )
    operation.drop_column.assert_called_once_with(
        "users",
        "token_version"
    )
