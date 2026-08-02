from pydantic import BaseModel
from typing import List


class RagRequest(BaseModel):
    question: str


class RagResponse(BaseModel):
    answer: str


class RecommendationResponse(BaseModel):
    candidate_id: str
    candidate_name: str
    match_score: int
    strengths: List[str]
    relevant_experience: List[str]
    reason: str