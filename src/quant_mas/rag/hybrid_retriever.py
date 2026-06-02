"""Hybrid keyword and vector retriever."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from quant_mas.rag.document_loader import Document
from quant_mas.rag.embedding_client import EmbeddingClient, HashEmbeddingClient
from quant_mas.rag.simple_retriever import RetrievalResult, SimpleRetriever
from quant_mas.rag.vector_store_base import VectorStore


@dataclass(frozen=True)
class HybridRetrievalResult:
    """One hybrid retrieval result."""

    document: Document
    score: float
    sources: list[str]
    metadata: dict[str, Any]


class HybridRetriever:
    """Combine SimpleRetriever and optional vector search."""

    def __init__(
        self,
        *,
        keyword_retriever: SimpleRetriever | None = None,
        vector_store: VectorStore | None = None,
        embedding_client: EmbeddingClient | None = None,
    ) -> None:
        self.keyword_retriever = keyword_retriever or SimpleRetriever()
        self.vector_store = vector_store
        self.embedding_client = embedding_client or HashEmbeddingClient()

    def search(self, query: str, *, top_k: int = 5) -> list[HybridRetrievalResult]:
        merged: dict[str, HybridRetrievalResult] = {}
        for result in self.keyword_retriever.search(query, top_k=top_k):
            key = str(result.document.path)
            merged[key] = HybridRetrievalResult(
                document=result.document,
                score=result.score,
                sources=["keyword"],
                metadata={"matched_terms": result.matched_terms},
            )
        if self.vector_store is not None:
            query_embedding = self.embedding_client.embed([query])[0]
            for result in self.vector_store.search(query_embedding, top_k=top_k):
                document = _document_from_metadata(result.metadata)
                key = str(document.path)
                previous = merged.get(key)
                if previous is None:
                    merged[key] = HybridRetrievalResult(
                        document=document,
                        score=result.score,
                        sources=["vector"],
                        metadata=result.metadata,
                    )
                else:
                    merged[key] = HybridRetrievalResult(
                        document=previous.document,
                        score=previous.score + result.score,
                        sources=sorted(set([*previous.sources, "vector"])),
                        metadata={**previous.metadata, **result.metadata},
                    )
        results = list(merged.values())
        results.sort(key=lambda result: (-result.score, str(result.document.path)))
        return results[:top_k]


def _document_from_metadata(metadata: dict[str, Any]) -> Document:
    path = Path(metadata.get("path", metadata.get("source", "")))
    return Document(
        doc_id=str(metadata.get("doc_id", path)),
        path=path,
        title=str(metadata.get("title", path.stem)),
        content=str(metadata.get("content", "")),
        metadata=metadata,
    )
