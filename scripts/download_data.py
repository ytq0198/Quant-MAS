"""Download data from configured sources."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from quant_mas.data import (
    DataCatalog,
    ParquetStorage,
    create_market_data_fetcher,
    default_data_source_registry,
    validate_ohlcv,
)
from quant_mas.utils.env import load_repo_dotenv


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Download market, macro, or filing data.")
    parser.add_argument("--symbols", nargs="+", help="Ticker symbols for OHLCV sources.")
    parser.add_argument("--start", default="2018-01-01", help="Start date, YYYY-MM-DD.")
    parser.add_argument("--end", default="2025-12-31", help="End date, YYYY-MM-DD.")
    parser.add_argument(
        "--output-dir",
        help="Directory for downloaded parquet. Defaults to raw_data_dir.",
    )
    parser.add_argument(
        "--storage-config",
        default="configs/storage.yaml",
        help="Storage config path used when --output-dir is omitted.",
    )
    parser.add_argument(
        "--filename",
        default="market_data.parquet",
        help="Output parquet filename.",
    )
    parser.add_argument(
        "--skip-existing",
        action="store_true",
        help="Skip download if output file already exists.",
    )
    parser.add_argument(
        "--retries",
        type=int,
        default=8,
        help="Max retries per symbol when yfinance rate-limits or fails.",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=5.0,
        help="Seconds to wait between symbols.",
    )
    parser.add_argument(
        "--retry-backoff",
        type=float,
        default=20.0,
        help="Base seconds for non-rate-limit retries.",
    )
    parser.add_argument(
        "--rate-limit-backoff",
        type=float,
        default=120.0,
        help="Base seconds for rate-limit backoff (doubles each attempt, max 900s).",
    )
    parser.add_argument(
        "--source",
        choices=("yfinance", "stooq", "auto", "alpha_vantage", "finnhub", "fred", "sec_edgar"),
        default="auto",
        help="Data source.",
    )
    parser.add_argument(
        "--stooq-api-key",
        default=None,
        help="Stooq API key (overrides STOOQ_API_KEY env var).",
    )
    parser.add_argument("--api-key", help="API key override for Alpha Vantage, Finnhub, or FRED.")
    parser.add_argument("--user-agent", help="SEC EDGAR User-Agent override.")
    parser.add_argument("--series-id", help="FRED series id, e.g. DGS10.")
    parser.add_argument("--cik", help="SEC company CIK, e.g. 0000320193.")
    parser.add_argument(
        "--sec-kind",
        choices=("submissions", "company_facts"),
        default="submissions",
        help="SEC EDGAR JSON endpoint to download.",
    )
    parser.add_argument(
        "--jitter-min",
        type=float,
        default=0.0,
        help="Random extra sleep lower bound after each successful symbol fetch.",
    )
    parser.add_argument(
        "--jitter-max",
        type=float,
        default=0.0,
        help="Random extra sleep upper bound after each successful symbol fetch.",
    )
    return parser


def main() -> int:
    load_repo_dotenv(Path(__file__).resolve().parent.parent)
    parser = build_parser()
    args = parser.parse_args()
    try:
        _run(args)
    except Exception as exc:
        print(f"[download] ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


def _run(args: argparse.Namespace) -> None:
    catalog = DataCatalog.from_yaml(args.storage_config)
    output_dir = (
        Path(args.output_dir).expanduser()
        if args.output_dir
        else catalog.raw_data_dir
    )
    source = args.source.lower().strip()

    if source == "fred":
        _download_fred(args, output_dir)
        return
    if source == "sec_edgar":
        _download_sec(args, output_dir)
        return

    output_path = output_dir / args.filename
    if args.skip_existing and output_path.exists():
        print(f"[download] skip existing {output_path}")
        return
    if not args.symbols:
        raise ValueError("--symbols is required for OHLCV sources")
    fetcher = create_market_data_fetcher(
        source,
        max_retries=args.retries,
        retry_backoff_seconds=args.retry_backoff,
        rate_limit_backoff_seconds=args.rate_limit_backoff,
        delay_between_symbols_seconds=args.delay,
        jitter_min_seconds=args.jitter_min,
        jitter_max_seconds=args.jitter_max,
        stooq_api_key=args.stooq_api_key,
        api_key=args.api_key,
    )
    data = fetcher.fetch(args.symbols, args.start, args.end)
    validated = validate_ohlcv(data)
    saved_path = ParquetStorage().save(validated, output_path)

    print(f"Saved {len(validated)} rows to {saved_path}")


def _download_fred(args: argparse.Namespace, output_dir: Path) -> None:
    if not args.series_id:
        raise ValueError("--series-id is required when --source fred")
    fetcher = default_data_source_registry().create_fetcher("fred", api_key=args.api_key)
    data = fetcher.fetch_series(args.series_id, args.start, args.end)
    output_path = output_dir / "macro" / f"{args.series_id}.parquet"
    if args.skip_existing and output_path.exists():
        print(f"[download] skip existing {output_path}")
        return
    saved_path = ParquetStorage().save(data, output_path)
    print(f"Saved {len(data)} macro rows to {saved_path}")


def _download_sec(args: argparse.Namespace, output_dir: Path) -> None:
    if not args.cik:
        raise ValueError("--cik is required when --source sec_edgar")
    fetcher = default_data_source_registry().create_fetcher(
        "sec_edgar",
        user_agent=args.user_agent,
    )
    payload = (
        fetcher.fetch_submissions(args.cik)
        if args.sec_kind == "submissions"
        else fetcher.fetch_company_facts(args.cik)
    )
    normalized_cik = str(args.cik).strip().lstrip("0").zfill(10)
    output_path = output_dir / "sec" / f"{normalized_cik}_{args.sec_kind}.json"
    if args.skip_existing and output_path.exists():
        print(f"[download] skip existing {output_path}")
        return
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Saved SEC JSON to {output_path}")


if __name__ == "__main__":
    raise SystemExit(main())
