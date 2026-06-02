"""Compare recorded Quant MAS experiments."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from quant_mas.data import DataCatalog
from quant_mas.memory import ExperimentMemory
from quant_mas.research import build_comparison_table, collect_experiment_metrics


DEFAULT_FAMILIES = ("ma_cross", "lightgbm", "ml_backtest", "walk_forward")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Compare ExperimentMemory records.")
    parser.add_argument("--storage-config", default="configs/storage.yaml")
    parser.add_argument("--memory-path", help="ExperimentMemory JSON path.")
    parser.add_argument("--output-dir", default="outputs/research")
    parser.add_argument(
        "--families",
        nargs="*",
        default=list(DEFAULT_FAMILIES),
        help="Experiment families to include.",
    )
    parser.add_argument(
        "--metrics",
        nargs="*",
        default=[
            "total_return",
            "sharpe",
            "max_drawdown",
            "test_auc",
            "oos.sharpe",
            "oos.total_return",
        ],
        help="Metric paths to include, including dotted nested paths.",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        result = compare_experiments(
            storage_config=Path(args.storage_config).expanduser(),
            memory_path=Path(args.memory_path).expanduser() if args.memory_path else None,
            output_dir=Path(args.output_dir).expanduser(),
            families=tuple(args.families),
            metrics=tuple(args.metrics),
        )
    except Exception as exc:
        print(f"[compare] ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"[compare] CSV: {result['csv']}")
    print(f"[compare] Markdown: {result['markdown']}")
    print(f"[compare] Rows: {result['rows']}")
    return 0


def compare_experiments(
    *,
    storage_config: str | Path,
    memory_path: str | Path | None,
    output_dir: str | Path,
    families: tuple[str, ...] = DEFAULT_FAMILIES,
    metrics: tuple[str, ...] = (
        "total_return",
        "sharpe",
        "max_drawdown",
        "test_auc",
        "oos.sharpe",
        "oos.total_return",
    ),
) -> dict[str, str | int]:
    catalog = DataCatalog.from_yaml(storage_config)
    memory_file = (
        Path(memory_path).expanduser()
        if memory_path is not None
        else catalog.path_for("reports_dir", "experiments.json")
    )
    records = ExperimentMemory(memory_file).list()
    runs = collect_experiment_metrics(records, metric_paths=metrics)
    table = build_comparison_table(runs, metric_paths=metrics, families=families)
    target_dir = Path(output_dir).expanduser()
    target_dir.mkdir(parents=True, exist_ok=True)
    csv_path = target_dir / "comparison.csv"
    markdown_path = target_dir / "comparison.md"
    table.to_csv(csv_path, index=False)
    markdown_path.write_text(_to_markdown(table), encoding="utf-8")
    return {
        "csv": str(csv_path),
        "markdown": str(markdown_path),
        "rows": int(len(table)),
    }


def _to_markdown(table) -> str:
    lines = ["# Experiment Comparison", ""]
    if table.empty:
        lines.append("No matching experiments found.")
        return "\n".join(lines) + "\n"
    columns = list(table.columns)
    lines.append("| " + " | ".join(columns) + " |")
    lines.append("| " + " | ".join(["---"] * len(columns)) + " |")
    for row in table.fillna("").to_dict(orient="records"):
        lines.append("| " + " | ".join(str(row[column]) for column in columns) + " |")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
