from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator
)


MAX_FEEDBACK_NOTE_LENGTH = 1000


class RAGEvaluationFeedbackRequest(BaseModel):

    retrieval_rating: int = Field(ge=1, le=5)
    answer_rating: int = Field(ge=1, le=5)
    feedback_note: str | None = Field(
        default=None,
        max_length=MAX_FEEDBACK_NOTE_LENGTH
    )

    @field_validator(
        "feedback_note",
        mode="before"
    )
    @classmethod
    def normalize_feedback_note(
        cls,
        value
    ) -> str | None:

        if value is None:
            return None

        if not isinstance(value, str):
            return value

        normalized = value.strip()

        return normalized or None


class RAGEvaluationFeedbackResponse(BaseModel):

    model_config = ConfigDict(
        from_attributes=True
    )

    id: int
    operation: str
    retrieval_rating: int | None
    answer_rating: int | None
    feedback_note: str | None
    evaluated_at: datetime | None
