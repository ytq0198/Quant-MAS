"""Align timestamped real-news records to feature bars."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

from quant_mas.text import (
    align_real_news_to_features,
    load_real_news_records,
    write_real_news_alignment_report,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Align real financial-news JSONL/parquet records to feature dates."
    )
    parser.add_argument("--news-path", required=True, help="Input real-news JSONL/parquet.")
    parser.add_argument("--features-path", required=True, help="Feature parquet path.")
    parser.add_argument(
        "--output-dir",
        required=True,
        help="Output directory for aligned_news.jsonl and audit files.",
    )
    parser.add_argument(
        "--market-close",
        default="16:00",
        help="Market close time. News after this time maps to the next feature bar.",
    )
    parser.add_argument("--date-col", default="date", help="Feature date column.")
    parser.add_argument("--symbol-col", default="symbol", help="Feature symbol column.")
    args = parser.parse_args()

    try:
        records = load_real_news_records(args.news_path)
        features = pd.read_parquet(Path(args.features_path).expanduser())
        aligned, audit = align_real_news_to_features(
            records,
            features,
            market_close=args.market_close,
            date_col=args.date_col,
            symbol_col=args.symbol_col,
        )
        artifacts = write_real_news_alignment_report(aligned, audit, args.output_dir)
    except Exception as exc:  # noqa: BLE001 - CLI should report clean failures.
        print(f"[align-real-news] ERROR: {exc}", file=sys.stderr)
        return 1

    payload = {**audit, "artifacts": artifacts}
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
