from __future__ import annotations

from typing import Any

from fastapi import APIRouter

from backend.services.config_status import get_effective_config
from backend.services.health import get_deep_health, get_health
from backend.services.logs import get_recent_logs
from backend.services.metrics import get_metrics_summary

router = APIRouter(prefix="/api", tags=["observability"])


@router.get("/health")
def read_health() -> dict[str, Any]:
    """Return health status.

    返回健康状态。
    """
    return get_health()


@router.get("/health/deep")
def read_deep_health() -> dict[str, Any]:
    """Return deep health status.

    返回深入健康状态。
    """
    return get_deep_health()


@router.get("/metrics/summary")
def read_metrics_summary() -> dict[str, Any]:
    """Return lightweight metrics summary.

    返回轻量指标摘要。
    """
    return get_metrics_summary()


@router.get("/logs/recent")
def read_recent_logs(limit: int = 50) -> dict[str, Any]:
    """Return recent logs.

    返回最近日志。
    """
    return get_recent_logs(limit=max(1, min(limit, 500)))


@router.get("/config/effective")
def read_effective_config() -> dict[str, Any]:
    """Return redacted effective config.

    返回脱敏有效配置。
    """
    return get_effective_config()
