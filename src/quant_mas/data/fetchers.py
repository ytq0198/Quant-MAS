"""Market data fetchers."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence

import pandas as pd

from quant_mas.data.validation import OHLCV_COLUMNS, validate_ohlcv


class MarketDataFetcher(ABC):
    """Abstract interface for market data fetchers."""

    @abstractmethod
    def fetch(self, symbols: Sequence[str], start: str, end: str) -> pd.DataFrame:
        """Fetch OHLCV data for symbols between start and end dates."""


class YFinanceFetcher(MarketDataFetcher):
    """Fetch OHLCV data from yfinance.

    yfinance is imported lazily so tests and offline workflows do not require it.
    """

    def fetch(self, symbols: Sequence[str], start: str, end: str) -> pd.DataFrame:
        normalized_symbols = [symbol.upper() for symbol in symbols]
        if not normalized_symbols:
            raise ValueError("At least one symbol is required")

        try:
            import yfinance as yf
        except ImportError as exc:
            raise ImportError(
                "YFinanceFetcher requires yfinance. Install it with "
                "`pip install yfinance` or use the data extra when available."
            ) from exc

        downloaded = yf.download(
            tickers=normalized_symbols,
            start=start,
            end=end,
            auto_adjust=False,
            progress=False,
            group_by="ticker",
            threads=False,
        )
        if downloaded.empty:
            raise ValueError("No market data returned by yfinance")

        frames = [
            self._frame_for_symbol(downloaded, symbol) for symbol in normalized_symbols
        ]
        return validate_ohlcv(pd.concat(frames, ignore_index=True))

    @staticmethod
    def _frame_for_symbol(downloaded: pd.DataFrame, symbol: str) -> pd.DataFrame:
        if isinstance(downloaded.columns, pd.MultiIndex):
            data = downloaded[symbol].copy()
        else:
            data = downloaded.copy()

        data = data.reset_index()
        date_column = "Date" if "Date" in data.columns else data.columns[0]
        renamed = data.rename(
            columns={
                date_column: "date",
                "Open": "open",
                "High": "high",
                "Low": "low",
                "Close": "close",
                "Volume": "volume",
            }
        )
        renamed["symbol"] = symbol
        return renamed.loc[:, OHLCV_COLUMNS]

