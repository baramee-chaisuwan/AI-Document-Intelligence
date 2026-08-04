"""Interactively create an administrator account."""

from getpass import getpass
from pathlib import Path
import sys

from pydantic import ValidationError


BACKEND_ROOT = Path(__file__).resolve().parents[1]

if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))


from app.core.exceptions import ConflictError  # noqa: E402
from app.database.database import SessionLocal  # noqa: E402
from app.models.auth_model import (  # noqa: E402
    UserRegisterRequest,
    UserRole,
)
from app.services.auth_service import (  # noqa: E402
    create_admin_user,
)


def _validation_message(
    error: ValidationError
) -> str:

    first_error = error.errors(
        include_input=False
    )[0]

    field = str(
        first_error.get("loc", ("input",))[0]
    ).replace("_", " ")

    message = first_error.get(
        "msg",
        "Invalid value"
    )

    return f"Invalid {field}: {message}"


def main() -> int:

    db = None

    try:

        email = input("Email: ")
        full_name = input("Full name: ")
        password = getpass("Password: ")
        password_confirmation = getpass(
            "Confirm password: "
        )

        if password != password_confirmation:
            print(
                "Error: Passwords do not match.",
                file=sys.stderr
            )
            return 1

        data = UserRegisterRequest(
            email=email,
            full_name=full_name,
            password=password
        )

        db = SessionLocal()

        user = create_admin_user(
            db,
            data
        )

        print(
            f"Administrator created: "
            f"email={user.email} "
            f"role={UserRole.ADMIN.value}"
        )

        return 0

    except ValidationError as error:

        print(
            f"Error: {_validation_message(error)}",
            file=sys.stderr
        )

    except ConflictError as error:

        if db is not None:
            db.rollback()

        print(
            f"Error: {error}",
            file=sys.stderr
        )

    except (EOFError, KeyboardInterrupt):

        if db is not None:
            db.rollback()

        print(
            "Error: Administrator creation cancelled.",
            file=sys.stderr
        )

    except Exception:

        if db is not None:
            db.rollback()

        print(
            "Error: Administrator could not be created.",
            file=sys.stderr
        )

    finally:

        if db is not None:
            db.close()

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
