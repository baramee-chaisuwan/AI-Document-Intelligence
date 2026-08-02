from pydantic import BaseModel


class AssistantRequest(BaseModel):
    question: str


class AssistantResponse(BaseModel):
    answer: str