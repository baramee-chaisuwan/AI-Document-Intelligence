from pydantic import BaseModel

class DashboardSummaryResponse(BaseModel):
    total_candidates: int
    average_score: float
    top_candidate: str
    top_score: int
    junior_count: int
    mid_count: int
    senior_count: int

    model_config = {
        "json_schema_extra": {
            "example": {
                "total_candidates": 15,
                "average_score": 78.5,
                "top_candidate": "John Doe",
                "top_score": 92,
                "junior_count": 8,
                "mid_count": 5,
                "senior_count": 2
            }
        }
    }

class TopCandidateResponse(BaseModel):
    id: int
    name: str
    skill_score: int