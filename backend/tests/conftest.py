import os

import pytest


os.environ.setdefault("TESTING", "true")
os.environ.setdefault("PYTHON_DOTENV_DISABLED", "1")
os.environ.setdefault(
    "DATABASE_URL",
    "sqlite:///./.pytest-safe-default.db"
)
os.environ.setdefault("GEMINI_API_KEY", "test-only-not-real")
os.environ.setdefault(
    "JWT_SECRET_KEY",
    "test-only-jwt-secret-with-at-least-32-bytes"
)


from app.api.dependencies import (
    get_current_admin_user,
    get_current_staff_user,
    get_current_user
)
from app.database.models import User
from main import app


@pytest.fixture(autouse=True)
def authenticated_legacy_test_user(request):
    """Keep pre-RBAC tests focused on their original behavior."""

    if request.node.get_closest_marker(
        "real_auth"
    ):

        yield
        return

    admin = User(
        id=1,
        email="legacy-tests@example.com",
        full_name="Legacy Test Admin",
        role="admin",
        is_active=True
    )

    dependencies = (
        get_current_user,
        get_current_staff_user,
        get_current_admin_user
    )

    previous_overrides = {
        dependency: app.dependency_overrides.get(
            dependency
        )
        for dependency in dependencies
    }

    for dependency in dependencies:

        app.dependency_overrides[
            dependency
        ] = lambda: admin

    yield

    for dependency, previous in (
        previous_overrides.items()
    ):

        if previous is None:

            app.dependency_overrides.pop(
                dependency,
                None
            )

        else:

            app.dependency_overrides[
                dependency
            ] = previous
