"""pgvector-backed VectorStore for enterprise RAG deployments."""

from __future__ import annotations

import json
import os
from typing import Any, Protocol

from quant_mas.rag.vector_store_base import VectorSearchResult, VectorStore


class PgConnection(Protocol):
    def execute(self, query: str, params: tuple[Any, ...] | None = None) -> Any: ...
    def fetchall(self) -> list[Any]: ...
    def commit(self) -> None: ...
    def close(self) -> None: ...


class PgVectorStore(VectorStore):
    """PostgreSQL pgvector VectorStore implementation."""

    def __init__(
        self,
        dsn: str | None = None,
        *,
        connection: PgConnection | None = None,
        table_name: str = "rag_vectors",
        dimensions: int = 64,
        initialize: bool = True,
    ) -> None:
        self.dsn = dsn or os.getenv("POSTGRES_DSN")
        self._provided_connection = connection
        self.table_name = table_name
        self.dimensions = dimensions
        if self._provided_connection is None and not self.dsn:
            raise ValueError("pgvector backend requires POSTGRES_DSN or dsn")
        if initialize:
            self._initialize()

    def upsert(
        self,
        ids: list[str],
        embeddings: list[list[float]],
        metadata: list[dict[str, Any]],
    ) -> None:
        if not (len(ids) == len(embeddings) == len(metadata)):
            raise ValueError("ids, embeddings, and metadata must have equal length")
        connection = self._connect()
        try:
            for id_, embedding, item_metadata in zip(ids, embeddings, metadata, strict=True):
                self._validate_embedding(embedding)
                connection.execute(
                    f"""
                    INSERT INTO {self.table_name} (id, embedding, metadata)
                    VALUES (%s, %s, %s::jsonb)
                    ON CONFLICT (id) DO UPDATE
                    SET embedding = EXCLUDED.embedding,
                        metadata = EXCLUDED.metadata
                    """,
                    (
                        id_,
                        _embedding_literal(embedding),
                        json.dumps(item_metadata, ensure_ascii=False),
                    ),
                )
            connection.commit()
        finally:
            self._close_if_owned(connection)

    def search(
        self,
        query_embedding: list[float],
        *,
        top_k: int = 5,
    ) -> list[VectorSearchResult]:
        if top_k <= 0:
            return []
        self._validate_embedding(query_embedding)
        connection = self._connect()
        try:
            connection.execute(
                f"""
                SELECT id, metadata, 1 - (embedding <=> %s) AS score
                FROM {self.table_name}
                ORDER BY embedding <=> %s
                LIMIT %s
                """,
                (
                    _embedding_literal(query_embedding),
                    _embedding_literal(query_embedding),
                    top_k,
                ),
            )
            rows = connection.fetchall()
        finally:
            self._close_if_owned(connection)
        return [_row_to_result(row) for row in rows]

    def delete(self, ids: list[str]) -> None:
        connection = self._connect()
        try:
            for id_ in ids:
                connection.execute(f"DELETE FROM {self.table_name} WHERE id = %s", (id_,))
            connection.commit()
        finally:
            self._close_if_owned(connection)

    def _initialize(self) -> None:
        connection = self._connect()
        try:
            connection.execute("CREATE EXTENSION IF NOT EXISTS vector")
            connection.execute(
                f"""
                CREATE TABLE IF NOT EXISTS {self.table_name} (
                    id TEXT PRIMARY KEY,
                    embedding VECTOR({self.dimensions}) NOT NULL,
                    metadata JSONB NOT NULL
                )
                """
            )
            connection.commit()
        finally:
            self._close_if_owned(connection)

    def _validate_embedding(self, embedding: list[float]) -> None:
        if len(embedding) != self.dimensions:
            raise ValueError(
                f"embedding dimension mismatch: expected {self.dimensions}, got {len(embedding)}"
            )

    def _connect(self) -> PgConnection:
        if self._provided_connection is not None:
            return self._provided_connection
        try:
            import psycopg
        except ImportError as exc:
            raise ImportError("pgvector backend requires psycopg.") from exc
        return psycopg.connect(self.dsn)

    def _close_if_owned(self, connection: PgConnection) -> None:
        if self._provided_connection is None:
            connection.close()


def _embedding_literal(embedding: list[float]) -> str:
    return "[" + ",".join(str(float(value)) for value in embedding) + "]"


def _row_to_result(row: Any) -> VectorSearchResult:
    if isinstance(row, dict):
        id_ = row["id"]
        metadata = row["metadata"]
        score = row["score"]
    elif hasattr(row, "keys"):
        id_ = row["id"]
        metadata = row["metadata"]
        score = row["score"]
    else:
        id_, metadata, score = row
    if isinstance(metadata, str):
        metadata = json.loads(metadata)
    return VectorSearchResult(id=str(id_), score=float(score), metadata=dict(metadata))
