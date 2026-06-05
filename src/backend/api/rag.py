from __future__ import annotations

from typing import Any

from fastapi import APIRouter

from backend.services.rag import list_rag_documents, query_rag

router = APIRouter(prefix="/api/rag", tags=["rag"])


@router.get("/documents")
def read_rag_documents() -> dict[str, Any]:
    """Return RAG documents.

    返回 RAG 文档。
    """
    return list_rag_documents()


@router.get("/query")
def read_rag_query(q: str = "") -> dict[str, Any]:
    """Return RAG query results.

    返回 RAG 查询结果。
    """
    return query_rag(q)
