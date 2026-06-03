"""Context building package."""

from quant_mas.context.compression import (
    compress_metrics,
    compress_rag_chunks,
    truncate_text,
)
from quant_mas.context.context_builder import ContextBuilder
from quant_mas.context.context_schema import (
    AgentContextBundle,
    ExperimentContextSnapshot,
    MarketContextSnapshot,
    RagContextChunk,
    RiskContextSnapshot,
)

__all__ = [
    "AgentContextBundle",
    "ContextBuilder",
    "ExperimentContextSnapshot",
    "MarketContextSnapshot",
    "RagContextChunk",
    "RiskContextSnapshot",
    "compress_metrics",
    "compress_rag_chunks",
    "truncate_text",
]
