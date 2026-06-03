"""FinBERT sentiment baseline boundary."""

from __future__ import annotations

from typing import Protocol

from quant_mas.text.data_schema import FinancialTextRecord, TextSignalRecord
from quant_mas.text.mock_classifier import MockSentimentClassifier


class SentimentClassifier(Protocol):
    """Protocol for text sentiment models."""

    model_id: str

    def predict(self, texts: list[str]) -> list[float]:
        """Return one numeric sentiment score per text."""


class FinBERTSentimentClassifier:
    """Thin wrapper for a real FinBERT model, intended for server use."""

    def __init__(self, model_name: str = "ProsusAI/finbert", *, max_length: int = 128) -> None:
        try:
            from transformers import pipeline
        except ImportError as exc:
            raise ImportError(
                'FinBERT requires optional text dependencies: python -m pip install -e ".[text]"'
            ) from exc
        self.model_id = model_name
        self.max_length = max_length
        self._pipeline = pipeline("sentiment-analysis", model=model_name, tokenizer=model_name)

    def predict(self, texts: list[str]) -> list[float]:
        results = self._pipeline(
            texts,
            truncation=True,
            max_length=self.max_length,
        )
        return [_score_from_label(result) for result in results]


def predict_sentiment(
    records: list[FinancialTextRecord],
    classifier: SentimentClassifier | None = None,
    *,
    signal_name: str = "finbert_sentiment",
) -> list[TextSignalRecord]:
    """Convert text records into structured sentiment signal records."""
    model = classifier or MockSentimentClassifier()
    scores = model.predict([record.text for record in records])
    if len(scores) != len(records):
        raise ValueError("classifier returned a different number of scores than input texts")
    return [
        TextSignalRecord(
            date=record.date,
            symbol=record.symbol,
            signal_name=signal_name,
            value=float(score),
            model_id=model.model_id,
        )
        for record, score in zip(records, scores, strict=True)
    ]


def _score_from_label(result: dict) -> float:
    label = str(result.get("label", "")).lower()
    score = float(result.get("score", 0.0))
    if "positive" in label:
        return score
    if "negative" in label:
        return -score
    return 0.0
