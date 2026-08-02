from pydantic import BaseModel


class LevelDistribution(BaseModel):
    entry_level: int
    junior: int
    mid_level: int
    senior: int


class CandidateStatsResponse(BaseModel):
    total_candidates: int
    average_skill_score: float
    level_distribution: LevelDistribution