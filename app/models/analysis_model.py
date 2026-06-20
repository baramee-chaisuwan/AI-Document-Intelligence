from pydantic import BaseModel
from typing import List

class CandidateAnalysis(BaseModel):

    candidate_level: str

    skill_score: int

    recommended_roles: List[str]

    strengths: List[str]

    improvement_areas: List[str]