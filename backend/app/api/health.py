from fastapi import APIRouter

router = APIRouter(
    prefix="/health",
    tags=["Health Check"]
)


@router.get("/")
def health_check():
    return {
        "status": "healthy",
        "message": "AI Document Intelligence API Running"
    }