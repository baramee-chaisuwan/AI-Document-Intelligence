from fastapi import APIRouter

router = APIRouter(
    prefix="/upload",
    tags=["Document Upload"]
)


@router.post("/")
def upload_document():
    return {
        "message": "Upload endpoint ready"
    }