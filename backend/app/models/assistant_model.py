from pydantic import BaseModel, Field, field_validator


class AssistantRequest(BaseModel):

    question: str = Field(
        min_length=1,
        max_length=2000
    )

    @field_validator("question")
    @classmethod
    def normalize_question(cls, value: str) -> str:

        normalized = value.strip()

        if not normalized:
            raise ValueError(
                "Question cannot be blank"
            )

        return normalized


class AssistantResponse(BaseModel):
    answer: str
