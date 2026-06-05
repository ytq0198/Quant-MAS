from __future__ import annotations

from typing import Any

from fastapi import APIRouter

from backend.services.tools import list_tools

router = APIRouter(prefix="/api/tools", tags=["tools"])


@router.get("")
def read_tools() -> list[dict[str, Any]]:
    """Return controlled quant tools.

    返回受控量化工具。
    """
    return list_tools()
