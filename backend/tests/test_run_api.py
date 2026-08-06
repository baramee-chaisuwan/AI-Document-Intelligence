import sys
from unittest.mock import Mock

import pytest

from scripts import run_api


def test_run_api_uses_cloud_run_default_port(
    monkeypatch
):

    monkeypatch.delenv(
        "PORT",
        raising=False
    )
    exec_process = Mock()
    monkeypatch.setattr(
        run_api.os,
        "execv",
        exec_process
    )

    run_api.main()

    exec_process.assert_called_once_with(
        sys.executable,
        [
            sys.executable,
            "-m",
            "uvicorn",
            "main:app",
            "--host",
            "0.0.0.0",
            "--port",
            "8080"
        ]
    )


def test_run_api_uses_cloud_run_port(
    monkeypatch
):

    monkeypatch.setenv(
        "PORT",
        "9090"
    )
    exec_process = Mock()
    monkeypatch.setattr(
        run_api.os,
        "execv",
        exec_process
    )

    run_api.main()

    command = exec_process.call_args.args[1]
    assert command[-1] == "9090"


@pytest.mark.parametrize(
    "port",
    [
        "not-a-number",
        "0",
        "65536"
    ]
)
def test_run_api_rejects_invalid_port(
    monkeypatch,
    port
):

    monkeypatch.setenv(
        "PORT",
        port
    )

    with pytest.raises(RuntimeError):

        run_api.get_port()
