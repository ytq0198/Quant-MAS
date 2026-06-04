"""YAML pipeline recipe schema for M13 orchestration."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class PipelineNode:
    """One node declared in a pipeline recipe."""

    id: str
    tool_name: str
    metric_family: str = "audit"
    depends_on: tuple[str, ...] = ()
    script: str | None = None
    dry_run_stub: dict[str, Any] = field(default_factory=dict)
    allowed_metrics_prefix: tuple[str, ...] = ()

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "PipelineNode":
        node_id = str(payload["id"])
        return cls(
            id=node_id,
            tool_name=str(payload.get("tool_name", payload.get("tool", "data_summary"))),
            metric_family=str(payload.get("metric_family", "audit")),
            depends_on=tuple(str(item) for item in payload.get("depends_on", [])),
            script=str(payload["script"]) if payload.get("script") else None,
            dry_run_stub=dict(payload.get("dry_run_stub", {})),
            allowed_metrics_prefix=tuple(
                str(item) for item in payload.get("allowed_metrics_prefix", [])
            ),
        )

    def to_scheduler_dict(self) -> dict[str, Any]:
        return {
            "node_id": self.id,
            "tool_name": self.tool_name,
            "metric_family": self.metric_family,
            "depends_on": self.depends_on,
            "dry_run_stub": {
                **self.dry_run_stub,
                "script": self.script,
                "allowed_metrics_prefix": list(self.allowed_metrics_prefix),
            },
        }


@dataclass(frozen=True)
class PipelineRecipe:
    """Declarative research pipeline recipe."""

    pipeline_id: str
    version: int
    nodes: tuple[PipelineNode, ...]
    description: str = ""
    metric_families: tuple[str, ...] = ()

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "PipelineRecipe":
        nodes = tuple(PipelineNode.from_dict(item) for item in payload.get("nodes", []))
        if not nodes:
            raise ValueError("pipeline recipe must contain at least one node")
        return cls(
            pipeline_id=str(payload["pipeline_id"]),
            version=int(payload.get("version", 1)),
            description=str(payload.get("description", "")),
            metric_families=tuple(str(item) for item in payload.get("metric_families", [])),
            nodes=nodes,
        )


def load_recipe_yaml(path: str | Path) -> PipelineRecipe:
    """Load a pipeline recipe from YAML."""
    recipe_path = Path(path)
    if not recipe_path.exists():
        raise FileNotFoundError(f"recipe file does not exist: {recipe_path}")
    payload = yaml.safe_load(recipe_path.read_text(encoding="utf-8")) or {}
    if not isinstance(payload, dict):
        raise ValueError(f"recipe YAML must be a mapping: {recipe_path}")
    return PipelineRecipe.from_dict(payload)
