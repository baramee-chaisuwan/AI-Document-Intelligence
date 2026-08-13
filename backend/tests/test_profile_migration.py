import importlib.util
from pathlib import Path

from sqlalchemy import String

from app.database.models import User


MIGRATION_PATH = (
    Path(__file__).parents[1]
    / "alembic"
    / "versions"
    / "e4a7c1d9b250_add_user_profile_image.py"
)


def test_profile_image_model_and_migration_contract():
    column = User.__table__.columns.profile_image_key
    assert isinstance(column.type, String)
    assert column.type.length == 1024
    assert column.nullable is True

    spec = importlib.util.spec_from_file_location(
        "profile_migration",
        MIGRATION_PATH
    )
    migration = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(migration)
    assert migration.revision == "e4a7c1d9b250"
    assert migration.down_revision == "d2f6a9b3c840"
