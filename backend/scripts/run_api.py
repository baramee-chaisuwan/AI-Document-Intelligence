import os
import sys


DEFAULT_PORT = 8080


def get_port() -> int:

    raw_port = os.getenv(
        "PORT",
        str(DEFAULT_PORT)
    )

    try:

        port = int(raw_port)

    except (TypeError, ValueError) as error:

        raise RuntimeError(
            "PORT must be an integer"
        ) from error

    if port < 1 or port > 65535:

        raise RuntimeError(
            "PORT must be between 1 and 65535"
        )

    return port


def main() -> None:

    command = [
        sys.executable,
        "-m",
        "uvicorn",
        "main:app",
        "--host",
        "0.0.0.0",
        "--port",
        str(get_port())
    ]

    os.execv(
        sys.executable,
        command
    )


if __name__ == "__main__":

    main()
