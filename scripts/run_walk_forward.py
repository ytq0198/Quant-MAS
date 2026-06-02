"""Run walk-forward out-of-sample evaluation."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml

from quant_mas.backtest import run_walk_forward_from_config


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run walk-forward OOS evaluation.")
    parser.add_argument("--config", default="configs/walk_forward.yaml")
    parser.add_argument("--storage-config", default="configs/storage.yaml")
    parser.add_argument("--features-path", help="Override feature parquet path.")
    parser.add_argument("--output-dir", help="Override report output directory.")
    parser.add_argument("--experiment-name", help="Override experiment name.")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        with Path(args.config).expanduser().open("r", encoding="utf-8") as file:
            config = yaml.safe_load(file) or {}
        result = run_walk_forward_from_config(
            config=config,
            storage_config=Path(args.storage_config).expanduser(),
            features_path=Path(args.features_path).expanduser()
            if args.features_path
            else None,
            output_dir=Path(args.output_dir).expanduser() if args.output_dir else None,
            experiment_name=args.experiment_name,
        )
    except Exception as exc:
        print(f"[walk-forward] ERROR: {exc}", file=sys.stderr)
        return 1

    print("[walk-forward] Evaluation completed")
    print(json.dumps(result["metrics"], indent=2))
    print(f"[walk-forward] Summary: {result['artifacts']['summary']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
