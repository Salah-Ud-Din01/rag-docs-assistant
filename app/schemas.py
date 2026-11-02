from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    version: str


class IngestResponse(BaseModel):
    documents: int
    chunks: int