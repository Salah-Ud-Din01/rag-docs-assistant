from langchain_core.documents import Document
from langchain_core.language_models.fake_chat_models import FakeListChatModel

from app.config import settings
from app.ingest import load_documents, split_documents
from app.rag import NO_ANSWER, answer_question, format_context
from app.vectorstore import index_chunks
from tests.conftest import FAKE_ANSWER


def index_sample_docs(store):
    docs = load_documents(settings.docs_dir)
    index_chunks(store, split_documents(docs, chunk_size=800, chunk_overlap=100))


def test_answer_includes_sources(store, docs_dir, fake_llm):
    index_sample_docs(store)

    response = answer_question("How do I keep data?", store, fake_llm, k=2)

    assert response.answer == FAKE_ANSWER
    assert len(response.sources) == 2
    assert all(source.document == "docker.md" for source in response.sources)


def test_empty_store_returns_no_answer(store, fake_llm):
    response = answer_question("How do I keep data?", store, fake_llm, k=2)

    assert response.answer == NO_ANSWER
    assert response.sources == []


def test_no_sources_when_model_cannot_answer(store, docs_dir):
    index_sample_docs(store)
    refusing_llm = FakeListChatModel(responses=[NO_ANSWER])

    response = answer_question("What is the capital of Japan?", store, refusing_llm, k=2)

    assert response.answer == NO_ANSWER
    assert response.sources == []


def test_format_context_shows_source_and_section():
    doc = Document(page_content="Some text", metadata={"source": "a.md", "section": "Intro"})

    context = format_context([(doc, 0.9)])

    assert "Source: a.md - Intro" in context
    assert "Some text" in context