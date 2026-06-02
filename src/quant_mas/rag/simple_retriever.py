"""Deterministic keyword retriever."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from quant_mas.rag.document_loader import Document, load_documents


@dataclass(frozen=True)
class RetrievalResult:
    """One keyword retrieval result."""

    document: Document
    score: float
    matched_terms: list[str]


class SimpleRetriever:
    """Small keyword retriever without vectors or external services."""

    def __init__(self, documents: list[Document] | None = None) -> None:
        self.documents: list[Document] = list(documents or [])

    def add_documents(self, documents: list[Document]) -> None:
        self.documents.extend(documents)

    def search(self, query: str, *, top_k: int = 5) -> list[RetrievalResult]:
        if top_k <= 0:
            return []
        terms = _terms(query)
        if not terms:
            return []
        results = []
        for document in self.documents:
            content = document.content.lower()
            matched = [term for term in terms if term in content]
            score = sum(content.count(term) for term in terms)
            if score > 0:
                results.append(
                    RetrievalResult(
                        document=document,
                        score=float(score),
                        matched_terms=matched,
                    )
                )
        results.sort(key=lambda result: (-result.score, str(result.document.path)))
        return results[:top_k]

    @classmethod
    def from_directories(
        cls,
        directories: list[str | Path] | None = None,
        **loader_kwargs,
    ) -> "SimpleRetriever":
        roots = directories or [Path("docs"), Path("outputs") / "reports"]
        documents: list[Document] = []
        for directory in roots:
            path = Path(directory).expanduser()
            if path.exists():
                documents.extend(load_documents(path, **loader_kwargs))
        return cls(documents)


def _terms(query: str) -> list[str]:
    seen: set[str] = set()
    terms: list[str] = []
    for raw in query.lower().split():
        term = raw.strip()
        if term and term not in seen:
            terms.append(term)
            seen.add(term)
    return terms
