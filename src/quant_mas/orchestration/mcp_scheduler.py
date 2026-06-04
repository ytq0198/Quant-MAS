"""Minimal internal MCP-style scheduler for research orchestration dry-runs."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from quant_mas.orchestration.agent_communication import (
    AuditMessage,
    InMemoryMessageBus,
    NodeResultMessage,
    PlanMessage,
)
from quant_mas.orchestration.audit_log import AuditEvent, append_audit_event, summarize_audit_log
from quant_mas.protocols.mcp.policy import PolicyEvaluation, ToolPolicy, evaluate_tool_call
from quant_mas.protocols.mcp.types import MCPToolCall


@dataclass(frozen=True)
class SchedulerNode:
    """One dry-run scheduler node."""

    node_id: str
    tool_name: str
    metric_family: str = "audit"
    depends_on: tuple[str, ...] = ()
    dry_run_stub: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class SchedulerNodeResult:
    """Result for one scheduler node."""

    node_id: str
    status: str
    metric_family: str
    artifacts: dict[str, str] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class SchedulerResult:
    """Result for one scheduler run."""

    pipeline_id: str
    run_id: str
    status: str
    planned_nodes: list[str]
    node_results: list[SchedulerNodeResult]
    audit_path: Path
    audit_summary: dict[str, Any]


BUILTIN_RECIPES: dict[str, tuple[SchedulerNode, ...]] = {
    "mock_research": (
        SchedulerNode(
            node_id="data_check",
            tool_name="data_summary",
            metric_family="audit",
            dry_run_stub={"rows": 0, "status": "dry_run"},
        ),
        SchedulerNode(
            node_id="report",
            tool_name="report",
            metric_family="audit",
            depends_on=("data_check",),
            dry_run_stub={"summary": "dry-run report"},
        ),
    ),
    "text_smoke": (
        SchedulerNode(
            node_id="align_real_news",
            tool_name="data_summary",
            metric_family="audit",
            dry_run_stub={"aligned": 0, "dropped": 0},
        ),
        SchedulerNode(
            node_id="audit_text_signals",
            tool_name="data_summary",
            metric_family="audit",
            depends_on=("align_real_news",),
            dry_run_stub={"coverage_ratio": 0.0},
        ),
        SchedulerNode(
            node_id="walk_forward_eval",
            tool_name="backtest",
            metric_family="walk_forward",
            depends_on=("audit_text_signals",),
            dry_run_stub={"oos": "not_computed_in_dry_run"},
        ),
    ),
}


def evaluate_scheduler_tool_call(
    call: MCPToolCall, policy: ToolPolicy | None = None
) -> PolicyEvaluation:
    """Evaluate scheduler tool calls with the existing MCP ToolPolicy."""
    return evaluate_tool_call(call, policy or ToolPolicy())


class MCPScheduler:
    """Mock-first scheduler for M13.0 internal research orchestration."""

    def __init__(
        self,
        *,
        recipes: dict[str, tuple[SchedulerNode, ...]] | None = None,
        policy: ToolPolicy | None = None,
        message_bus: InMemoryMessageBus | None = None,
    ) -> None:
        self.recipes = dict(recipes or BUILTIN_RECIPES)
        self.policy = policy or ToolPolicy()
        self.message_bus = message_bus or InMemoryMessageBus()

    def list_recipes(self) -> list[str]:
        return sorted(self.recipes)

    def plan(self, recipe: str) -> list[SchedulerNode]:
        nodes = self._recipe_nodes(recipe)
        return _topological_order(nodes)

    def run(
        self,
        recipe: str,
        *,
        output_dir: str | Path = "outputs/pipelines",
        dry_run: bool = True,
        run_id: str | None = None,
    ) -> SchedulerResult:
        if not dry_run:
            raise ValueError("M13.0 scheduler only supports dry_run=True")

        planned = self.plan(recipe)
        actual_run_id = run_id or f"{recipe}_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}_{uuid4().hex[:8]}"
        run_dir = Path(output_dir) / actual_run_id
        audit_path = run_dir / "audit.jsonl"
        self.message_bus.publish(
            "pipeline.plan",
            PlanMessage(
                sender="mcp_scheduler",
                pipeline_id=recipe,
                nodes=[node.node_id for node in planned],
            ),
        )

        results: list[SchedulerNodeResult] = []
        for node in planned:
            started = time.perf_counter()
            decision = evaluate_scheduler_tool_call(
                MCPToolCall(tool_name=node.tool_name, arguments={}),
                self.policy,
            )
            if decision.decision.value != "allow":
                duration_ms = int((time.perf_counter() - started) * 1000)
                append_audit_event(
                    audit_path,
                    AuditEvent(
                        pipeline_id=recipe,
                        run_id=actual_run_id,
                        node_id=node.node_id,
                        status="denied",
                        metric_family=node.metric_family,
                        duration_ms=duration_ms,
                        error=decision.reason,
                    ),
                )
                raise PermissionError(decision.reason)

            artifacts = {"dry_run": f"{node.node_id}.json"}
            metadata = dict(node.dry_run_stub)
            duration_ms = int((time.perf_counter() - started) * 1000)
            result = SchedulerNodeResult(
                node_id=node.node_id,
                status="success",
                metric_family=node.metric_family,
                artifacts=artifacts,
                metadata=metadata,
            )
            results.append(result)
            append_audit_event(
                audit_path,
                AuditEvent(
                    pipeline_id=recipe,
                    run_id=actual_run_id,
                    node_id=node.node_id,
                    status=result.status,
                    metric_family=node.metric_family,
                    duration_ms=duration_ms,
                    artifacts=artifacts,
                    metadata=metadata,
                ),
            )
            self.message_bus.publish(
                "pipeline.node_finished",
                NodeResultMessage(
                    sender="mcp_scheduler",
                    pipeline_id=recipe,
                    node_id=node.node_id,
                    status=result.status,
                    artifacts=artifacts,
                    metadata=metadata,
                ),
            )
            self.message_bus.publish(
                "pipeline.audit",
                AuditMessage(
                    sender="mcp_scheduler",
                    pipeline_id=recipe,
                    node_id=node.node_id,
                    audit_path=str(audit_path),
                ),
            )

        return SchedulerResult(
            pipeline_id=recipe,
            run_id=actual_run_id,
            status="success",
            planned_nodes=[node.node_id for node in planned],
            node_results=results,
            audit_path=audit_path,
            audit_summary=summarize_audit_log(audit_path),
        )

    def _recipe_nodes(self, recipe: str) -> tuple[SchedulerNode, ...]:
        if recipe not in self.recipes:
            available = ", ".join(self.list_recipes())
            raise ValueError(f"unknown recipe: {recipe}. Available recipes: {available}")
        return self.recipes[recipe]


def _topological_order(nodes: tuple[SchedulerNode, ...]) -> list[SchedulerNode]:
    by_id = {node.node_id: node for node in nodes}
    if len(by_id) != len(nodes):
        raise ValueError("duplicate scheduler node id")

    ordered: list[SchedulerNode] = []
    temporary: set[str] = set()
    permanent: set[str] = set()

    def visit(node_id: str) -> None:
        if node_id in permanent:
            return
        if node_id in temporary:
            raise ValueError(f"cycle detected at node: {node_id}")
        if node_id not in by_id:
            raise ValueError(f"unknown dependency node: {node_id}")
        temporary.add(node_id)
        for dependency in by_id[node_id].depends_on:
            visit(dependency)
        temporary.remove(node_id)
        permanent.add(node_id)
        ordered.append(by_id[node_id])

    for node in nodes:
        visit(node.node_id)
    return ordered
