from fastapi import FastAPI

from app.config import settings
from app.schemas import HealthResponse

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Answer questions about your documents, with source citations.",
)


@app.get("/health", response_model=HealthResponse, tags=["system"])
def health() -> HealthResponse:
    """Return service status. Used by Docker and monitoring to check liveness."""
    return HealthResponse(status="ok", version=settings.app_version)