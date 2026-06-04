from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest


EXAMPLE_RECIPES = [
    "ml_baseline.yaml.example",
    "text_enhanced.yaml.example",
    "population_oos.yaml.example",
    "rl_ablation.yaml.example",
]


def test_load_all_example_pipeline_recipes() -> None:
    from quant_mas.orchestration.pipeline_recipe import load_recipe_yaml

    for name in EXAMPLE_RECIPES:
        recipe = load_recipe_yaml(Path("configs/pipelines") / name)
        assert recipe.pipeline_id
        assert recipe.version == 1
        assert recipe.nodes


def test_text_enhanced_recipe_audits_before_walk_forward() -> None:
    from quant_mas.orchestration.pipeline_recipe import load_recipe_yaml
    from quant_mas.orchestration.mcp_scheduler import MCPScheduler

    recipe = load_recipe_yaml(Path("configs/pipelines/text_enhanced.yaml.example"))
    order = MCPScheduler().plan(recipe)
    node_ids = [node.node_id for node in order]

    assert node_ids.index("audit_text_signals") < node_ids.index("walk_forward_eval")


def test_rl_ablation_recipe_does_not_mark_training_as_walk_forward() -> None:
    from quant_mas.orchestration.pipeline_recipe import load_recipe_yaml

    recipe = load_recipe_yaml(Path("configs/pipelines/rl_ablation.yaml.example"))
    families = {node.id: node.metric_family for node in recipe.nodes}

    assert families["rl_train"] in {"training", "simulation"}
    assert families["rl_train"] != "walk_forward"
    assert families["validate_candidate_oos"] == "walk_forward"


def test_recipe_cycle_detection(tmp_path: Path) -> None:
    from quant_mas.orchestration.pipeline_recipe import load_recipe_yaml
    from quant_mas.orchestration.mcp_scheduler import MCPScheduler

    path = tmp_path / "cycle.yaml"
    path.write_text(
        """
pipeline_id: cycle
version: 1
nodes:
  - id: a
    tool_name: data_summary
    depends_on: [b]
  - id: b
    tool_name: report
    depends_on: [a]
""",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="cycle detected"):
        MCPScheduler().plan(load_recipe_yaml(path))


def test_scheduler_runs_yaml_recipe_dry_run(tmp_path: Path) -> None:
    from quant_mas.orchestration.pipeline_recipe import load_recipe_yaml
    from quant_mas.orchestration.mcp_scheduler import MCPScheduler

    recipe = load_recipe_yaml(Path("configs/pipelines/population_oos.yaml.example"))
    result = MCPScheduler().run(recipe, output_dir=tmp_path, dry_run=True)

    assert result.pipeline_id == "population_oos"
    assert result.status == "success"
    assert result.planned_nodes == [
        "export_population_candidates",
        "batch_validate_candidates",
        "compare_experiments",
    ]
    assert result.audit_summary["total_events"] == 3


def test_cli_runs_yaml_recipe_path(tmp_path: Path) -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/run_mcp_pipeline.py",
            "--recipe",
            "configs/pipelines/text_enhanced.yaml.example",
            "--dry-run",
            "--output-dir",
            str(tmp_path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "text_enhanced" in result.stdout
    assert "audit_text_signals" in result.stdout
    assert list(tmp_path.glob("*/audit.jsonl"))


def test_cli_rejects_missing_yaml_recipe(tmp_path: Path) -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/run_mcp_pipeline.py",
            "--recipe",
            str(tmp_path / "missing.yaml"),
            "--dry-run",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert "unknown recipe" in result.stderr or "does not exist" in result.stderr
