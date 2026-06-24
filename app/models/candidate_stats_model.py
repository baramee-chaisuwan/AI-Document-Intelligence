from pydantic import BaseModel

class CandidateStatsResponse(BaseModel):
    total_candidates: int
    average_skill_score: float
    entry_level_count: int
    junior_count: int