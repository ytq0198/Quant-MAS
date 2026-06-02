"""End-to-end pipeline tool."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any

from quant_mas.pipeline import PipelineResult, run_quant_pipeline
from quant_mas.tools.base import BaseTool, ToolResult


class PipelineTool(BaseTool):
    """Run the deterministic quant pipeline with network disabled by default."""

    def __init__(
        self,
        pipeline_runner: Callable[..., PipelineResult] | None = None,
    ) -> None:
        super().__init__(
            name="pipeline",
            description="Run end-to-end quant pipeline using local data by default.",
        )
        self.pipeline_runner = pipeline_runner or run_quant_pipeline

    def run(self, **kwargs: Any) -> ToolResult:
        result = self.pipeline_runner(
            symbols=list(kwargs.get("symbols") or ["AAPL", "MSFT", "SPY"]),
            start=kwargs.get("start", "2018-01-01"),
            end=kwargs.get("end", "2025-12-31"),
            raw_dir=_optional_path(kwargs.get("raw_dir")),
            features_dir=_optional_path(kwargs.get("features_dir")),
            output_dir=_optional_path(kwargs.get("output_dir")),
            storage_config=Path(kwargs.get("storage_config", "configs/storage.yaml")).expanduser(),
            features_config=Path(kwargs.get("features_config", "configs/features.yaml")).expanduser(),
            backtest_config=Path(kwargs.get("backtest_config", "configs/backtest.yaml")).expanduser(),
            skip_download=bool(kwargs.get("skip_download", True)),
            skip_features=bool(kwargs.get("skip_features", True)),
            strategy_name=kwargs.get("strategy_name", "ma_cross"),
            experiment_name=kwargs.get("experiment_name", "agent_pipeline"),
            log=kwargs.get("log", lambda message: None),
        )
        artifacts = {key: str(value) for key, value in result.artifacts.items()}
        paths = {
            "raw_path": str(result.raw_path),
            "features_path": str(result.features_path),
            "output_dir": str(result.output_dir),
            "experiment_memory": str(result.experiment_memory_path),
        }
        return ToolResult(
            content=(
                "Pipeline completed. "
                f"total_return={result.metrics.get('total_return', 0.0):.6g}, "
                f"sharpe={result.metrics.get('sharpe', 0.0):.6g}. "
                f"Summary: {artifacts.get('summary', '')}"
            ),
            metadata={
                "metrics": result.metrics,
                "artifacts": artifacts,
                "paths": paths,
            },
        )


def _optional_path(value: str | Path | None) -> Path | None:
    return Path(value).expanduser() if value is not None else None
