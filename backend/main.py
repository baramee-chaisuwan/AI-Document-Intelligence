import logging
import os
from contextlib import asynccontextmanager

from fastapi import (
    FastAPI,
    Request
)
from fastapi.middleware.cors import (
    CORSMiddleware
)
from fastapi.responses import (
    JSONResponse,
    RedirectResponse
)

from app.core.config import (
    APP_NAME,
    APP_VERSION
)
from app.core.exceptions import (
    NotFoundError
)
from app.database.database import (
    Base,
    engine
)

import app.database.models

from app.api.health import (
    router as health_router
)
from app.api.upload import (
    router as upload_router
)
from app.api.candidate import (
    router as candidate_router
)
from app.api.export import (
    router as export_router
)
from app.api.dashboard import (
    router as dashboard_router
)
from app.api.search import (
    router as search_router
)
from app.api.assistant import (
    router as assistant_router
)
from app.api.recommend import (
    router as recommend_router
)


logging.basicConfig(
    level=logging.INFO,
    format=(
        "%(asctime)s "
        "%(levelname)s "
        "%(name)s "
        "%(message)s"
    )
)

logger = logging.getLogger(
    __name__
)


ENVIRONMENT = os.getenv(
    "ENVIRONMENT",
    "development"
).lower()


CORS_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS",
        (
            "http://localhost:3000,"
            "http://localhost:3001"
        )
    ).split(",")
    if origin.strip()
]


@asynccontextmanager
async def lifespan(
    app: FastAPI
):

    logger.info(
        "Starting %s version %s",
        APP_NAME,
        APP_VERSION
    )

    if ENVIRONMENT == "development":

        try:

            Base.metadata.create_all(
                bind=engine
            )

            logger.info(
                "Development database tables verified"
            )

        except Exception:

            logger.exception(
                "Development database initialization failed"
            )

            raise

    yield

    logger.info(
        "Stopping %s",
        APP_NAME
    )


app = FastAPI(
    title=APP_NAME,
    description="""
AI-powered Resume Screening System

Features:
- Resume Parsing
- Candidate Ranking
- AI Resume Analysis
- Duplicate Detection
- Semantic and Hybrid Search
- AI HR Assistant
- Candidate Recommendation
- Dashboard Analytics
- CSV Export
""",
    version=APP_VERSION,
    lifespan=lifespan
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=[
        "GET",
        "POST",
        "PUT",
        "DELETE",
        "OPTIONS"
    ],
    allow_headers=[
        "Authorization",
        "Content-Type"
    ]
)


@app.get(
    "/",
    include_in_schema=False
)
def root():

    return RedirectResponse(
        url="/docs"
    )


app.include_router(
    health_router
)

app.include_router(
    upload_router
)

app.include_router(
    candidate_router
)

app.include_router(
    search_router
)

app.include_router(
    assistant_router
)

app.include_router(
    recommend_router
)

app.include_router(
    dashboard_router
)

app.include_router(
    export_router
)


@app.exception_handler(
    NotFoundError
)
def not_found_handler(
    request: Request,
    exc: NotFoundError
):

    return JSONResponse(
        status_code=404,
        content={
            "detail": exc.message
        }
    )


@app.exception_handler(
    Exception
)
def unexpected_error_handler(
    request: Request,
    exc: Exception
):

    logger.exception(
        "Unexpected request failure: "
        "method=%s path=%s",
        request.method,
        request.url.path
    )

    return JSONResponse(
        status_code=500,
        content={
            "detail": (
                "An unexpected server error occurred"
            )
        }
    )