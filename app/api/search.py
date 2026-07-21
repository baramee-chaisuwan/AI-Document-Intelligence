from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.search_model import (SearchRequest, SearchResponse)
from app.services.search_service import semantic_search

router = APIRouter(
    prefix="/search",
    tags=["Semantic Search"]
)


@router.post("/",response_model=SearchResponse)
def search(
    request: SearchRequest,
    db: Session = Depends(get_db)
):

    return {
        "results": semantic_search(
            request.query,
            db
        )
    }