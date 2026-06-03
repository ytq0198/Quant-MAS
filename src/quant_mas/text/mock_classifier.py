"""Deterministic mock text classifier."""

from __future__ import annotations

import hashlib


class MockSentimentClassifier:
    """Hash-based deterministic classifier returning scores in [-1, 1]."""

    model_id = "mock_sentiment_v1"

    def predict(self, texts: list[str]) -> list[float]:
        scores = []
        for text in texts:
            digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
            value = int(digest[:8], 16) / 0xFFFFFFFF
            scores.append(round(value * 2 - 1, 6))
        return scores
