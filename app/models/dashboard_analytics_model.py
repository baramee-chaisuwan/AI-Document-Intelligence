from pydantic import BaseModel


class ScoreDistributionResponse(BaseModel):
    score_range: str
    count: int


class LevelDistributionResponse(BaseModel):
    level: str
    count: int