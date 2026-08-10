from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator
)


class JobRequirements(BaseModel):

    required_skills: list[str] = Field(
        default_factory=list
    )
    preferred_skills: list[str] = Field(
        default_factory=list
    )
    experience_requirements: list[str] = Field(
        default_factory=list
    )
    responsibilities: list[str] = Field(
        default_factory=list
    )


class JobCreateRequest(BaseModel):

    title: str = Field(
        min_length=1,
        max_length=255
    )
    description: str = Field(
        min_length=1
    )

    @field_validator(
        "title",
        "description"
    )
    @classmethod
    def reject_blank_values(
        cls,
        value: str
    ):

        normalized = value.strip()

        if not normalized:
            raise ValueError(
                "Value cannot be blank"
            )

        return normalized


class JobResponse(BaseModel):

    model_config = ConfigDict(
        from_attributes=True
    )

    id: int
    title: str
    description: str
    extracted_requirements: JobRequirements
    created_by: int
    created_at: datetime
