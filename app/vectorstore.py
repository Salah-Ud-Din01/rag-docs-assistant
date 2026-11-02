"""Turn chunks into embeddings and store/search them in Chroma."""

import sys

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_ollama import OllamaEmbeddings

from app.config import settings


def get_embeddings() -> Embeddings:
    """Embedding model served by Ollama."""
    return OllamaEmbeddings(
        model=settings.embedding_model, base_url=settings.ollama_base_url
    )


def get_vectorstore(embeddings: Embeddings | None = None) -> Chroma:
    """Open (or create) the Chroma collection stored on disk."""
    return Chroma(
        collection_name=settings.collection_name,
        embedding_function=embeddings or get_embeddings(),
        persist_directory=settings.chroma_dir,
        collection_metadata={"hnsw:space": "cosine"},
    )


def index_chunks(vectorstore: Chroma, chunks: list[Document]) -> int:
    """Replace everything in the collection with these chunks. Returns the count."""
    vectorstore.reset_collection()
    if not chunks:
        return 0
    ids = [chunk.metadata["chunk_id"] for chunk in chunks]
    vectorstore.add_documents(chunks, ids=ids)
    return len(chunks)


def search(
    vectorstore: Chroma, question: str, k: int
) -> list[tuple[Document, float]]:
    """Return the k most similar chunks with a similarity score (higher is better)."""
    results = vectorstore.similarity_search_with_score(question, k=k)
    return [(doc, 1 - distance) for doc, distance in results]


if __name__ == "__main__":
    from app.ingest import load_documents, split_documents

    question = sys.argv[1] if len(sys.argv) > 1 else "How do I keep data?"

    chunks = split_documents(
        load_documents(settings.docs_dir), settings.chunk_size, settings.chunk_overlap
    )
    store = get_vectorstore()
    count = index_chunks(store, chunks)
    print(f"Indexed {count} chunks\n")
    print(f"Question: {question}\n")

    results = search(store, question, k=settings.top_k)

    for doc, score in results:
        print(f"{score:.2f}  {doc.metadata['source']} -> {doc.metadata['section']}")