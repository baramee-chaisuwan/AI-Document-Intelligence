from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, RedirectResponse
from dotenv import load_dotenv

from app.database.database import engine, Base
import app.database.models

from app.api.health import router as health_router
from app.api.upload import router as upload_router
from app.api.candidate import router as candidate_router
from app.api.export import router as export_router
from app.api.dashboard import router as dashboard_router
from app.api.search import router as search_router
from app.api.langchain import (router as langchain_router)
from app.api.rag import router as rag_router
from app.core.exceptions import NotFoundError

load_dotenv()

try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    print("DB not ready yet:", e)

app = FastAPI(
    title="AI Resume Intelligence API",
    description="""
AI-powered Resume Screening System

Features:
- Resume Parsing
- Candidate Ranking
- AI Resume Analysis
- Duplicate Detection
- Dashboard Analytics
- CSV Export
""",
    version="1.0.0"
)

@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")

app.include_router(health_router)
app.include_router(upload_router)
app.include_router(candidate_router)
app.include_router(search_router)
app.include_router(langchain_router)
app.include_router(rag_router)
app.include_router(dashboard_router)
app.include_router(export_router)

@app.exception_handler(NotFoundError)
def not_found_handler(request: Request, exc: NotFoundError):
    return JSONResponse(
        status_code=404,
        content={"detail": exc.message},
    )