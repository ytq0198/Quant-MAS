from __future__ import annotations

from fastapi import FastAPI

from backend.api.agents import router as agents_router
from backend.api.memory import router as memory_router
from backend.api.status import router as status_router
from backend.api.tools import router as tools_router


def create_app() -> FastAPI:
    """Create the Quant MAS v4 API app.

    创建 Quant MAS v4 API 应用。
    """
    api = FastAPI(
        title="Quant MAS v4 API",
        description=(
            "Full-stack API for the Quant MAS research platform. "
            "Research and education only; no direct live trading."
        ),
        version="0.4.0",
    )
    api.include_router(status_router)
    api.include_router(agents_router)
    api.include_router(tools_router)
    api.include_router(memory_router)
    return api


app = create_app()
