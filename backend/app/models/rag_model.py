from typing import List

from pydantic import (
    BaseModel,
    Field
)

class RagRequest(BaseModel):

    question: str = Field(
        min_length=1,
        max_length=2000
    )

class RagResponse(BaseModel):

    answer: str

class RecommendationResponse(BaseModel):

    candidate_id: str

    candidate_name: str

    match_score: int = Field(
        ge=0,
        le=100
    )

    strengths: List[str] = Field(
        default_factory=list
    )

    relevant_experience: List[str] = Field(
        default_factory=list
    )

    reason: str