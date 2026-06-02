"""Download market data to parquet."""

from __future__ import annotations

import argparse
from pathlib import Path

from quant_mas.data import DataCatalog, ParquetStorage, YFinanceFetcher, validate_ohlcv


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
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    output_dir = (
        Path(args.output_dir).expanduser()
        if args.output_dir
        else DataCatalog.from_yaml(args.storage_config).raw_data_dir
    )
    output_path = output_dir / args.filename

    fetcher = YFinanceFetcher()
    data = fetcher.fetch(args.symbols, args.start, args.end)
    validated = validate_ohlcv(data)
    saved_path = ParquetStorage().save(validated, output_path)

    print(f"Saved {len(validated)} rows to {saved_path}")


if __name__ == "__main__":
    main()
