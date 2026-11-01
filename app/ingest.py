"""Load documents from disk and split them into chunks with source metadata."""

from pathlib import Path

from langchain_core.documents import Document
from langchain_text_splitters import (
    MarkdownHeaderTextSplitter,
    RecursiveCharacterTextSplitter,
)
from pypdf import PdfReader

from app.config import settings

HEADERS_TO_SPLIT_ON = [("#", "h1"), ("##", "h2"), ("###", "h3")]


def load_markdown(path: Path) -> list[Document]:
    """Split a Markdown file by headings. Each section keeps its heading as metadata."""
    text = path.read_text(encoding="utf-8")
    splitter = MarkdownHeaderTextSplitter(headers_to_split_on=HEADERS_TO_SPLIT_ON)
    sections = splitter.split_text(text)

    documents = []
    for section in sections:
        heading = (
            section.metadata.get("h3")
            or section.metadata.get("h2")
            or section.metadata.get("h1")
            or "Introduction"
        )
        documents.append(
            Document(
                page_content=section.page_content,
                metadata={"source": path.name, "section": heading},
            )
        )
    return documents


def load_pdf(path: Path) -> list[Document]:
    """Read a PDF page by page. The page number is used as the section."""
    reader = PdfReader(path)
    documents = []
    for page_number, page in enumerate(reader.pages, start=1):
        text = (page.extract_text() or "").strip()
        if text:
            documents.append(
                Document(
                    page_content=text,
                    metadata={"source": path.name, "section": f"Page {page_number}"},
                )
            )
    return documents


def load_documents(docs_dir: str | Path) -> list[Document]:
    """Load all supported files (.md, .pdf) in a folder and its subfolders."""
    docs_dir = Path(docs_dir)
    if not docs_dir.is_dir():
        raise FileNotFoundError(f"Documents folder not found: {docs_dir}")

    documents = []
    for path in sorted(docs_dir.rglob("*")):
        suffix = path.suffix.lower()
        if suffix == ".md":
            documents.extend(load_markdown(path))
        elif suffix == ".pdf":
            documents.extend(load_pdf(path))
    return documents


def split_documents(
    documents: list[Document], chunk_size: int, chunk_overlap: int
) -> list[Document]:
    """Split long sections into smaller chunks and give each chunk a unique ID."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap
    )
    chunks = splitter.split_documents(documents)

    counters: dict[str, int] = {}
    for chunk in chunks:
        source = chunk.metadata["source"]
        counters[source] = counters.get(source, 0) + 1
        chunk.metadata["chunk_id"] = f"{source}:{counters[source]}"
    return chunks


if __name__ == "__main__":
    docs = load_documents(settings.docs_dir)
    chunks = split_documents(docs, settings.chunk_size, settings.chunk_overlap)
    print(f"Loaded {len(docs)} sections -> {len(chunks)} chunks\n")
    for chunk in chunks:
        meta = chunk.metadata
        preview = chunk.page_content[:60].replace("\n", " ")
        print(f"[{meta['chunk_id']}] {meta['section']}: {preview}...")