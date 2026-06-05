from __future__ import annotations

from pathlib import Path
from typing import Any

from backend.services.config import get_artifact_root


def get_health() -> dict[str, Any]:
    """Return shallow health status.

    返回浅层健康状态。
    """
    return {
        "status": "ok",
        "service": "quant-mas-backend",
        "live_trading_enabled": False,
        "research_only": True,
    }


def get_deep_health() -> dict[str, Any]:
    """Return deep but fallback-safe health status.

    返回深入但 fallback-safe 的健康状态。
    """
    artifact_root = get_artifact_root()
    return {
        **get_health(),
        "components": [
            {"name": "backend", "status": "ok", "detail": "FastAPI research API is running."},
            {
                "name": "artifact_root",
                "status": "exists" if Path(artifact_root).exists() else "missing",
                "detail": f"Artifact root: {artifact_root}",
                "path": str(artifact_root),
            },
            {"name": "database_optional", "status": "optional", "detail": "Postgres is optional."},
            {"name": "rag_optional", "status": "optional", "detail": "RAG vector store is optional."},
        ],
    }
