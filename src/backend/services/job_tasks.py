from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Callable

from backend.services.config import (
    get_artifact_root,
    get_audit_dir,
    get_experiment_memory_path,
    get_paper_dir,
)
from backend.services.job_store import get_job_record

ProgressCallback = Callable[[float, str], None]


def run_job_task(job_id: str, progress: ProgressCallback) -> dict[str, Any]:
    """Dispatch a queued job to the appropriate research task."""
    job = get_job_record(job_id)
    if not job:
        raise ValueError(f"Unknown job: {job_id}")

    job_type = job["type"]
    params = job.get("params") if isinstance(job.get("params"), dict) else {}

    if job_type == "backtest":
        return _run_backtest(params, progress)
    if job_type == "walk_forward_oos":
        return _run_walk_forward_oos(params, progress)
    if job_type == "paper_export":
        return _run_paper_export(params, progress)
    raise ValueError(f"Unsupported job type: {job_type}")


def _project_root() -> Path:
    root = get_artifact_root()
    if (root / "src" / "quant_mas").exists():
        return root
    configured = os.getenv("QUANT_MAS_PROJECT_ROOT")
    if configured:
        return Path(configured).expanduser().resolve()
    return root


def _resolve_path(value: str | None, default: Path) -> Path:
    if not value:
        return default
    path = Path(value).expanduser()
    if path.is_absolute():
        return path.resolve()
    return (_project_root() / path).resolve()


def _run_backtest(params: dict[str, Any], progress: ProgressCallback) -> dict[str, Any]:
    from quant_mas.tools.quant import BacktestTool

    progress(0.1, "Loading backtest configuration.")
    root = _project_root()
    config_path = _resolve_path(params.get("config_path"), root / "configs" / "backtest.yaml")
    storage_config = _resolve_path(params.get("storage_config"), root / "configs" / "storage.yaml")
    output_dir = _resolve_path(params.get("output_dir"), root / "outputs" / "reports" / "backtest_latest")
    experiment_name = str(params.get("experiment_name", "ui_backtest"))

    kwargs: dict[str, Any] = {
        "config_path": str(config_path),
        "storage_config": str(storage_config),
        "output_dir": str(output_dir),
        "experiment_name": experiment_name,
    }
    if params.get("input_path"):
        kwargs["input_path"] = str(
            _resolve_path(str(params["input_path"]), root / "data" / "raw" / "market_data.parquet")
        )

    progress(0.25, "Running deterministic backtest through Quant Engine.")
    if params.get("fast_window") is not None or params.get("slow_window") is not None:
        if params.get("fast_window") is not None:
            kwargs["fast_window"] = int(params["fast_window"])
        if params.get("slow_window") is not None:
            kwargs["slow_window"] = int(params["slow_window"])
        result = _run_backtest_with_overrides(kwargs, progress)
    else:
        result = BacktestTool().run(**kwargs)

    progress(0.95, "Backtest artifacts saved.")
    metadata = result.metadata if isinstance(result.metadata, dict) else {}
    metrics = metadata.get("metrics") if isinstance(metadata.get("metrics"), dict) else {}
    artifacts = metadata.get("artifacts") if isinstance(metadata.get("artifacts"), dict) else {}
    return {
        "summary": result.content,
        "metrics": metrics,
        "artifacts": artifacts,
        "experiment_name": experiment_name,
        "output_dir": str(output_dir),
        "metric_family": "backtest.summary",
        "research_only": True,
    }


def _stringify_paths(paths: dict[str, Path]) -> dict[str, str]:
    return {key: str(value) for key, value in paths.items()}


def _run_backtest_with_overrides(kwargs: dict[str, Any], progress: ProgressCallback) -> Any:
    import yaml
    from quant_mas.backtest import BacktestEngine, CommissionModel, SlippageModel, save_backtest_report
    from quant_mas.data import DataCatalog, ParquetStorage
    from quant_mas.memory import ExperimentMemory
    from quant_mas.strategies import MovingAverageCrossStrategy
    from quant_mas.tools.base import ToolResult

    config_path = Path(kwargs["config_path"])
    storage_config = Path(kwargs["storage_config"])
    config = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    strategy_config = dict(config.get("strategy", {}))
    if kwargs.get("fast_window") is not None:
        strategy_config["fast_window"] = kwargs["fast_window"]
    if kwargs.get("slow_window") is not None:
        strategy_config["slow_window"] = kwargs["slow_window"]
    strategy_config.setdefault("name", "moving_average_cross")
    config["strategy"] = strategy_config

    catalog = DataCatalog.from_yaml(storage_config)
    input_path = Path(kwargs.get("input_path") or catalog.path_for("raw_data_dir", "market_data.parquet"))
    output_dir = Path(kwargs["output_dir"])
    experiment_name = kwargs["experiment_name"]

    progress(0.4, f"Loading market data from {input_path.name}.")
    strategy = MovingAverageCrossStrategy(
        fast_window=strategy_config.get("fast_window", 5),
        slow_window=strategy_config.get("slow_window", 20),
    )
    engine = BacktestEngine(
        strategy=strategy,
        initial_cash=config.get("portfolio", {}).get("initial_cash", 100_000.0),
        commission_model=CommissionModel(config.get("costs", {}).get("commission_bps", 0.0)),
        slippage_model=SlippageModel(config.get("costs", {}).get("slippage_bps", 0.0)),
    )
    progress(0.55, "Executing backtest.")
    result = engine.run(ParquetStorage().load(input_path))
    progress(0.8, "Writing backtest report artifacts.")
    artifacts = save_backtest_report(result, output_dir, title=experiment_name, params=config)
    memory_path = catalog.path_for("reports_dir", "experiments.json")
    ExperimentMemory(memory_path).add(
        name=experiment_name,
        metrics=result.metrics,
        artifacts=artifacts,
        params=config,
    )
    artifact_strings = _stringify_paths(artifacts)
    return ToolResult(
        content=(
            f"Backtest completed. total_return={result.metrics['total_return']:.6g}, "
            f"sharpe={result.metrics['sharpe']:.6g}, "
            f"max_drawdown={result.metrics['max_drawdown']:.6g}. "
            f"Summary: {artifact_strings['summary']}"
        ),
        metadata={
            "metrics": result.metrics,
            "artifacts": artifact_strings,
            "experiment_memory": str(memory_path),
        },
    )


