from __future__ import annotations

from typing import Any

from fastapi import APIRouter

from backend.services.graph import get_graph_relationships

router = APIRouter(prefix="/api/graph", tags=["graph"])


@router.get("/relationships")
def read_graph_relationships() -> dict[str, Any]:
    """Return graph relationships.

    返回图谱关系。
    """
    return get_graph_relationships()
