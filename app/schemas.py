from pydantic import BaseModel


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