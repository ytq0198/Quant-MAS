"""ResearchWorkflow node functions."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

import pandas as pd
import yaml

from quant_mas.data import ParquetStorage
from quant_mas.features import build_feature_table_from_config
from quant_mas.memory import ExperimentMemory
from quant_mas.orchestration.langgraph_state import QuantWorkflowState
from quant_mas.orchestration.node_context import NodeContext
from quant_mas.orchestration.registry import WorkflowMockModel
from quant_mas.orchestration.workflow_events import WorkflowNodeEvent
from quant_mas.tools import ToolRegistry


def node_data_check(
    state: QuantWorkflowState,
    *,
    tools: ToolRegistry,
    context: NodeContext,
) -> QuantWorkflowState:
    return _run_node(state, "data_check", _data_check, tools=tools, context=context)


def node_feature_build(
    state: QuantWorkflowState,
    *,
    tools: ToolRegistry,
    context: NodeContext,
) -> QuantWorkflowState:
    return _run_node(state, "feature_build", _feature_build, tools=tools, context=context)


def node_train_model(
    state: QuantWorkflowState,
    *,
    tools: ToolRegistry,
    context: NodeContext,
) -> QuantWorkflowState:
    return _run_node(state, "train_model", _train_model, tools=tools, context=context)


def node_ml_backtest(
    state: QuantWorkflowState,
    *,
    tools: ToolRegistry,
    context: NodeContext,
) -> QuantWorkflowState:
    return _run_node(state, "ml_backtest", _ml_backtest, tools=tools, context=context)


def node_risk_check(
    state: QuantWorkflowState,
    *,
    tools: ToolRegistry,
    context: NodeContext,
) -> QuantWorkflowState:
    return _run_node(state, "risk_check", _risk_check, tools=tools, context=context)


def node_report(
    state: QuantWorkflowState,
    *,
    tools: ToolRegistry,
    context: NodeContext,
) -> QuantWorkflowState:
    return _run_node(state, "report", _report, tools=tools, context=context)


NODE_FUNCTIONS = {
    "data_check": node_data_check,
    "feature_build": node_feature_build,
    "train_model": node_train_model,
    "ml_backtest": node_ml_backtest,
    "risk_check": node_risk_check,
    "report": node_report,
}


def _run_node(
    state: QuantWorkflowState,
    node: str,
    implementation: Callable[[QuantWorkflowState, ToolRegistry, NodeContext], None],
    *,
    tools: ToolRegistry,
    context: NodeContext,
) -> QuantWorkflowState:
    state["current_node"] = node
    _append_event(state, node, "node_start", f"Starting {node}")
    try:
        implementation(state, tools, context)
    except Exception as exc:
        message = f"{node} failed: {exc}"
        state["errors"].append(message)
        _append_event(state, node, "node_error", message)
        return state
    state["completed_nodes"].append(node)
    _append_event(state, node, "node_complete", f"Completed {node}")
    return state


def _data_check(
    state: QuantWorkflowState,
    tools: ToolRegistry,
    context: NodeContext,
) -> None:
    raw_path = _path_or_default(state.get("raw_path"), context.work_dir / "raw" / "market_data.parquet")
    if context.dry_run and not raw_path.exists():
        ParquetStorage().save(_synthetic_ohlcv(), raw_path)
    if not ParquetStorage().exists(raw_path):
        raise FileNotFoundError(f"raw parquet not found: {raw_path}")
    result = tools.get("data_summary").run(path=raw_path)
    _append_event(
        state,
        "data_check",
        "tool_call",
        "Called data_summary",
        {"tool_name": "data_summary", "metadata": result.metadata},
    )
    state["raw_path"] = str(raw_path)
    state["artifacts"]["raw_path"] = str(raw_path)


def _feature_build(
    state: QuantWorkflowState,
    tools: ToolRegistry,
    context: NodeContext,
) -> None:
    raw_path = _path_or_default(state.get("raw_path"), context.work_dir / "raw" / "market_data.parquet")
    features_path = _path_or_default(
        state.get("features_path"),
        context.work_dir / "features" / "features.parquet",
    )
    if context.dry_run:
        ParquetStorage().save(_synthetic_features(), features_path)
    else:
        config = _load_yaml(context.features_config)
        features = build_feature_table_from_config(ParquetStorage().load(raw_path), config)
        ParquetStorage().save(features, features_path)
    state["features_path"] = str(features_path)
    state["artifacts"]["features_path"] = str(features_path)


def _train_model(
    state: QuantWorkflowState,
    tools: ToolRegistry,
    context: NodeContext,
) -> None:
    features_path = _path_or_default(
        state.get("features_path"),
        context.work_dir / "features" / "features.parquet",
    )
    model_dir = context.work_dir / "models" / "workflow_model"
    result = tools.get("train_model").run(
        config_path=context.train_config,
        storage_config=context.storage_config,
        input_path=features_path,
        output_dir=model_dir,
        experiment_name="workflow_train_model",
    )
    _append_event(
        state,
        "train_model",
        "tool_call",
        "Called train_model",
        {"tool_name": "train_model", "metadata": result.metadata},
    )
    artifacts = result.metadata.get("artifacts", {})
    state["artifacts"].update(artifacts)
    state["metrics"].update(result.metadata.get("metrics", {}))
    if "model" in artifacts:
        state["model_path"] = artifacts["model"]


def _ml_backtest(
    state: QuantWorkflowState,
    tools: ToolRegistry,
    context: NodeContext,
) -> None:
    features_path = _path_or_default(
        state.get("features_path"),
        context.work_dir / "features" / "features.parquet",
    )
    output_dir = context.work_dir / "reports" / "ml_backtest"
    kwargs: dict[str, Any] = {
        "config_path": context.ml_backtest_config,
        "storage_config": context.storage_config,
        "features_path": features_path,
        "output_dir": output_dir,
        "experiment_name": "workflow_ml_backtest",
    }
    if context.dry_run:
        kwargs["model"] = WorkflowMockModel()
    result = tools.get("ml_backtest").run(**kwargs)
    _append_event(
        state,
        "ml_backtest",
        "tool_call",
        "Called ml_backtest",
        {"tool_name": "ml_backtest", "metadata": result.metadata},
    )
    artifacts = result.metadata.get("artifacts", {})
    state["artifacts"].update(artifacts)
    state["metrics"].update(result.metadata.get("metrics", {}))
    if "equity_curve" in artifacts:
        state["equity_path"] = artifacts["equity_curve"]


def _risk_check(
    state: QuantWorkflowState,
    tools: ToolRegistry,
    context: NodeContext,
) -> None:
    targets_path = _path_or_default(
        state.get("targets_path"),
        context.work_dir / "risk" / "targets.parquet",
    )
    if context.dry_run and not targets_path.exists():
        ParquetStorage().save(_synthetic_targets(), targets_path)
    result = tools.get("risk_check").run(
        targets_path=targets_path,
        config_path=context.risk_config,
        equity_path=state.get("equity_path"),
        clip=True,
    )
    _append_event(
        state,
        "risk_check",
        "tool_call",
        "Called risk_check",
        {"tool_name": "risk_check", "metadata": result.metadata},
    )
    state["targets_path"] = str(targets_path)
    state["metrics"]["risk"] = {
        "approved": result.metadata.get("approved"),
        "status": result.metadata.get("status"),
        "violations": result.metadata.get("violations", []),
    }


def _report(
    state: QuantWorkflowState,
    tools: ToolRegistry,
    context: NodeContext,
) -> None:
    if context.dry_run:
        _ensure_stub_experiment(context, state)
    result = tools.get("report").run(storage_config=context.storage_config)
    _append_event(
        state,
        "report",
        "tool_call",
        "Called report",
        {"tool_name": "report", "metadata": result.metadata},
    )
    state["artifacts"]["summary"] = result.metadata.get("summary", "")


def _ensure_stub_experiment(context: NodeContext, state: QuantWorkflowState) -> None:
    import yaml
    from quant_mas.data import DataCatalog

    catalog = DataCatalog.from_yaml(context.storage_config)
    memory_path = catalog.path_for("reports_dir", "experiments.json")
    summary = context.work_dir / "reports" / "workflow_summary.md"
    summary.parent.mkdir(parents=True, exist_ok=True)
    if not summary.exists():
        summary.write_text("# Workflow Dry Run\n\nSynthetic dry-run report.\n", encoding="utf-8")
    try:
        latest = ExperimentMemory(memory_path).latest()
        summary_value = latest.artifacts.get("summary", "")
        if summary_value and Path(summary_value).exists():
            return
    except ValueError:
        pass
    ExperimentMemory(memory_path).add(
        name="workflow_dry_run_report",
        metrics=state["metrics"],
        artifacts={"summary": summary},
        params={"dry_run": True},
    )


def _append_event(
    state: QuantWorkflowState,
    node: str,
    event_type: str,
    message: str,
    metadata: dict[str, Any] | None = None,
) -> None:
    state["events"].append(
        WorkflowNodeEvent(
            event_type=event_type,
            node=node,
            message=message,
            metadata=metadata or {},
        ).to_dict()
    )


def _path_or_default(value: str | None, default: Path) -> Path:
    path = Path(value).expanduser() if value else default
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def _load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file) or {}


def _synthetic_ohlcv(days: int = 30) -> pd.DataFrame:
    rows = []
    for index in range(days):
        close = 10.0 + index * 0.5
        rows.append(
            {
                "date": pd.Timestamp("2026-01-01") + pd.Timedelta(days=index),
                "symbol": "AAA",
                "open": close,
                "high": close + 1.0,
                "low": close - 1.0,
                "close": close,
                "volume": 1000 + index,
            }
        )
    return pd.DataFrame(rows)


def _synthetic_features(days: int = 30) -> pd.DataFrame:
    rows = []
    for index in range(days):
        close = 10.0 + index * 0.5
        rows.append(
            {
                "date": pd.Timestamp("2026-01-01") + pd.Timedelta(days=index),
                "symbol": "AAA",
                "open": close,
                "high": close + 1.0,
                "low": close - 1.0,
                "close": close,
                "volume": 1000 + index,
                "return_1": index / 100.0,
                "ma_5": close / 2.0,
                "future_return_5": 0.01 if index % 2 else -0.01,
                "future_direction_5": 1 if index % 2 else 0,
            }
        )
    return pd.DataFrame(rows)


def _synthetic_targets() -> pd.DataFrame:
    return pd.DataFrame({"symbol": ["AAA"], "target_weight": [0.1]})
