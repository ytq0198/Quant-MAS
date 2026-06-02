"""Embedding client abstractions."""

from __future__ import annotations

import hashlib
import json
import os
import urllib.request
from abc import ABC, abstractmethod


class EmbeddingClient(ABC):
    """Abstract embedding client."""

    @abstractmethod
    def embed(self, texts: list[str]) -> list[list[float]]:
        """Embed texts into dense vectors."""


class HashEmbeddingClient(EmbeddingClient):
    """Deterministic hash embeddings for tests and local indexing."""

    def __init__(self, dimensions: int = 64) -> None:
        if dimensions <= 0:
            raise ValueError("dimensions must be positive")
        self.dimensions = dimensions

    def embed(self, texts: list[str]) -> list[list[float]]:
        return [self._embed_one(text) for text in texts]

    def _embed_one(self, text: str) -> list[float]:
        vector = [0.0] * self.dimensions
        for token in text.lower().split():
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            index = int.from_bytes(digest[:4], "big") % self.dimensions
            sign = 1.0 if digest[4] % 2 == 0 else -1.0
            vector[index] += sign
        return vector


class OpenAICompatibleEmbeddingClient(EmbeddingClient):
    """Skeleton OpenAI-compatible embedding client.

    Tests must not call this client. It exists so future deployments can set
    EMBEDDING_BASE_URL, EMBEDDING_API_KEY, and EMBEDDING_MODEL.
    """

    def __init__(
        self,
        *,
        base_url: str | None = None,
        api_key: str | None = None,
        model: str | None = None,
        timeout_seconds: float = 60.0,
    ) -> None:
        self.base_url = (base_url or os.environ.get("EMBEDDING_BASE_URL", "")).rstrip("/")
        self.api_key = api_key or os.environ.get("EMBEDDING_API_KEY", "")
        self.model = model or os.environ.get("EMBEDDING_MODEL", "")
        self.timeout_seconds = timeout_seconds
        if not self.base_url or not self.api_key or not self.model:
            raise ValueError(
                "OpenAICompatibleEmbeddingClient requires EMBEDDING_BASE_URL, "
                "EMBEDDING_API_KEY, and EMBEDDING_MODEL."
            )

    def embed(self, texts: list[str]) -> list[list[float]]:
        payload = json.dumps({"model": self.model, "input": texts}).encode("utf-8")
        request = urllib.request.Request(
            f"{self.base_url}/embeddings",
            data=payload,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
            data = json.loads(response.read().decode("utf-8"))
        return [item["embedding"] for item in data["data"]]
