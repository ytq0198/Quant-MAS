from __future__ import annotations

from typing import Any


def get_deployment_status() -> dict[str, Any]:
    """Return v4 deployment skeleton metadata.

    返回 v4 部署骨架元数据。
    """
    return {
        "phase": "v4-phase-4",
        "frontend": {
            "stack": "React + Vite",
            "dev_url": "http://127.0.0.1:5173",
            "build_dir": "frontend/dist",
        },
        "backend": {
            "stack": "FastAPI + Uvicorn",
            "dev_url": "http://127.0.0.1:8000",
            "entrypoint": "backend.app:app",
        },
        "artifacts": [
            "docker-compose.yml",
            "Dockerfile.backend",
            "Dockerfile.frontend",
            "docs/database_setup.md",
            "docs/fullstack_quickstart.md",
        ],
        "safety": {
            "live_trading_enabled": False,
            "notes": [
                "Deployment skeleton exposes research APIs only.",
                "No broker, order, shell, or secrets path is exposed through Phase 4 status APIs.",
            ],
        },
    }
