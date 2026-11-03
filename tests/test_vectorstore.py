from langchain_core.documents import Document

from app.vectorstore import index_chunks, search


def make_chunk(text: str, chunk_id: str) -> Document:
    return Document(
        page_content=text,
        metadata={"source": "a.md", "section": "Test", "chunk_id": chunk_id},
    )


def test_index_chunks_replaces_previous_content(store):
    chunks = [make_chunk("first text", "a.md:1"), make_chunk("second text", "a.md:2")]

    index_chunks(store, chunks)
    count = index_chunks(store, chunks)

    assert count == 2
    assert len(search(store, "text", k=10)) == 2


def test_index_chunks_with_no_chunks_empties_the_store(store):
    index_chunks(store, [make_chunk("some text", "a.md:1")])

    count = index_chunks(store, [])

    assert count == 0
    assert search(store, "text", k=5) == []


def test_search_returns_documents_with_scores(store):
    index_chunks(store, [make_chunk("volumes keep data", "a.md:1")])

    results = search(store, "volumes keep data", k=1)

    doc, score = results[0]
    assert doc.metadata["source"] == "a.md"
    assert isinstance(score, float)