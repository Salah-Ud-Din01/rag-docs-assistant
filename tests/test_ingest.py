from pathlib import Path

import pytest
from langchain_core.documents import Document

from app import ingest
from app.ingest import load_documents, load_markdown, split_documents

SAMPLE_MARKDOWN = """# Guide

## Installation

Run the installer and follow the steps.

## Usage

Start the program from the terminal.
"""


def test_load_markdown_splits_by_heading(tmp_path: Path):
    file = tmp_path / "guide.md"
    file.write_text(SAMPLE_MARKDOWN, encoding="utf-8")

    docs = load_markdown(file)

    assert [d.metadata["section"] for d in docs] == ["Installation", "Usage"]
    assert all(d.metadata["source"] == "guide.md" for d in docs)
    assert "installer" in docs[0].page_content


def test_load_documents_ignores_unsupported_files(tmp_path: Path):
    (tmp_path / "guide.md").write_text(SAMPLE_MARKDOWN, encoding="utf-8")
    (tmp_path / "notes.txt").write_text("Should be ignored", encoding="utf-8")

    docs = load_documents(tmp_path)

    assert {d.metadata["source"] for d in docs} == {"guide.md"}


def test_load_documents_raises_for_missing_folder(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        load_documents(tmp_path / "does-not-exist")


def test_load_pdf_uses_page_numbers_and_skips_empty_pages(monkeypatch):
    class FakePage:
        def __init__(self, text):
            self._text = text

        def extract_text(self):
            return self._text

    class FakeReader:
        def __init__(self, path):
            self.pages = [FakePage("First page"), FakePage(""), FakePage("Third page")]

    monkeypatch.setattr(ingest, "PdfReader", FakeReader)

    docs = ingest.load_pdf(Path("manual.pdf"))

    assert [d.metadata["section"] for d in docs] == ["Page 1", "Page 3"]
    assert docs[0].metadata["source"] == "manual.pdf"


def test_split_documents_keeps_metadata_and_creates_unique_ids():
    long_text = "This is a sentence about Docker volumes. " * 40
    doc = Document(page_content=long_text, metadata={"source": "a.md", "section": "Volumes"})

    chunks = split_documents([doc], chunk_size=200, chunk_overlap=20)

    assert len(chunks) > 1
    assert all(len(c.page_content) <= 200 for c in chunks)
    assert all(c.metadata["section"] == "Volumes" for c in chunks)
    ids = [c.metadata["chunk_id"] for c in chunks]
    assert len(ids) == len(set(ids))
    assert ids[0] == "a.md:1"