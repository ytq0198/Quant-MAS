"""Tool registry helpers for workflow orchestration."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from quant_mas.models import BasePredictiveModel
from quant_mas.tools import (
    DataSummaryTool,
    MLBacktestTool,
    ReportTool,
    RiskTool,
    ToolRegistry,
    TrainModelTool,
)


class WorkflowMockModel(BasePredictiveModel):
    """Deterministic mock model for dry-run training and ML backtesting."""

    def __init__(self, **params: Any) -> None:
        self.feature_columns: list[str] = []
        self.threshold = 0.0

    def fit(self, features: pd.DataFrame, target: pd.Series) -> "WorkflowMockModel":
        self.feature_columns = list(features.columns)
        key = "return_1" if "return_1" in features.columns else self.feature_columns[0]
        self.threshold = float(features[key].median())
        return self

    def predict(self, features: pd.DataFrame) -> pd.Series:
        return (self.predict_proba(features) >= 0.5).astype(int)

    def predict_proba(self, features: pd.DataFrame) -> pd.Series:
        key = "return_1" if "return_1" in features.columns else list(features.columns)[0]
        values = features[key].astype(float)
        minimum = values.min()
        maximum = values.max()
        if minimum == maximum:
            return pd.Series([0.5] * len(values), index=features.index)
        return (values - minimum) / (maximum - minimum)

    def save(self, path: str | Path) -> Path:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("workflow mock model", encoding="utf-8")
        return target

    @classmethod
    def load(cls, path: str | Path) -> "WorkflowMockModel":
        return cls()

    def metadata(self) -> dict[str, Any]:
        return {"model_type": "workflow_mock", "feature_columns": self.feature_columns}


def create_default_tool_registry(*, dry_run: bool = False) -> ToolRegistry:
    """Create tools used by ResearchWorkflow."""
    model_factory = WorkflowMockModel if dry_run else None
    model = WorkflowMockModel() if dry_run else None
    return ToolRegistry(
        [
            DataSummaryTool(),
            TrainModelTool(model_factory=model_factory),
            MLBacktestTool(model=model),
            RiskTool(),
            ReportTool(),
        ]
    )
