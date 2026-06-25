from pydantic import BaseModel
from typing import List, Dict


class ScoreBreakdown(BaseModel):
    python: int
    sql: int
    machine_learning: int
    etl: int
    experience: int

class CandidateAnalysis(BaseModel):

    candidate_level: str

    rule_score: int

    ai_score: int

    skill_score: int

    score_breakdown: Dict[str, int]

    ai_status: str

    recommended_roles: List[str]

    strengths: List[str]

    improvement_areas: List[str]