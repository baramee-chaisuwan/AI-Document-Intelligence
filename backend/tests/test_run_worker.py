from unittest.mock import Mock

import pytest

from scripts import run_worker


def test_worker_launcher_execs_uvicorn_directly(monkeypatch):

    monkeypatch.setenv("PORT", "9090")
    execv = Mock()
    monkeypatch.setattr(run_worker.os, "execv", execv)

    run_worker.main()

    execv.assert_called_once_with(
        run_worker.sys.executable,
        [
            run_worker.sys.executable,
            "-m",
            "uvicorn",
            "worker_main:app",
            "--host",
            "0.0.0.0",
            "--port",
            "9090"
        ]
    )


@pytest.mark.parametrize(
    "port",
    ["invalid", "0", "65536"]
)
def test_worker_launcher_rejects_invalid_port(
    monkeypatch,
    port
):

    monkeypatch.setenv("PORT", port)

    with pytest.raises(RuntimeError):
        run_worker.get_port()
