"""Merge OHLCV parquet files."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from quant_mas.data.storage import ParquetStorage
from quant_mas.data.validation import validate_ohlcv


def merge_parquet_files(
    input_dir: Path,
    output: Path,
    *,
    pattern: str = "*.parquet",
    exclude: set[str] | None = None,
) -> Path:
    exclude = exclude or set()
    paths = sorted(
        path
        for path in input_dir.glob(pattern)
        if path.is_file() and path.name not in exclude and path.resolve() != output.resolve()
    )
    if not paths:
        raise FileNotFoundError(f"No parquet files matched in {input_dir} ({pattern})")

    storage = ParquetStorage()
    frames = [storage.load(path) for path in paths]
    merged = validate_ohlcv(pd.concat(frames, ignore_index=True))
    merged = merged.sort_values(["symbol", "date"]).reset_index(drop=True)
    return storage.save(merged, output)
