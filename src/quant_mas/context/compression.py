"""Compression helpers for bounded research context."""

from __future__ import annotations

from typing import Any

from quant_mas.context.context_schema import RagContextChunk


DEFAULT_METRIC_KEYS = [
    "oos.sharpe",
    "oos.total_return",
    "oos.max_drawdown",
    "total_return",
    "sharpe",
    "max_drawdown",
    "test_auc",
]


def compress_metrics(
    metrics: dict[str, Any],
    *,
    keep_keys: list[str] | None = None,
) -> dict[str, Any]:
    """Keep only selected metric paths while preserving nested structure."""
    keys = keep_keys or DEFAULT_METRIC_KEYS
    compressed: dict[str, Any] = {}
    for key in keys:
        value = _resolve_metric(metrics, key)
        if value is not None:
            _set_metric(compressed, key, value)
    return compressed


def truncate_text(text: str, max_chars: int) -> str:
    """Truncate text to a bounded character count."""
    if max_chars <= 0:
        return ""
    if len(text) <= max_chars:
        return text
    suffix = "...[truncated]"
    if max_chars <= len(suffix):
        return suffix[:max_chars]
    return text[: max_chars - len(suffix)].rstrip() + suffix


def compress_rag_chunks(
    chunks: list[RagContextChunk],
    *,
    max_chunks: int,
    max_chars: int,
) -> list[RagContextChunk]:
    """Limit RAG chunk count and snippet size."""
    if max_chunks <= 0:
        return []
    return [
        RagContextChunk(
            doc_id=chunk.doc_id,
            path=chunk.path,
            title=chunk.title,
            snippet=truncate_text(chunk.snippet, max_chars),
            score=chunk.score,
        )
        for chunk in chunks[:max_chunks]
    ]


def _resolve_metric(metrics: dict[str, Any], key: str) -> Any:
    if key in metrics:
        return metrics[key]
    current: Any = metrics
    for part in key.split("."):
        if not isinstance(current, dict) or part not in current:
            return None
        current = current[part]
    return current


def _set_metric(target: dict[str, Any], key: str, value: Any) -> None:
    parts = key.split(".")
    current = target
    for part in parts[:-1]:
        current = current.setdefault(part, {})
    current[parts[-1]] = value
