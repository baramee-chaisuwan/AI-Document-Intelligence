from fastapi import FastAPI
from app.core.config import APP_NAME, APP_VERSION
from app.api.health import router as health_router
from app.api.upload import router as upload_router
from app.database.database import engine, Base
import app.database.models
from app.api.candidate import router as candidate_router
from app.api.export import router as export_router
from dotenv import load_dotenv

load_dotenv()

Base.metadata.create_all(bind=engine)

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

app.include_router(health_router)
app.include_router(upload_router)
app.include_router(candidate_router)
app.include_router(export_router)