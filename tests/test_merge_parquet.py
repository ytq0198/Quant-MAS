from __future__ import annotations

from pathlib import Path

import pandas as pd

from quant_mas.data import OHLCV_COLUMNS, ParquetStorage, merge_parquet_files


def test_merge_parquet_files_combines_and_sorts(tmp_path: Path) -> None:
    storage = ParquetStorage()
    for symbol in ("AAA", "BBB"):
        frame = pd.DataFrame(
            {
                "date": pd.to_datetime(["2026-01-02", "2026-01-01"]),
                "symbol": [symbol, symbol],
                "open": [10.0, 9.0],
                "high": [11.0, 10.0],
                "low": [9.0, 8.0],
                "close": [10.5, 9.5],
                "volume": [100, 200],
            }
        )
        storage.save(frame, tmp_path / f"{symbol}_2026.parquet")

    output = tmp_path / "market_data.parquet"
    merge_parquet_files(tmp_path, output, pattern="*_*.parquet")

    merged = storage.load(output)
    assert list(merged.columns) == OHLCV_COLUMNS
    assert set(merged["symbol"]) == {"AAA", "BBB"}
    assert merged.groupby("symbol")["date"].apply(lambda s: s.is_monotonic_increasing).all()
