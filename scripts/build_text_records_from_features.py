"""Build feature-aligned text record JSONL for text signal experiments."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

from quant_mas.text.dataset import build_text_records_from_features, write_text_records_jsonl


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build one JSONL text record per feature row (symbol/date aligned)."
    )
    parser.add_argument("--features-path", required=True, help="Feature parquet path.")
    parser.add_argument("--output-path", required=True, help="Output JSONL path.")
    parser.add_argument("--date-col", default="date", help="Feature date column name.")
    parser.add_argument("--symbol-col", default="symbol", help="Feature symbol column name.")
    parser.add_argument(
        "--source",
        default="feature_aligned_smoke",
        help="Source label stored on each FinancialTextRecord.",
    )
    parser.add_argument(
        "--text-template",
        default="{symbol} market headline for {date}",
        help="Headline template with {symbol} and {date} placeholders.",
    )
    args = parser.parse_args()

    try:
        features = pd.read_parquet(Path(args.features_path).expanduser())
        records = build_text_records_from_features(
            features,
            date_col=args.date_col,
            symbol_col=args.symbol_col,
            source=args.source,
            text_template=args.text_template,
        )
        output_path = write_text_records_jsonl(records, args.output_path)
    except Exception as exc:  # noqa: BLE001 - CLI should print clean failures.
        print(f"[build-text-records] ERROR: {exc}", file=sys.stderr)
        return 1

    summary = {
        "features_path": str(Path(args.features_path).expanduser()),
        "output_path": str(output_path),
        "record_count": len(records),
        "symbol_count": len({record.symbol for record in records}),
        "source": args.source,
    }
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
