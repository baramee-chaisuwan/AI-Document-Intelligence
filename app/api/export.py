import csv
import io

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database.models import Candidate

router = APIRouter(
    prefix="/export",
    tags=["Export"]
)