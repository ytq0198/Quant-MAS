from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from quant_mas.protocols.mcp.policy import PolicyDecision
from quant_mas.protocols.mcp.types import MCPToolCall


def test_message_bus_publish_subscribe_round_trip() -> None:
    from quant_mas.orchestration.agent_communication import InMemoryMessageBus, PlanMessage

    bus = InMemoryMessageBus()
    message = PlanMessage(sender="coordinator", pipeline_id="mock_research", nodes=["data_check"])

    bus.publish("pipeline.plan", message)

    assert bus.subscribe("pipeline.plan") == [message]
    assert bus.subscribe("missing.topic") == []


def test_audit_log_append_read_tail_and_summary(tmp_path: Path) -> None:
    from quant_mas.orchestration.audit_log import (
        AuditEvent,
        append_audit_event,
        read_audit_tail,
        summarize_audit_log,
    )

    path = tmp_path / "audit.jsonl"
    append_audit_event(
        path,
        AuditEvent(
            pipeline_id="mock_research",
            run_id="run-1",
            node_id="data_check",
            status="success",
            metric_family="audit",
        ),
    )
    append_audit_event(
        path,
        AuditEvent(
            pipeline_id="mock_research",
            run_id="run-1",
            node_id="report",
            status="success",
            metric_family="audit",
            artifacts={"summary": "summary.md"},
        ),
    )

    tail = read_audit_tail(path, limit=1)
    assert tail[0]["node_id"] == "report"
    assert tail[0]["artifacts"] == {"summary": "summary.md"}

    summary = summarize_audit_log(path)
    assert summary["total_events"] == 2
    assert summary["status_counts"] == {"success": 2}
    assert summary["metric_families"] == ["audit"]


def test_scheduler_lists_builtin_recipes() -> None:
    from quant_mas.orchestration.mcp_scheduler import BUILTIN_RECIPES, MCPScheduler

    scheduler = MCPScheduler()

    assert "mock_research" in scheduler.list_recipes()
    assert "text_smoke" in scheduler.list_recipes()
    assert set(BUILTIN_RECIPES) >= {"mock_research", "text_smoke"}


def test_scheduler_dry_run_runs_two_mock_nodes_and_writes_audit(tmp_path: Path) -> None:
    from quant_mas.orchestration.mcp_scheduler import MCPScheduler

    scheduler = MCPScheduler()
    result = scheduler.run("mock_research", output_dir=tmp_path, dry_run=True)

    assert result.pipeline_id == "mock_research"
    assert result.status == "success"
    assert result.planned_nodes == ["data_check", "report"]
    assert [node.node_id for node in result.node_results] == ["data_check", "report"]
    assert result.audit_path.exists()

    audit_rows = [json.loads(line) for line in result.audit_path.read_text(encoding="utf-8").splitlines()]
    assert [row["node_id"] for row in audit_rows] == ["data_check", "report"]
    assert all(row["status"] == "success" for row in audit_rows)


def test_scheduler_text_smoke_orders_audit_before_walk_forward(tmp_path: Path) -> None:
    from quant_mas.orchestration.mcp_scheduler import MCPScheduler

    result = MCPScheduler().run("text_smoke", output_dir=tmp_path, dry_run=True)

    assert result.planned_nodes.index("audit_text_signals") < result.planned_nodes.index(
        "walk_forward_eval"
    )
    families = {node.node_id: node.metric_family for node in result.node_results}
    assert families["audit_text_signals"] == "audit"
    assert families["walk_forward_eval"] == "walk_forward"


def test_scheduler_rejects_unknown_recipe(tmp_path: Path) -> None:
    from quant_mas.orchestration.mcp_scheduler import MCPScheduler

    with pytest.raises(ValueError, match="unknown recipe"):
        MCPScheduler().run("does_not_exist", output_dir=tmp_path, dry_run=True)


def test_scheduler_policy_denies_dangerous_tool_names() -> None:
    from quant_mas.orchestration.mcp_scheduler import evaluate_scheduler_tool_call

    for tool_name in ["shell", "broker_order", "place_order", "secrets_dump"]:
        decision = evaluate_scheduler_tool_call(MCPToolCall(tool_name=tool_name, arguments={}))
        assert decision.decision == PolicyDecision.DENY


def test_scheduler_policy_allows_safe_dry_run_tool() -> None:
    from quant_mas.orchestration.mcp_scheduler import evaluate_scheduler_tool_call

    decision = evaluate_scheduler_tool_call(MCPToolCall(tool_name="data_summary", arguments={}))

    assert decision.decision == PolicyDecision.ALLOW


def test_cli_help() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/run_mcp_pipeline.py", "--help"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "--list-recipes" in result.stdout
    assert "--recipe" in result.stdout


def test_cli_list_recipes() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/run_mcp_pipeline.py", "--list-recipes"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "mock_research" in result.stdout
    assert "text_smoke" in result.stdout


def test_cli_dry_run_writes_audit(tmp_path: Path) -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/run_mcp_pipeline.py",
            "--recipe",
            "mock_research",
            "--dry-run",
            "--output-dir",
            str(tmp_path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "mock_research" in result.stdout
    assert "audit.jsonl" in result.stdout
    assert list(tmp_path.glob("*/audit.jsonl"))
