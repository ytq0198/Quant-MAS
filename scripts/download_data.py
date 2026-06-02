"""Download market data to parquet."""

from __future__ import annotations

import argparse
from pathlib import Path

from quant_mas.data import DataCatalog, ParquetStorage, create_market_data_fetcher, validate_ohlcv
from quant_mas.utils.env import load_repo_dotenv


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Download market data.")
    parser.add_argument("--symbols", nargs="+", required=True, help="Ticker symbols.")
    parser.add_argument("--start", required=True, help="Start date, YYYY-MM-DD.")
    parser.add_argument("--end", required=True, help="End date, YYYY-MM-DD.")
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
        choices=("yfinance", "stooq", "auto"),
        default="auto",
        help="Data source: yfinance, stooq (needs STOOQ_API_KEY), or auto.",
    )
    parser.add_argument(
        "--stooq-api-key",
        default=None,
        help="Stooq API key (overrides STOOQ_API_KEY env var).",
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


def main() -> None:
    load_repo_dotenv(Path(__file__).resolve().parent.parent)

    parser = build_parser()
    args = parser.parse_args()

    output_dir = (
        Path(args.output_dir).expanduser()
        if args.output_dir
        else DataCatalog.from_yaml(args.storage_config).raw_data_dir
    )
    output_path = output_dir / args.filename

    if args.skip_existing and output_path.exists():
        print(f"[download] skip existing {output_path}")
        return

    fetcher = create_market_data_fetcher(
        args.source,
        max_retries=args.retries,
        retry_backoff_seconds=args.retry_backoff,
        rate_limit_backoff_seconds=args.rate_limit_backoff,
        delay_between_symbols_seconds=args.delay,
        jitter_min_seconds=args.jitter_min,
        jitter_max_seconds=args.jitter_max,
        stooq_api_key=args.stooq_api_key,
    )
    data = fetcher.fetch(args.symbols, args.start, args.end)
    validated = validate_ohlcv(data)
    saved_path = ParquetStorage().save(validated, output_path)

    print(f"Saved {len(validated)} rows to {saved_path}")


if __name__ == "__main__":
    main()
