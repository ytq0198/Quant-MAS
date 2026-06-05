from __future__ import annotations

from typing import Any

_TOOLS: list[dict[str, Any]] = [
    {
        "name": "DataSummaryTool",
        "description": "Summarizes local datasets and experiment metadata.",
        "中文": "总结本地数据集和实验元数据。",
        "allowed_operations": ["read_metadata", "summarize"],
    },
    {
        "name": "BacktestTool",
        "description": "Runs deterministic backtest workflows through Quant Engine.",
        "中文": "通过 Quant Engine 运行确定性回测流程。",
        "allowed_operations": ["run_backtest", "read_report"],
    },
    {
        "name": "TrainModelTool",
        "description": "Starts configured ML training workflows in controlled mode.",
        "中文": "以受控模式启动配置化机器学习训练流程。",
        "allowed_operations": ["run_training", "read_metrics"],
    },
    {
        "name": "ReportTool",
        "description": "Generates readable reports from audited experiment outputs.",
        "中文": "基于经过审计的实验输出生成可读报告。",
        "allowed_operations": ["generate_report", "read_artifact"],
    },
    {
        "name": "RiskTool",
        "description": "Checks risk constraints before any candidate can move forward.",
        "中文": "在候选策略进入下一步之前检查风险约束。",
        "allowed_operations": ["run_risk_check", "read_decision"],
    },
    {
        "name": "MLBacktestTool",
        "description": "Runs ML strategy backtest workflows without live-order access.",
        "中文": "运行机器学习策略回测流程，不提供实盘下单访问。",
        "allowed_operations": ["run_ml_backtest", "read_metrics"],
    },
    {
        "name": "PipelineTool",
        "description": "Runs configured YAML pipeline recipes under audit policy.",
        "中文": "在审计策略下运行配置化 YAML 流水线配方。",
        "allowed_operations": ["run_pipeline", "dry_run", "read_audit"],
    },
]


def list_tools() -> list[dict[str, Any]]:
    """Return controlled Phase 2 tool metadata.

    返回 Phase 2 受控工具元数据。
    """
    return _TOOLS
