"""ML backtest tool."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from quant_mas.models import BasePredictiveModel
from quant_mas.tools.base import BaseTool, ToolResult


class MLBacktestTool(BaseTool):
    """Run the ML signal backtest without spawning a subprocess."""

    def __init__(self, model: BasePredictiveModel | None = None) -> None:
        super().__init__(
            name="ml_backtest",
            description="Run ML signal backtest and save report artifacts.",
        )
        self.model = model

    def run(self, **kwargs: Any) -> ToolResult:
        from scripts.run_ml_backtest import run_ml_backtest

        config_path = Path(kwargs.get("config_path", "configs/backtest_ml.yaml")).expanduser()
        storage_config = Path(kwargs.get("storage_config", "configs/storage.yaml")).expanduser()
        config = _load_yaml(config_path)
        result = run_ml_backtest(
            config=config,
            storage_config=storage_config,
            features_path=_optional_path(kwargs.get("features_path")),
            model_path=_optional_path(kwargs.get("model_path")),
            output_dir=_optional_path(kwargs.get("output_dir")),
            experiment_name=kwargs.get("experiment_name"),
            model=kwargs.get("model", self.model),
        )
        metrics = result["metrics"]
        return ToolResult(
            content=(
                "ML backtest completed. "
                f"total_return={metrics.get('total_return', 0.0):.6g}, "
                f"sharpe={metrics.get('sharpe', 0.0):.6g}. "
                f"Summary: {result['artifacts'].get('summary', '')}"
            ),
            metadata={
                "metrics": metrics,
                "artifacts": result["artifacts"],
                "experiment_memory": result["experiment_memory"],
                "feature_columns": result.get("feature_columns", []),
            },
        )


def _load_yaml(path: Path) -> dict[str, Any]:
    import yaml

    with path.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file) or {}


def _optional_path(value: str | Path | None) -> Path | None:
    return Path(value).expanduser() if value is not None else None
