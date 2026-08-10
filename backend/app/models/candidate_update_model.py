from pydantic import BaseModel

from app.models.candidate_stage import CandidateStage

class CandidateUpdate(BaseModel):
    candidate_level: str | None = None
    skill_score: int | None = None


class CandidateStageUpdate(BaseModel):

    candidate_stage: CandidateStage
