from typing import List, Literal

from pydantic import (
    BaseModel,
    Field
)


class ScoreBreakdown(BaseModel):

    score_version: Literal["profile_v2"] | None = None

    python: int = Field(
        default=0,
        ge=0
    )

    sql: int = Field(
        default=0,
        ge=0
    )

    backend: int = Field(
        default=0,
        ge=0
    )

    devops: int = Field(
        default=0,
        ge=0
    )

    ai_domain: int = Field(
        default=0,
        ge=0
    )

    data_domain: int = Field(
        default=0,
        ge=0
    )

    backend_domain: int = Field(
        default=0,
        ge=0
    )

    experience: int = Field(
        default=0,
        ge=0
    )

    projects: int = Field(
        default=0,
        ge=0
    )

    engineering_signal: int = Field(
        default=0,
        ge=0
    )

    professional_experience: int = Field(
        default=0,
        ge=0,
        le=25
    )

    achievements: int = Field(
        default=0,
        ge=0,
        le=20
    )

    competencies: int = Field(
        default=0,
        ge=0,
        le=20
    )

    certifications: int = Field(
        default=0,
        ge=0,
        le=10
    )

    education: int = Field(
        default=0,
        ge=0,
        le=10
    )

    leadership: int = Field(
        default=0,
        ge=0,
        le=10
    )

    evidence_quality: int = Field(
        default=0,
        ge=0,
        le=5
    )


class CandidateAnalysis(BaseModel):

    candidate_level: Literal[
        "Entry-Level",
        "Junior",
        "Mid-Level",
        "Senior"
    ]

    rule_score: int = Field(
        ge=0,
        le=100
    )

    ai_score: int = Field(
        ge=0,
        le=100
    )

    skill_score: int = Field(
        ge=0,
        le=100
    )

    score_breakdown: ScoreBreakdown

    project_count: int = Field(
        default=0,
        ge=0
    )

    ai_status: Literal[
        "success",
        "fallback"
    ]

    recommended_roles: List[str] = Field(
        default_factory=list
    )

    strengths: List[str] = Field(
        default_factory=list
    )

    improvement_areas: List[str] = Field(
        default_factory=list
    )
