import json
import logging
import os
import time
from contextlib import contextmanager
from datetime import datetime, timezone
from functools import wraps

from fastapi import FastAPI, Request


logger = logging.getLogger("ats.observability")
logger.setLevel(logging.INFO)
logger.propagate = False

if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter("%(message)s")
    )
    logger.addHandler(handler)


def duration_ms(started_at: float) -> float:

    return round(
        max(0.0, time.perf_counter() - started_at) * 1000,
        2
    )


def emit_event(
    event: str,
    *,
    service: str | None = None,
    severity: str = "INFO",
    **fields
) -> None:

    payload = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "severity": severity,
        "event": event,
        "service": service or service_name(),
    }
    payload.update({
        key: value
        for key, value in fields.items()
        if value is not None
    })

    log_method = (
        logger.error
        if severity == "ERROR"
        else logger.info
    )
    log_method(
        json.dumps(
            payload,
            separators=(",", ":"),
            default=str
        )
    )


@contextmanager
def observe_operation(
    operation: str,
    **safe_fields
):

    started_at = time.perf_counter()

    try:
        yield
    except Exception as error:
        emit_event(
            "operation_failed",
            severity="ERROR",
            operation=operation,
            outcome="failure",
            duration_ms=duration_ms(started_at),
            error_category=type(error).__name__,
            **safe_fields
        )
        raise
    else:
        emit_event(
            "operation_completed",
            operation=operation,
            outcome="success",
            duration_ms=duration_ms(started_at),
            **safe_fields
        )


def observed_operation(operation: str):

    def decorator(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            with observe_operation(operation):
                return function(*args, **kwargs)

        return wrapper

    return decorator


def install_request_logging(
    app: FastAPI,
    *,
    default_service: str
) -> None:

    @app.middleware("http")
    async def log_request(
        request: Request,
        call_next
    ):
        started_at = time.perf_counter()

        try:
            response = await call_next(request)
        except Exception as error:
            emit_event(
                "http_request",
                service=service_name(default_service),
                severity="ERROR",
                method=request.method,
                route=_safe_route(request),
                status_code=500,
                duration_ms=duration_ms(started_at),
                error_category=type(error).__name__
            )
            raise

        emit_event(
            "http_request",
            service=service_name(default_service),
            method=request.method,
            route=_safe_route(request),
            status_code=response.status_code,
            duration_ms=duration_ms(started_at)
        )

        return response


def service_name(default: str = "ats-backend") -> str:

    return (
        os.getenv("K_SERVICE", "").strip()
        or default
    )


def _safe_route(request: Request) -> str:

    route = request.scope.get("route")
    route_path = getattr(route, "path", None)

    if isinstance(route_path, str) and route_path:
        return route_path

    return "unmatched"
