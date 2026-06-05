from __future__ import annotations

from fastapi import FastAPI

from backend.api.agents import router as agents_router
from backend.api.artifacts import router as artifacts_router
from backend.api.audit import router as audit_router
from backend.api.auth import router as auth_router
from backend.api.backtests import router as backtests_router
from backend.api.database import router as database_router
from backend.api.deployment import router as deployment_router
from backend.api.experiments import router as experiments_router
from backend.api.graph import router as graph_router
from backend.api.jobs import router as jobs_router
from backend.api.memory import router as memory_router
from backend.api.oos import router as oos_router
from backend.api.observability import router as observability_router
from backend.api.rag import router as rag_router
from backend.api.risk import router as risk_router
from backend.api.review import router as review_router
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
    api.include_router(auth_router)
    api.include_router(agents_router)
    api.include_router(tools_router)
    api.include_router(memory_router)
    api.include_router(backtests_router)
    api.include_router(oos_router)
    api.include_router(risk_router)
    api.include_router(database_router)
    api.include_router(deployment_router)
    api.include_router(experiments_router)
    api.include_router(artifacts_router)
    api.include_router(audit_router)
    api.include_router(review_router)
    api.include_router(jobs_router)
    api.include_router(rag_router)
    api.include_router(graph_router)
    api.include_router(observability_router)
    return api


app = create_app()
