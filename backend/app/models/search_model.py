from pydantic import BaseModel


class SearchRequest(BaseModel):
    query: str

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