"""Market data fetchers."""

from __future__ import annotations

import time
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
    Downloads one symbol at a time with retries to reduce rate-limit failures.
    """

    def __init__(
        self,
        *,
        max_retries: int = 5,
        retry_backoff_seconds: float = 10.0,
        delay_between_symbols_seconds: float = 3.0,
    ) -> None:
        self.max_retries = max_retries
        self.retry_backoff_seconds = retry_backoff_seconds
        self.delay_between_symbols_seconds = delay_between_symbols_seconds

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

        frames: list[pd.DataFrame] = []
        failures: list[str] = []

        for index, symbol in enumerate(normalized_symbols):
            if index > 0 and self.delay_between_symbols_seconds > 0:
                time.sleep(self.delay_between_symbols_seconds)

            try:
                frames.append(self._download_symbol(yf, symbol, start, end))
                print(f"[download] OK {symbol}")
            except Exception as exc:
                failures.append(f"{symbol}: {exc}")
                print(f"[download] FAIL {symbol}: {exc}")

        if not frames:
            hint = (
                "yfinance returned no data. Common causes: rate limit (wait 15–30 min), "
                "network issues, or invalid symbols. Try fewer symbols, increase "
                "--delay / --retries, or download one symbol at a time."
            )
            detail = "; ".join(failures) if failures else "no symbols succeeded"
            raise ValueError(f"No market data returned by yfinance. {detail}. {hint}")

        if failures:
            print(f"[download] warning: skipped failed symbols: {', '.join(failures)}")

        return validate_ohlcv(pd.concat(frames, ignore_index=True))

    def _download_symbol(self, yf_module, symbol: str, start: str, end: str) -> pd.DataFrame:
        last_error: Exception | None = None

        for attempt in range(1, self.max_retries + 1):
            try:
                downloaded = yf_module.download(
                    tickers=symbol,
                    start=start,
                    end=end,
                    auto_adjust=False,
                    progress=False,
                    threads=False,
                )
                if downloaded is not None and not downloaded.empty:
                    return self._frame_for_symbol(downloaded, symbol)
                last_error = ValueError(
                    f"empty response (attempt {attempt}/{self.max_retries})"
                )
            except Exception as exc:
                last_error = exc

            if attempt < self.max_retries:
                wait = self.retry_backoff_seconds * attempt
                print(
                    f"[download] retry {symbol} in {wait:.0f}s "
                    f"(attempt {attempt}/{self.max_retries})"
                )
                time.sleep(wait)

        raise RuntimeError(
            f"Failed to download {symbol} after {self.max_retries} attempts: {last_error}"
        )

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
