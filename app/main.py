from fastapi import Depends, FastAPI, HTTPException
from langchain_chroma import Chroma
from langchain_core.language_models import BaseChatModel

from app.config import settings
from app.ingest import load_documents, split_documents
from app.rag import answer_question, get_llm
from app.schemas import AskRequest, AskResponse, HealthResponse, IngestResponse
from app.vectorstore import get_vectorstore, index_chunks

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Answer questions about your documents, with source citations.",
)


def get_store() -> Chroma:
    """Dependency that provides the vector store. Tests replace it with a fake."""
    return get_vectorstore()


@app.get("/health", response_model=HealthResponse, tags=["system"])
def health() -> HealthResponse:
    """Return service status. Used by Docker and monitoring to check liveness."""
    return HealthResponse(status="ok", version=settings.app_version)


@app.post("/ingest", response_model=IngestResponse, tags=["documents"])
def ingest(store: Chroma = Depends(get_store)) -> IngestResponse:
    """Load all documents, split them into chunks and (re)build the vector index."""
    try:
        documents = load_documents(settings.docs_dir)
    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error

    chunks = split_documents(documents, settings.chunk_size, settings.chunk_overlap)
    count = index_chunks(store, chunks)
    sources = {doc.metadata["source"] for doc in documents}
    return IngestResponse(documents=len(sources), chunks=count)


@app.post("/ask", response_model=AskResponse, tags=["questions"])
def ask(
    request: AskRequest,
    store: Chroma = Depends(get_store),
    llm: BaseChatModel = Depends(get_llm),
) -> AskResponse:
    """Answer a question using the indexed documents, with sources."""
    return answer_question(request.question, store, llm, k=settings.top_k)