def _run_walk_forward_oos(params: dict[str, Any], progress: ProgressCallback) -> dict[str, Any]:
    import yaml
    from quant_mas.backtest import run_walk_forward_from_config

    progress(0.1, "Loading walk-forward OOS configuration.")
    root = _project_root()
    config_path = _resolve_path(params.get("config_path"), root / "configs" / "walk_forward.yaml")
    storage_config = _resolve_path(params.get("storage_config"), root / "configs" / "storage.yaml")
    config = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}

    features_path = _resolve_path(params.get("features_path"), root / "data" / "features" / "features.parquet")
    output_dir = _resolve_path(params.get("output_dir"), root / "outputs" / "reports" / "walk_forward_latest")
    experiment_name = params.get("experiment_name")

    progress(0.3, "Running walk-forward OOS evaluation.")
    payload = run_walk_forward_from_config(
        config=config,
        storage_config=storage_config,
        features_path=features_path if features_path.exists() else None,
        output_dir=output_dir,
        experiment_name=str(experiment_name) if experiment_name else None,
    )
    progress(0.9, "Walk-forward OOS artifacts saved.")
    metrics = payload.get("metrics") if isinstance(payload.get("metrics"), dict) else {}
    artifacts = payload.get("artifacts") if isinstance(payload.get("artifacts"), dict) else {}
    sharpe = metrics.get("oos_sharpe", metrics.get("sharpe"))
    return {
        "summary": f"Walk-forward OOS completed. Sharpe={sharpe}.",
        "metrics": metrics,
        "artifacts": {key: str(value) for key, value in artifacts.items()},
        "metric_family": "oos",
        "paper_grade": True,
        "experiment_name": experiment_name or config.get("experiment_name", "walk_forward_oos"),
        "output_dir": str(output_dir),
    }


def _run_paper_export(params: dict[str, Any], progress: ProgressCallback) -> dict[str, Any]:
    from quant_mas.research.paper_artifacts import export_paper_artifacts

    progress(0.15, "Preparing paper artifact export.")
    memory_path = _resolve_path(params.get("memory_path"), get_experiment_memory_path())
    audit_dir = _resolve_path(params.get("audit_dir"), get_audit_dir())
    output_dir = _resolve_path(params.get("output_dir"), get_paper_dir())

    progress(0.45, "Exporting paper tables and summaries.")
    result = export_paper_artifacts(
        memory_path=memory_path,
        audit_dir=audit_dir if audit_dir.exists() else None,
        output_dir=output_dir,
    )
    progress(0.9, "Paper export completed.")
    return {
        "summary": "Paper artifacts exported.",
        "artifacts": {key: str(value) for key, value in result.items()},
        "output_dir": str(output_dir),
        "metric_family": "audit",
    }


def load_backtest_from_output(output_dir: Path) -> dict[str, Any] | None:
    """Load backtest summary from saved report directory."""
    metrics_path = output_dir / "metrics.json"
    if not metrics_path.exists():
        return None
    try:
        metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    return {
        "metrics": metrics,
        "chart": _equity_chart_from_csv(output_dir / "equity_curve.csv"),
        "output_dir": str(output_dir),
    }


def _equity_chart_from_csv(path: Path, points: int = 12) -> list[dict[str, Any]]:
    if not path.exists():
        return [{"label": "start", "equity": 1.0}, {"label": "end", "equity": 1.0}]
    try:
        import pandas as pd

        frame = pd.read_csv(path)
        if frame.empty:
            return [{"label": "empty", "equity": 1.0}]
        column = "equity" if "equity" in frame.columns else frame.columns[-1]
        values = frame[column].astype(float).tolist()
        if len(values) <= points:
            sampled = values
        else:
            step = max(1, len(values) // points)
            sampled = values[::step][:points]
        base = sampled[0] if sampled and sampled[0] else 1.0
        normalized = [value / base for value in sampled]
        return [{"label": f"p{i}", "equity": value} for i, value in enumerate(normalized)]
    except Exception:
        return [{"label": "start", "equity": 1.0}, {"label": "end", "equity": 1.0}]
