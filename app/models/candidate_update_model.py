from pydantic import BaseModel

class CandidateUpdate(BaseModel):
    candidate_level: str | None = None
    skill_score: int | None = None