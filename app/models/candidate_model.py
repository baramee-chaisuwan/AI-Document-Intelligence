from datetime import datetime
from pydantic import BaseModel


class CandidateResponse(BaseModel):

    id: int
    name: str
    summary: str
    candidate_level: str
    skill_score: int
    created_at: datetime
    rule_score: int
    ai_score: int
    ai_status: str
    score_breakdown: dict

    class Config:
        from_attributes = True

class RankingResponse(BaseModel):
    id: int
    name: str
    skill_score: int