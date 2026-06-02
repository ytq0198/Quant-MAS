"""Merge multiple OHLCV parquet files into one."""

from __future__ import annotations

import argparse
from pathlib import Path

from quant_mas.data.merge import merge_parquet_files
from quant_mas.data.storage import ParquetStorage


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Merge OHLCV parquet files.")
    parser.add_argument(
        "--input-dir",
        type=Path,
        required=True,
        help="Directory containing source parquet files.",
    )
    parser.add_argument(
        "--pattern",
        default="*.parquet",
        help="Glob pattern for input files (default: *.parquet).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Output parquet path.",
    )
    parser.add_argument(
        "--exclude",
        nargs="*",
        default=[],
        help="Basenames to exclude, e.g. market_data.parquet.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    saved = merge_parquet_files(
        args.input_dir.expanduser(),
        args.output.expanduser(),
        pattern=args.pattern,
        exclude=set(args.exclude),
    )
    rows = len(ParquetStorage().load(saved))
    print(f"Merged into {saved} ({rows} rows)")


if __name__ == "__main__":
    main()
