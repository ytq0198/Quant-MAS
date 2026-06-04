"""Download real financial news JSONL for text-signal experiments."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from quant_mas.text.finnhub_news import (
    fetch_finnhub_company_news_records,
    write_real_news_jsonl,
)
from quant_mas.utils.env import load_repo_dotenv


def main() -> int:
    load_repo_dotenv()
    parser = argparse.ArgumentParser(
        description="Fetch real company news JSONL (Finnhub) for EXP-TEXT-WF-003."
    )
    parser.add_argument(
        "--source",
        choices=["finnhub"],
        default="finnhub",
        help="News provider. Currently only finnhub is supported.",
    )
    parser.add_argument(
        "--symbols",
        nargs="+",
        default=["AAPL", "MSFT", "SPY"],
        help="Ticker symbols to download.",
    )
    parser.add_argument("--start", default="2018-01-01", help="Start date YYYY-MM-DD.")
    parser.add_argument("--end", default="2025-12-31", help="End date YYYY-MM-DD.")
    parser.add_argument("--output-path", required=True, help="Output JSONL path.")
    parser.add_argument("--api-key", help="Finnhub API key override.")
    parser.add_argument(
        "--chunk-months",
        type=int,
        default=1,
        help="Split each symbol download into N-month windows.",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=1.0,
        help="Seconds to wait between Finnhub requests.",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress per-request progress logs on stderr.",
    )
    args = parser.parse_args()

    try:
        if args.source != "finnhub":
            raise ValueError(f"Unsupported source: {args.source}")
        records = fetch_finnhub_company_news_records(
            args.symbols,
            start=args.start,
            end=args.end,
            api_key=args.api_key,
            chunk_months=args.chunk_months,
            delay_seconds=args.delay,
            progress=not args.quiet,
        )
        output_path = write_real_news_jsonl(records, args.output_path)
    except Exception as exc:  # noqa: BLE001 - CLI should print clean failures.
        print(f"[fetch-real-news] ERROR: {exc}", file=sys.stderr)
        return 1

    summary = {
        "source": args.source,
        "symbols": [symbol.upper() for symbol in args.symbols],
        "start": args.start,
        "end": args.end,
        "record_count": len(records),
        "output_path": str(output_path),
        "symbol_counts": _count_by_symbol(records),
    }
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


def _count_by_symbol(records) -> dict[str, int]:
    counts: dict[str, int] = {}
    for record in records:
        counts[record.symbol] = counts.get(record.symbol, 0) + 1
    return dict(sorted(counts.items()))


if __name__ == "__main__":
    raise SystemExit(main())
