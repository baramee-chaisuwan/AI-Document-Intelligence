from pydantic import BaseModel

class CandidateUpdate(BaseModel):
    candidate_level: str
    skill_score: int