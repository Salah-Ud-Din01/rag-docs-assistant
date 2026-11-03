from fastapi.testclient import TestClient

from app.config import settings
from app.main import app

client = TestClient(app)


def test_health_returns_ok():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "version": settings.app_version}
    

def test_ingest_returns_counts(api_client):
    response = api_client.post("/ingest")

    assert response.status_code == 200
    assert response.json() == {"documents": 1, "chunks": 2}


def test_ingest_returns_404_when_docs_folder_is_missing(api_client, monkeypatch, tmp_path):
    monkeypatch.setattr(settings, "docs_dir", str(tmp_path / "missing"))

    response = api_client.post("/ingest")

    assert response.status_code == 404


def test_ask_returns_answer_and_sources(api_client):
    api_client.post("/ingest")

    response = api_client.post("/ask", json={"question": "How do I keep data?"})

    body = response.json()
    assert response.status_code == 200
    assert body["answer"] == "Use a volume to keep data."
    assert body["sources"][0]["document"] == "docker.md"


def test_ask_rejects_too_short_question(api_client):
    response = api_client.post("/ask", json={"question": "hi"})

    assert response.status_code == 422