from __future__ import annotations

from typing import Any

from fastapi import APIRouter

from backend.services.memory import search_memory

router = APIRouter(prefix="/api/memory", tags=["memory"])


@router.get("/search")
def read_memory_search(q: str = "") -> dict[str, Any]:
    """Search local research memory.

    检索本地研究记忆。
    """
    return search_memory(q)
