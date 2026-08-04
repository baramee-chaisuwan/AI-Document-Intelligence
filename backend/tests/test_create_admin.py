from unittest.mock import Mock

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.security import (
    hash_password,
    verify_password,
)
from app.database.database import Base
from app.database.models import User
from scripts import create_admin


ADMIN_PASSWORD = "StrongAdminPassword123!"


def _session_factory():

    engine = create_engine(
        "sqlite://",
        connect_args={
            "check_same_thread": False
        },
        poolclass=StaticPool
    )

    Base.metadata.create_all(bind=engine)

    return sessionmaker(
        autocommit=False,
        autoflush=False,
        expire_on_commit=False,
        bind=engine
    )


def _mock_prompts(
    monkeypatch,
    *,
    email="Admin@Example.com",
    full_name="  First Administrator  ",
    password=ADMIN_PASSWORD,
    confirmation=ADMIN_PASSWORD
):

    responses = iter([email, full_name])
    passwords = iter([password, confirmation])

    monkeypatch.setattr(
        "builtins.input",
        lambda _prompt: next(responses)
    )

    monkeypatch.setattr(
        create_admin,
        "getpass",
        lambda _prompt: next(passwords)
    )


def test_create_admin_success(
    monkeypatch,
    capsys
):

    testing_session = _session_factory()

    _mock_prompts(monkeypatch)

    monkeypatch.setattr(
        create_admin,
        "SessionLocal",
        testing_session
    )

    assert create_admin.main() == 0

    output = capsys.readouterr()

    assert output.out.strip() == (
        "Administrator created: "
        "email=admin@example.com role=admin"
    )
    assert output.err == ""
    assert ADMIN_PASSWORD not in output.out
    assert ADMIN_PASSWORD not in output.err

    with testing_session() as db:

        user = db.query(User).one()

        assert user.email == "admin@example.com"
        assert user.full_name == "First Administrator"
        assert user.role == "admin"
        assert user.is_active is True
        assert user.hashed_password != ADMIN_PASSWORD
        assert verify_password(
            ADMIN_PASSWORD,
            user.hashed_password
        )


def test_create_admin_rejects_duplicate_email(
    monkeypatch,
    capsys
):

    testing_session = _session_factory()

    with testing_session() as db:

        db.add(
            User(
                email="admin@example.com",
                full_name="Existing Admin",
                hashed_password=hash_password(
                    ADMIN_PASSWORD
                ),
                role="admin",
                is_active=True
            )
        )

        db.commit()

    _mock_prompts(
        monkeypatch,
        email="ADMIN@example.com"
    )

    monkeypatch.setattr(
        create_admin,
        "SessionLocal",
        testing_session
    )

    assert create_admin.main() == 1

    output = capsys.readouterr()

    assert output.out == ""
    assert "already exists" in output.err
    assert ADMIN_PASSWORD not in output.err

    with testing_session() as db:
        assert db.query(User).count() == 1


def test_create_admin_rejects_password_mismatch(
    monkeypatch,
    capsys
):

    _mock_prompts(
        monkeypatch,
        confirmation="DifferentPassword123!"
    )

    session_factory = Mock()

    monkeypatch.setattr(
        create_admin,
        "SessionLocal",
        session_factory
    )

    assert create_admin.main() == 1
    session_factory.assert_not_called()

    output = capsys.readouterr()

    assert output.out == ""
    assert "Passwords do not match" in output.err
    assert ADMIN_PASSWORD not in output.err


def test_create_admin_sanitizes_validation_error(
    monkeypatch,
    capsys
):

    invalid_password = "secret"

    _mock_prompts(
        monkeypatch,
        password=invalid_password,
        confirmation=invalid_password
    )

    session_factory = Mock()

    monkeypatch.setattr(
        create_admin,
        "SessionLocal",
        session_factory
    )

    assert create_admin.main() == 1
    session_factory.assert_not_called()

    output = capsys.readouterr()

    assert output.out == ""
    assert "Invalid password" in output.err
    assert invalid_password not in output.err


def test_create_admin_rolls_back_unexpected_failure(
    monkeypatch,
    capsys
):

    _mock_prompts(monkeypatch)

    db = Mock()

    monkeypatch.setattr(
        create_admin,
        "SessionLocal",
        lambda: db
    )

    monkeypatch.setattr(
        create_admin,
        "create_admin_user",
        Mock(side_effect=RuntimeError("database failed"))
    )

    assert create_admin.main() == 1

    db.rollback.assert_called_once_with()
    db.close.assert_called_once_with()

    output = capsys.readouterr()

    assert output.out == ""
    assert output.err.strip() == (
        "Error: Administrator could not be created."
    )
    assert ADMIN_PASSWORD not in output.err
