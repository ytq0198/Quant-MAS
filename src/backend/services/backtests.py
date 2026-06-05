from __future__ import annotations

from pathlib import Path
from typing import Any

from backend.services.job_store import get_job_record
from backend.services.job_tasks import _project_root, load_backtest_from_output


def get_backtest_summary(backtest_id: str) -> dict[str, Any]:
    """Return backtest summary from artifacts, job result, or fixture fallback."""
    loaded = _load_latest_backtest_artifact()
    if backtest_id.startswith("job-"):
        job_loaded = _load_backtest_from_job(backtest_id)
        if job_loaded:
            return job_loaded
    if loaded and backtest_id in {"demo-backtest", "latest", "backtest_latest"}:
        return _build_summary(backtest_id, loaded)
    if loaded:
        return _build_summary("latest", loaded)
    return _fixture_summary(backtest_id)


def _load_latest_backtest_artifact() -> dict[str, Any] | None:
    root = _project_root()
    output_dir = root / "outputs" / "reports" / "backtest_latest"
    return load_backtest_from_output(output_dir)


def _load_backtest_from_job(job_id: str) -> dict[str, Any] | None:
    job = get_job_record(job_id)
    if not job or job.get("type") != "backtest":
        return None
    result = job.get("result")
    if not isinstance(result, dict):
        return None
    output_dir = Path(str(result.get("output_dir", "")))
    loaded = load_backtest_from_output(output_dir) if output_dir.exists() else None
    if loaded:
        return _build_summary(job_id, loaded, experiment_name=result.get("experiment_name"))
    metrics = result.get("metrics") if isinstance(result.get("metrics"), dict) else {}
    if metrics:
        return {
            "id": job_id,
            "title": str(result.get("experiment_name", "Backtest job result")),
            "metric_family": "backtest.summary",
            "is_oos": False,
            "research_only": True,
            "strategy": "moving_average_cross",
            "chart": [{"label": "start", "equity": 1.0}, {"label": "end", "equity": 1.0}],
            "notes": ["Loaded from completed backtest job result."],
            "disclaimer": "Research only; not financial advice; not a live-trading signal.",
            "metrics": metrics,
        }
    return None


def _build_summary(
    backtest_id: str,
    loaded: dict[str, Any],
    *,
    experiment_name: str | None = None,
) -> dict[str, Any]:
    metrics = loaded.get("metrics") if isinstance(loaded.get("metrics"), dict) else {}
    return {
        "id": backtest_id,
        "title": experiment_name or "Latest deterministic backtest",
        "metric_family": "backtest.summary",
        "is_oos": False,
        "research_only": True,
        "strategy": "moving_average_cross",
        "time_range": "artifact-backed",
        "metrics": metrics,
        "chart": loaded.get("chart") or [{"label": "start", "equity": 1.0}],
        "notes": [
            "Backtest summaries are not paper-grade OOS conclusions.",
            "Use walk-forward OOS for paper-grade baseline comparison.",
        ],
        "disclaimer": "Research only; not financial advice; not a live-trading signal.",
        "source": "server_artifact",
        "output_dir": loaded.get("output_dir"),
    }


def _fixture_summary(backtest_id: str) -> dict[str, Any]:
    return {
        "id": backtest_id,
        "title": "Demo deterministic backtest summary",
        "metric_family": "backtest.summary",
        "is_oos": False,
        "research_only": True,
        "strategy": "MLSignalStrategy candidate",
        "chart": [
            {"label": "start", "equity": 1.0},
            {"label": "mid", "equity": 1.03},
            {"label": "end", "equity": 1.01},
        ],
        "notes": [
            "Backtest summaries are not paper-grade OOS conclusions.",
            "Use walk-forward OOS for paper-grade baseline comparison.",
            "Submit a backtest job from the UI or run scripts/run_backtest.py to populate artifacts.",
        ],
        "disclaimer": "Research only; not financial advice; not a live-trading signal.",
        "source": "fallback_fixture",
    }
