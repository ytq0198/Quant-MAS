from __future__ import annotations

import json
from pathlib import Path

from quant_mas.memory import ExperimentMemory
from quant_mas.research import (
    BaselineRegistry,
    BaselineRun,
    build_comparison_table,
    collect_experiment_metrics,
)
from scripts.compare_experiments import compare_experiments


def seed_memory(path: Path) -> ExperimentMemory:
    memory = ExperimentMemory(path)
    memory.add(
        experiment_id="ma-001",
        name="ma_cross_baseline",
        metrics={"total_return": 0.1, "sharpe": 0.8, "max_drawdown": -0.05},
        artifacts={"summary": path.parent / "ma.md"},
        params={"symbols": ["AAA"]},
    )
    memory.add(
        experiment_id="lgbm-001",
        name="lightgbm_direction",
        metrics={"test_auc": 0.55, "test_accuracy": 0.52},
        artifacts={"model": path.parent / "model.pkl"},
    )
    memory.add(
        experiment_id="wf-001",
        name="walk_forward_oos",
        metrics={
            "oos": {
                "sharpe": 1.4,
                "total_return": 0.22,
                "max_drawdown": -0.08,
            }
        },
        artifacts={"summary": path.parent / "wf.md"},
    )
    return memory


def write_storage_config(tmp_path: Path) -> Path:
    path = tmp_path / "storage.yaml"
    path.write_text(
        "\n".join(
            [
                "project_root: .",
                "raw_data_dir: data/raw",
                "processed_data_dir: data/processed",
                "features_dir: data/features",
                "models_dir: models",
                "reports_dir: reports",
                "logs_dir: logs",
            ]
        ),
        encoding="utf-8",
    )
    return path


def test_baseline_registry_add_compare_and_get_best() -> None:
    registry = BaselineRegistry()
    registry.add_baseline(
        BaselineRun(
            run_id="a",
            name="ma_cross",
            family="ma_cross",
            metrics={"sharpe": 0.5, "oos": {"sharpe": 0.2}},
        )
    )
    registry.add_baseline(
        BaselineRun(
            run_id="b",
            name="walk_forward",
            family="walk_forward",
            metrics={"sharpe": 0.8, "oos": {"sharpe": 1.1}},
        )
    )

    table = registry.compare_runs(["sharpe", "oos.sharpe"])
    best = registry.get_best("oos.sharpe")

    assert list(table["run_id"]) == ["a", "b"]
    assert table.loc[1, "oos.sharpe"] == 1.1
    assert best.run_id == "b"


def test_collect_experiment_metrics_supports_nested_metric(tmp_path: Path) -> None:
    memory = seed_memory(tmp_path / "experiments.json")

    runs = collect_experiment_metrics(
        memory.list(),
        metric_paths=("sharpe", "test_auc", "oos.sharpe"),
    )
    table = build_comparison_table(
        runs,
        metric_paths=("sharpe", "test_auc", "oos.sharpe"),
    )

    assert set(table["family"]) == {"ma_cross", "lightgbm", "walk_forward"}
    assert table.loc[table["family"] == "walk_forward", "oos.sharpe"].iloc[0] == 1.4
    assert table.loc[table["family"] == "lightgbm", "test_auc"].iloc[0] == 0.55


def test_compare_experiments_writes_csv_and_markdown(tmp_path: Path) -> None:
    storage_config = write_storage_config(tmp_path)
    memory_path = tmp_path / "experiments.json"
    seed_memory(memory_path)
    output_dir = tmp_path / "research"

    result = compare_experiments(
        storage_config=storage_config,
        memory_path=memory_path,
        output_dir=output_dir,
        families=("ma_cross", "lightgbm", "walk_forward"),
        metrics=("sharpe", "test_auc", "oos.sharpe"),
    )

    csv_path = Path(result["csv"])
    markdown_path = Path(result["markdown"])
    assert csv_path.exists()
    assert markdown_path.exists()
    assert result["rows"] == 3
    assert "walk_forward_oos" in markdown_path.read_text(encoding="utf-8")
    rows = csv_path.read_text(encoding="utf-8").splitlines()
    assert "oos.sharpe" in rows[0]


def test_compare_experiments_handles_empty_memory(tmp_path: Path) -> None:
    storage_config = write_storage_config(tmp_path)
    memory_path = tmp_path / "experiments.json"
    memory_path.write_text(json.dumps([]), encoding="utf-8")

    result = compare_experiments(
        storage_config=storage_config,
        memory_path=memory_path,
        output_dir=tmp_path / "research",
    )

    assert result["rows"] == 0
    assert "No matching experiments" in Path(result["markdown"]).read_text(encoding="utf-8")
