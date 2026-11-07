"""Chat interface for RAG Docs Assistant. Talks to the FastAPI backend over HTTP."""

import os

import httpx
import streamlit as st

API_URL = os.getenv("API_URL", "http://localhost:8000")
TIMEOUT = 120  # seconds; a local LLM on CPU can be slow


def api_is_up() -> bool:
    try:
        return httpx.get(f"{API_URL}/health", timeout=5).status_code == 200
    except httpx.HTTPError:
        return False


def ingest() -> dict:
    response = httpx.post(f"{API_URL}/ingest", timeout=TIMEOUT)
    response.raise_for_status()
    return response.json()


def ask(question: str) -> dict:
    response = httpx.post(
        f"{API_URL}/ask", json={"question": question}, timeout=TIMEOUT
    )
    response.raise_for_status()
    return response.json()


def show_sources(sources: list[dict]) -> None:
    if not sources:
        return
    with st.expander(f"📄 Sources ({len(sources)})"):
        for source in sources:
            st.markdown(
                f"**{source['document']}** → {source['section']}  \n"
                f"Similarity: `{source['score']:.2f}`"
            )


st.set_page_config(page_title="RAG Docs Assistant", page_icon="📚")
st.title("📚 RAG Docs Assistant")
st.caption("Ask questions about your documents. Every answer shows its sources.")

with st.sidebar:
    st.header("Status")
    if api_is_up():
        st.success("API is running")
    else:
        st.error(f"API not reachable at {API_URL}")

    st.header("Documents")
    if st.button("Index documents"):
        with st.spinner("Reading and indexing documents..."):
            try:
                result = ingest()
                st.success(f"Indexed {result['documents']} documents ({result['chunks']} chunks)")
            except httpx.HTTPError as error:
                st.error(f"Indexing failed: {error}")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        show_sources(message.get("sources", []))

question = st.chat_input("Ask a question, e.g. What is RAG?")
if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Searching documents and writing an answer..."):
            try:
                result = ask(question)
                answer, sources = result["answer"], result["sources"]
            except httpx.HTTPError as error:
                answer, sources = f"Something went wrong: {error}", []
        st.markdown(answer)
        show_sources(sources)

    st.session_state.messages.append(
        {"role": "assistant", "content": answer, "sources": sources}
    )