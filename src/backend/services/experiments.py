from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from backend.services.config import get_experiment_memory_path


def list_experiments(artifact_root: str | Path | None = None) -> dict[str, Any]:
    """List experiments from server/local artifacts with safe fallback.

    从服务器/本地产物列出实验，缺失时安全回退。
    """
    memory_path = get_experiment_memory_path(artifact_root)
    records = _read_experiment_records(memory_path)
    if records:
        return {
            "source": "server_artifact",
            "path": str(memory_path),
            "experiments": [_normalize_experiment(record) for record in records],
        }
    return {
        "source": "fallback_baseline",
        "path": str(memory_path),
        "experiments": [_fallback_baseline()],
    }


def get_experiment_detail(
    experiment_id: str,
    artifact_root: str | Path | None = None,
) -> dict[str, Any]:
    """Return one experiment detail with fallback baseline support.

    返回单个实验详情，支持基线回退。
    """
    payload = list_experiments(artifact_root)
    for experiment in payload["experiments"]:
        if experiment["experiment_id"] == experiment_id:
            return {
                "source": payload["source"],
                "path": payload["path"],
                "experiment": experiment,
            }
    if experiment_id == "EXP-20260602-008":
        return {
            "source": "fallback_baseline",
            "path": payload["path"],
            "experiment": _fallback_baseline(),
        }
    return {
        "source": payload["source"],
        "path": payload["path"],
        "experiment": None,
        "message": "Experiment not found.",
        "中文": "未找到实验。",
    }


def _read_experiment_records(memory_path: Path) -> list[dict[str, Any]]:
    if not memory_path.exists():
        return []
    try:
        raw = json.loads(memory_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []
    if not isinstance(raw, list):
        return []
    return [item for item in raw if isinstance(item, dict)]


def _normalize_experiment(record: dict[str, Any]) -> dict[str, Any]:
    metrics = record.get("metrics") if isinstance(record.get("metrics"), dict) else {}
    experiment_id = (
        record.get("experiment_id")
        or record.get("run_id")
        or record.get("id")
        or record.get("name")
        or "unknown"
    )
    return {
        "experiment_id": str(experiment_id),
        "name": str(record.get("name", experiment_id)),
        "status": str(record.get("status", "unknown")),
        "created_at": str(record.get("created_at", "")),
        "metrics": metrics,
        "metric_family_summary": _metric_family_summary(metrics),
        "artifacts": record.get("artifacts") if isinstance(record.get("artifacts"), dict) else {},
        "params": record.get("params") if isinstance(record.get("params"), dict) else {},
        "notes": str(record.get("notes", "")),
    }


def _metric_family_summary(metrics: dict[str, Any]) -> dict[str, bool]:
    return {
        "oos": _has_metric_family(metrics, "oos"),
        "simulation": _has_metric_family(metrics, "simulation"),
        "training": _has_metric_family(metrics, "training"),
        "population": _has_metric_family(metrics, "population"),
        "audit": _has_metric_family(metrics, "audit"),
    }


def _has_metric_family(metrics: dict[str, Any], family: str) -> bool:
    if family in metrics:
        return True
    prefix = f"{family}."
    return any(str(key).startswith(prefix) for key in metrics)


def _fallback_baseline() -> dict[str, Any]:
    metrics = {"oos": {"sharpe": 0.586, "window_count": 19}}
    return {
        "experiment_id": "EXP-20260602-008",
        "name": "Walk-forward OOS baseline",
        "status": "documented",
        "created_at": "",
        "metrics": metrics,
        "metric_family_summary": _metric_family_summary(metrics),
        "artifacts": {},
        "params": {},
        "notes": "Fallback baseline from documented project context; server artifacts may provide richer details.",
    }
