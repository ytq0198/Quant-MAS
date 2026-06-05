from __future__ import annotations

from typing import Any

from fastapi import APIRouter

from backend.services.experiments import get_experiment_detail, list_experiments

router = APIRouter(prefix="/api/experiments", tags=["experiments"])


@router.get("")
def read_experiments() -> dict[str, Any]:
    """List artifact-backed experiments.

    列出产物驱动的实验记录。
    """
    return list_experiments()


@router.get("/{experiment_id}")
def read_experiment(experiment_id: str) -> dict[str, Any]:
    """Return one artifact-backed experiment.

    返回单个产物驱动的实验记录。
    """
    return get_experiment_detail(experiment_id)
