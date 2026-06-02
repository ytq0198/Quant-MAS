"""Run the end-to-end Quant MAS pipeline."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from quant_mas.pipeline import run_quant_pipeline


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run Quant MAS end-to-end pipeline.")
    parser.add_argument("--symbols", nargs="*", default=[], help="Symbols to download.")
    parser.add_argument("--start", default="2018-01-01", help="Start date, YYYY-MM-DD.")
    parser.add_argument("--end", default="2025-12-31", help="End date, YYYY-MM-DD.")
    parser.add_argument("--raw-dir", help="Directory containing/saving market_data.parquet.")
    parser.add_argument("--features-dir", help="Directory containing/saving features.parquet.")
    parser.add_argument("--output-dir", help="Directory for report artifacts.")
    parser.add_argument(
        "--storage-config",
        default="configs/storage.yaml",
        help="Storage YAML config path.",
    )
    parser.add_argument(
        "--features-config",
        default="configs/features.yaml",
        help="Features YAML config path.",
    )
    parser.add_argument(
        "--backtest-config",
        default="configs/backtest.yaml",
        help="Backtest YAML config path.",
    )
    parser.add_argument(
        "--skip-download",
        action="store_true",
        help="Use local raw parquet instead of downloading.",
    )
    parser.add_argument(
        "--skip-features",
        action="store_true",
        help="Use local feature parquet instead of rebuilding features.",
    )
    parser.add_argument(
        "--strategy",
        default="ma_cross",
        choices=["ma_cross"],
        help="Strategy to backtest.",
    )
    parser.add_argument(
        "--experiment-name",
        default="pipeline_ma_cross",
        help="Experiment name for report and memory.",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        result = run_quant_pipeline(
            symbols=args.symbols,
            start=args.start,
            end=args.end,
            raw_dir=Path(args.raw_dir).expanduser() if args.raw_dir else None,
            features_dir=Path(args.features_dir).expanduser() if args.features_dir else None,
            output_dir=Path(args.output_dir).expanduser() if args.output_dir else None,
            storage_config=Path(args.storage_config).expanduser(),
            features_config=Path(args.features_config).expanduser(),
            backtest_config=Path(args.backtest_config).expanduser(),
            skip_download=args.skip_download,
            skip_features=args.skip_features,
            strategy_name=args.strategy,
            experiment_name=args.experiment_name,
        )
    except Exception as exc:
        print(f"[pipeline] ERROR: {exc}", file=sys.stderr)
        return 1

    print("[pipeline] Experiment summary")
    print(
        json.dumps(
            {
                "experiment_name": args.experiment_name,
                "metrics": result.metrics,
                "artifacts": {key: str(value) for key, value in result.artifacts.items()},
                "experiment_memory": str(result.experiment_memory_path),
            },
            indent=2,
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

