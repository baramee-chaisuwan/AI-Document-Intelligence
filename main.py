from fastapi import FastAPI
from app.core.config import APP_NAME, APP_VERSION
from app.api.health import router as health_router
from app.api.upload import router as upload_router
from app.database.database import engine, Base
import app.database.models
from app.api.candidate import router as candidate_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION
)

app.include_router(health_router)
app.include_router(upload_router)
app.include_router(candidate_router)