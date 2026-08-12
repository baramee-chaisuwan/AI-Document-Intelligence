from pydantic import (
    BaseModel,
    Field,
    field_validator
)

from app.models.candidate_stage import CandidateStage

class CandidateUpdate(BaseModel):

    candidate_level: str | None = Field(
        default=None,
        min_length=1,
        max_length=50
    )
    skill_score: int | None = Field(
        default=None,
        ge=0,
        le=100
    )

    @field_validator("candidate_level")
    @classmethod
    def normalize_candidate_level(
        cls,
        value: str | None
    ) -> str | None:

        if value is None:
            return None

        normalized = value.strip()

        if not normalized:
            raise ValueError(
                "Candidate level cannot be blank"
            )

        return normalized


class CandidateStageUpdate(BaseModel):

    candidate_stage: CandidateStage
