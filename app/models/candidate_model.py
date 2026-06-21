from datetime import datetime
from pydantic import BaseModel


class CandidateResponse(BaseModel):

    id: int
    name: str
    summary: str
    candidate_level: str
    skill_score: int
    created_at: datetime

    class Config:
        from_attributes = True