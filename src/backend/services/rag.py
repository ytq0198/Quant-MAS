from __future__ import annotations

from typing import Any


def list_rag_documents() -> dict[str, Any]:
    """Return fallback RAG document list.

    返回回退 RAG 文档列表。
    """
    return {
        "source": "fallback_documents",
        "vector_store": "fallback",
        "documents": [
            {
                "document_id": "doc-research-protocol",
                "type": "research_protocol",
                "title": "Metric family separation",
                "snippet": "Do not mix oos.* with simulation.*, training.*, population.*, or audit.* metrics.",
            },
            {
                "document_id": "doc-oos-baseline",
                "type": "research_baseline",
                "title": "EXP-20260602-008",
                "snippet": "Walk-forward OOS baseline with Sharpe 0.586 and 19 windows.",
            },
        ],
    }


def query_rag(query: str) -> dict[str, Any]:
    """Return fallback RAG query results.

    返回回退 RAG 查询结果。
    """
    documents = list_rag_documents()["documents"]
    return {
        "source": "fallback_rag",
        "query": query,
        "results": documents,
        "safety_notes": [
            "oos.* metrics must not be mixed with simulation.*, training.*, population.*, or audit.* metrics.",
            "RAG results are research context, not financial advice.",
        ],
    }
