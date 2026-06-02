"""Generate or locate experiment reports."""

from __future__ import annotations

import argparse
from pathlib import Path
from shutil import copyfile

from quant_mas.data import DataCatalog
from quant_mas.memory import ExperimentMemory


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate a report.")
    parser.add_argument(
        "--latest",
        action="store_true",
        help="Use the latest experiment from experiment memory.",
    )
    parser.add_argument(
        "--storage-config",
        default="configs/storage.yaml",
        help="Storage config path.",
    )
    parser.add_argument(
        "--memory-path",
        help="Experiment memory JSON path. Defaults to reports_dir/experiments.json.",
    )
    parser.add_argument(
        "--output",
        help="Optional path to copy the summary markdown to.",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    if not args.latest:
        parser.error("Only --latest is supported in this phase")

    catalog = DataCatalog.from_yaml(args.storage_config)
    memory_path = (
        Path(args.memory_path).expanduser()
        if args.memory_path
        else catalog.path_for("reports_dir", "experiments.json")
    )
    latest = ExperimentMemory(memory_path).latest()
    summary_path = Path(latest.artifacts.get("summary", "")).expanduser()
    if not summary_path.exists():
        raise FileNotFoundError(f"Latest experiment summary not found: {summary_path}")

    if args.output:
        output_path = Path(args.output).expanduser()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        copyfile(summary_path, output_path)
        print(f"Generated report: {output_path}")
    else:
        print(f"Latest report: {summary_path}")


if __name__ == "__main__":
    main()
