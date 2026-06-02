"""Quant tools package.

This package keeps compatibility with the legacy sibling `quant.py` module
while allowing focused tool modules such as `risk_tool.py`.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

from quant_mas.tools.quant.risk_tool import RiskTool

_legacy_path = Path(__file__).resolve().parent.parent / "quant.py"
_spec = importlib.util.spec_from_file_location("_quant_mas_legacy_quant_tools", _legacy_path)
if _spec is None or _spec.loader is None:
    raise ImportError(f"Unable to load legacy quant tools from {_legacy_path}")
_legacy = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_legacy)

DataSummaryTool = _legacy.DataSummaryTool
BacktestTool = _legacy.BacktestTool
TrainModelTool = _legacy.TrainModelTool
ReportTool = _legacy.ReportTool

__all__ = [
    "BacktestTool",
    "DataSummaryTool",
    "ReportTool",
    "RiskTool",
    "TrainModelTool",
]
