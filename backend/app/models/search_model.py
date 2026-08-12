from pydantic import BaseModel, Field, field_validator


class SearchRequest(BaseModel):

    query: str = Field(
        min_length=1,
        max_length=2000
    )

    @field_validator("query")
    @classmethod
    def normalize_query(cls, value: str) -> str:

        normalized = value.strip()

        if not normalized:
            raise ValueError(
                "Search query cannot be blank"
            )

        return normalized

class SearchResult(BaseModel):
    id: int
    name: str
    summary: str
    candidate_level: str
    skill_score: int
    rule_score: int
    ai_score: int
    distance: float


class SearchResponse(BaseModel):
    results: list[SearchResult]
