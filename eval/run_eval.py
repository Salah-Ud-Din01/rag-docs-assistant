"""Measure RAG quality on a small set of questions with known answers.

Two metrics:
- Retrieval hit rate: was the expected document retrieved in the top-k chunks?
- Answer accuracy:    did the generated answer contain the expected keywords?

Usage: python -m eval.run_eval
"""

import json
from pathlib import Path

from app.config import settings
from app.ingest import load_documents, split_documents
from app.rag import answer_question, get_llm
from app.vectorstore import get_vectorstore, index_chunks, search

EVAL_FILE = Path("eval/eval_set.json")


def load_eval_set() -> list[dict]:
    return json.loads(EVAL_FILE.read_text(encoding="utf-8"))


def retrieval_hit(store, case: dict, k: int) -> bool:
    """True if the expected document appears in the top-k retrieved chunks."""
    results = search(store, case["question"], k=k)
    documents = {doc.metadata["source"] for doc, _score in results}
    return case["expected_document"] in documents


def answer_hit(answer: str, case: dict) -> bool:
    """True if every expected keyword appears in the answer (case-insensitive)."""
    text = answer.lower()
    return all(keyword.lower() in text for keyword in case["expected_keywords"])


def main() -> None:
    cases = load_eval_set()
    store = get_vectorstore()
    llm = get_llm()

    # Rebuild the index so the evaluation is reproducible.
    chunks = split_documents(
        load_documents(settings.docs_dir), settings.chunk_size, settings.chunk_overlap
    )
    index_chunks(store, chunks)

    retrieval_hits = 0
    answer_hits = 0

    print(f"Evaluating {len(cases)} questions (top_k={settings.top_k})\n")
    print(f"{'Q':<48} {'Retrieved':<10} {'Answer':<8}")
    print("-" * 68)

    for case in cases:
        r_hit = retrieval_hit(store, case, settings.top_k)
        response = answer_question(case["question"], store, llm, k=settings.top_k)
        a_hit = answer_hit(response.answer, case)

        retrieval_hits += r_hit
        answer_hits += a_hit
        question = case["question"][:46]
        print(f"{question:<48} {'OK' if r_hit else 'MISS':<10} {'OK' if a_hit else 'MISS':<8}")

    n = len(cases)
    print("-" * 68)
    print(f"\nRetrieval hit rate: {retrieval_hits}/{n} = {retrieval_hits / n:.0%}")
    print(f"Answer accuracy:    {answer_hits}/{n} = {answer_hits / n:.0%}")


if __name__ == "__main__":
    main()