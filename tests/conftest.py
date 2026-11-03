"""Shared test fixtures. Fakes replace Ollama so tests run fast, offline and free."""

import pytest
from fastapi.testclient import TestClient
from langchain_core.embeddings import DeterministicFakeEmbedding
from langchain_core.language_models.fake_chat_models import FakeListChatModel

from app.config import settings
from app.main import app, get_store
from app.rag import get_llm
from app.vectorstore import get_vectorstore

SAMPLE_DOC = """# Docker

## Volumes

A volume stores data outside the container, so the data survives when the container is removed.

## Images

An image is a read-only template used to start containers.
"""

FAKE_ANSWER = "Use a volume to keep data."


@pytest.fixture
def docs_dir(tmp_path, monkeypatch):
    """A temporary documents folder with one small Markdown file."""
    folder = tmp_path / "docs"
    folder.mkdir()
    (folder / "docker.md").write_text(SAMPLE_DOC, encoding="utf-8")
    monkeypatch.setattr(settings, "docs_dir", str(folder))
    return folder


@pytest.fixture
def store(tmp_path, monkeypatch):
    """A real Chroma store in a temporary folder, using fake embeddings."""
    monkeypatch.setattr(settings, "chroma_dir", str(tmp_path / "chroma"))
    return get_vectorstore(DeterministicFakeEmbedding(size=32))


@pytest.fixture
def fake_llm():
    """A fake chat model that always returns the same answer instantly."""
    return FakeListChatModel(responses=[FAKE_ANSWER])


@pytest.fixture
def api_client(store, fake_llm, docs_dir):
    """API test client where the real store and LLM are replaced by fakes."""
    app.dependency_overrides[get_store] = lambda: store
    app.dependency_overrides[get_llm] = lambda: fake_llm
    yield TestClient(app)
    app.dependency_overrides.clear()