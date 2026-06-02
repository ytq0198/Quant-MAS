"""In-memory vector store."""

from __future__ import annotations

from typing import Any

import numpy as np

from quant_mas.rag.vector_store_base import VectorSearchResult, VectorStore


class InMemoryVectorStore(VectorStore):
    """Simple cosine-similarity vector store."""

    def __init__(self) -> None:
        self._vectors: dict[str, np.ndarray] = {}
        self._metadata: dict[str, dict[str, Any]] = {}

    def upsert(
        self,
        ids: list[str],
        embeddings: list[list[float]],
        metadata: list[dict[str, Any]],
    ) -> None:
        if not (len(ids) == len(embeddings) == len(metadata)):
            raise ValueError("ids, embeddings, and metadata must have equal length")
        for id_, embedding, item_metadata in zip(ids, embeddings, metadata, strict=True):
            self._vectors[id_] = np.asarray(embedding, dtype=float)
            self._metadata[id_] = dict(item_metadata)

    def search(
        self,
        query_embedding: list[float],
        *,
        top_k: int = 5,
    ) -> list[VectorSearchResult]:
        if top_k <= 0 or not self._vectors:
            return []
        query = np.asarray(query_embedding, dtype=float)
        query_norm = np.linalg.norm(query)
        if query_norm == 0:
            return []
        results = []
        for id_, vector in self._vectors.items():
            denom = query_norm * np.linalg.norm(vector)
            score = 0.0 if denom == 0 else float(np.dot(query, vector) / denom)
            results.append(
                VectorSearchResult(
                    id=id_,
                    score=score,
                    metadata=self._metadata.get(id_, {}),
                )
            )
        results.sort(key=lambda result: (-result.score, result.id))
        return results[:top_k]

    def delete(self, ids: list[str]) -> None:
        for id_ in ids:
            self._vectors.pop(id_, None)
            self._metadata.pop(id_, None)

    def to_records(self) -> list[dict[str, Any]]:
        return [
            {
                "id": id_,
                "embedding": vector.tolist(),
                "metadata": self._metadata.get(id_, {}),
            }
            for id_, vector in sorted(self._vectors.items())
        ]
