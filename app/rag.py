"""Answer questions: retrieve relevant chunks, then let the LLM write an answer."""

import sys

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama

from app.config import settings
from app.schemas import AskResponse, Source
from app.vectorstore import search

NO_ANSWER = "I couldn't find this in the provided documents."

PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You answer questions using ONLY the context below.\n"
            f'If the answer is not in the context, reply exactly: "{NO_ANSWER}"\n'
            "Keep the answer short and clear (2-4 sentences).",
        ),
        ("human", "Context:\n{context}\n\nQuestion: {question}"),
    ]
)


def get_llm() -> BaseChatModel:
    """Chat model served by Ollama. temperature=0 gives stable, factual answers."""
    return ChatOllama(
        model=settings.llm_model, base_url=settings.ollama_base_url, temperature=0
    )


def format_context(results: list[tuple[Document, float]]) -> str:
    """Join the retrieved chunks into one text block for the prompt."""
    parts = []
    for doc, _score in results:
        header = f"Source: {doc.metadata['source']} - {doc.metadata['section']}"
        parts.append(f"{header}\n{doc.page_content}")
    return "\n\n".join(parts)


def answer_question(
    question: str, store: Chroma, llm: BaseChatModel, k: int
) -> AskResponse:
    """The full RAG flow: retrieve -> build prompt -> generate -> attach sources."""
    results = search(store, question, k=k)
    if not results:
        return AskResponse(answer=NO_ANSWER, sources=[])

    messages = PROMPT.format_messages(
        context=format_context(results), question=question
    )
    answer = llm.invoke(messages).content.strip()

    if NO_ANSWER.lower() in answer.lower():
        return AskResponse(answer=NO_ANSWER, sources=[])

    sources = [
        Source(
            document=doc.metadata["source"],
            section=doc.metadata["section"],
            score=round(score, 2),
        )
        for doc, score in results
    ]
    return AskResponse(answer=answer, sources=sources)


if __name__ == "__main__":
    from app.vectorstore import get_vectorstore

    question = sys.argv[1] if len(sys.argv) > 1 else "What is RAG?"
    response = answer_question(question, get_vectorstore(), get_llm(), settings.top_k)

    print(f"Question: {question}\n")
    print(f"Answer: {response.answer}\n")
    print("Sources:")
    for source in response.sources:
        print(f"  {source.score:.2f}  {source.document} -> {source.section}")