"""Build feature tables from OHLCV parquet data."""

from __future__ import annotations

import argparse
from pathlib import Path

import yaml

from quant_mas.data import DataCatalog, ParquetStorage
from quant_mas.features import build_feature_table_from_config


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build feature tables.")
    parser.add_argument("--config", default="configs/features.yaml", help="Feature config path.")
    parser.add_argument(
        "--storage-config",
        default="configs/storage.yaml",
        help="Storage config path.",
    )
    parser.add_argument(
        "--input",
        help="Input OHLCV parquet path. Defaults to raw_data_dir/market_data.parquet.",
    )
    parser.add_argument(
        "--output",
        help="Output feature parquet path. Defaults to features_dir/features.parquet.",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    with Path(args.config).expanduser().open("r", encoding="utf-8") as file:
        feature_config = yaml.safe_load(file) or {}

    catalog = DataCatalog.from_yaml(args.storage_config)
    input_path = (
        Path(args.input).expanduser()
        if args.input
        else catalog.path_for("raw_data_dir", "market_data.parquet")
    )
    output_path = (
        Path(args.output).expanduser()
        if args.output
        else catalog.path_for("features_dir", "features.parquet")
    )

    storage = ParquetStorage()
    raw_data = storage.load(input_path)
    features = build_feature_table_from_config(raw_data, feature_config)
    saved_path = storage.save(features, output_path)

    print(f"Saved {len(features)} feature rows to {saved_path}")


if __name__ == "__main__":
    main()
