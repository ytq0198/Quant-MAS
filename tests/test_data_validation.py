from __future__ import annotations

import pandas as pd
import pytest

from quant_mas.data import OHLCV_COLUMNS, MarketDataFetcher, validate_ohlcv


class SyntheticFetcher(MarketDataFetcher):
    def fetch(self, symbols, start: str, end: str) -> pd.DataFrame:
        dates = pd.date_range(start=start, end=end, freq="D")
        rows = []
        for symbol in symbols:
            for index, date in enumerate(dates):
                close = 10.0 + index
                rows.append(
                    {
                        "date": date,
                        "symbol": symbol,
                        "open": close - 0.2,
                        "high": close + 0.5,
                        "low": close - 0.5,
                        "close": close,
                        "volume": 1000 + index,
                    }
                )
        return pd.DataFrame(rows)


def test_synthetic_fetcher_returns_valid_ohlcv() -> None:
    fetcher = SyntheticFetcher()

    result = validate_ohlcv(fetcher.fetch(["aaa", "bbb"], "2026-01-01", "2026-01-02"))

    assert list(result.columns) == OHLCV_COLUMNS
    assert result["symbol"].tolist() == ["AAA", "AAA", "BBB", "BBB"]
    assert pd.api.types.is_datetime64_any_dtype(result["date"])


def test_validate_ohlcv_rejects_missing_column() -> None:
    frame = pd.DataFrame(
        {
            "date": ["2026-01-01"],
            "symbol": ["TEST"],
            "open": [10.0],
            "high": [11.0],
            "low": [9.0],
            "close": [10.5],
        }
    )

    with pytest.raises(ValueError, match="Missing OHLCV columns"):
        validate_ohlcv(frame)


def test_validate_ohlcv_rejects_duplicate_symbol_date() -> None:
    frame = pd.DataFrame(
        {
            "date": ["2026-01-01", "2026-01-01"],
            "symbol": ["TEST", "TEST"],
            "open": [10.0, 10.0],
            "high": [11.0, 11.0],
            "low": [9.0, 9.0],
            "close": [10.5, 10.5],
            "volume": [1000, 1000],
        }
    )

    with pytest.raises(ValueError, match="duplicate"):
        validate_ohlcv(frame)


def test_validate_ohlcv_rejects_invalid_price_relationship() -> None:
    frame = pd.DataFrame(
        {
            "date": ["2026-01-01"],
            "symbol": ["TEST"],
            "open": [10.0],
            "high": [9.0],
            "low": [8.0],
            "close": [10.5],
            "volume": [1000],
        }
    )

    with pytest.raises(ValueError, match="high"):
        validate_ohlcv(frame)


def test_validate_ohlcv_rejects_negative_volume() -> None:
    frame = pd.DataFrame(
        {
            "date": ["2026-01-01"],
            "symbol": ["TEST"],
            "open": [10.0],
            "high": [11.0],
            "low": [9.0],
            "close": [10.5],
            "volume": [-1],
        }
    )

    with pytest.raises(ValueError, match="volume"):
        validate_ohlcv(frame)

