from pydantic import BaseModel

class CandidateStatsResponse(BaseModel):

    total_candidates: int

    average_ai_score: float