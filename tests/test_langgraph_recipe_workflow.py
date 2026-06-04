from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest


def test_langgraph_recipe_fallback_runs_without_langgraph(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import quant_mas.orchestration.langgraph_recipe_workflow as module

    monkeypatch.setattr(module, "LANGGRAPH_AVAILABLE", False)
    monkeypatch.setattr(module, "StateGraph", None)

    result = module.run_langgraph_recipe_workflow(
        "mock_research",
        output_dir=tmp_path,
        dry_run=True,
    )

    assert result.pipeline_id == "mock_research"
    assert result.status == "success"
    assert result.planned_nodes == ["data_check", "report"]
    assert result.audit_path.exists()


def test_build_langgraph_from_recipe_returns_none_when_unavailable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import quant_mas.orchestration.langgraph_recipe_workflow as module
    from quant_mas.orchestration.pipeline_recipe import load_recipe_yaml

    monkeypatch.setattr(module, "LANGGRAPH_AVAILABLE", False)
    monkeypatch.setattr(module, "StateGraph", None)

    recipe = load_recipe_yaml("configs/pipelines/text_enhanced.yaml.example")

    assert module.build_langgraph_from_recipe(recipe) is None


def test_langgraph_recipe_builds_when_available() -> None:
    pytest.importorskip("langgraph")
    from quant_mas.orchestration.langgraph_recipe_workflow import build_langgraph_from_recipe
    from quant_mas.orchestration.pipeline_recipe import load_recipe_yaml

    recipe = load_recipe_yaml("configs/pipelines/text_enhanced.yaml.example")

    graph = build_langgraph_from_recipe(recipe)

    assert graph is not None


def test_langgraph_recipe_run_preserves_text_order_when_available(tmp_path: Path) -> None:
    pytest.importorskip("langgraph")
    from quant_mas.orchestration.langgraph_recipe_workflow import run_langgraph_recipe_workflow

    result = run_langgraph_recipe_workflow(
        "configs/pipelines/text_enhanced.yaml.example",
        output_dir=tmp_path,
        dry_run=True,
    )

    assert result.planned_nodes.index("audit_text_signals") < result.planned_nodes.index(
        "walk_forward_eval"
    )
    assert result.audit_summary["total_events"] == 7


def test_run_mcp_pipeline_cli_langgraph_backend(tmp_path: Path) -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/run_mcp_pipeline.py",
            "--backend",
            "langgraph",
            "--recipe",
            "configs/pipelines/rl_ablation.yaml.example",
            "--dry-run",
            "--output-dir",
            str(tmp_path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "rl_ablation" in result.stdout
    assert "validate_candidate_oos" in result.stdout
    assert list(tmp_path.glob("*/audit.jsonl"))
