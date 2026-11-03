from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str
    version: str


class IngestResponse(BaseModel):
    documents: int
    chunks: int
    

class Source(BaseModel):
    document: str
    section: str
    score: float


class AskResponse(BaseModel):
    answer: str
    sources: list[Source]


class AskRequest(BaseModel):
    question: str = Field(min_length=3, examples=["What is RAG?"])