from fastapi import FastAPI

from app.api.health import router as health_router
from app.api.pubsub_receiver import (
    router as pubsub_receiver_router
)
from app.core.config import APP_NAME, APP_VERSION
from app.services.observability_service import (
    install_request_logging
)


app = FastAPI(
    title=f"{APP_NAME} Worker",
    description=(
        "Internal resume-processing worker. Deployment must require "
        "Cloud Run IAM authenticated invocation."
    ),
    version=APP_VERSION
)

install_request_logging(
    app,
    default_service="ats-worker"
)

app.include_router(health_router)
app.include_router(pubsub_receiver_router)
