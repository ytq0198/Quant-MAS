"""YFinance OHLCV fetcher."""

from __future__ import annotations

import random
import time
from collections.abc import Sequence

import pandas as pd

from quant_mas.data.fetchers.base import MarketDataFetcher, normalize_symbols
from quant_mas.data.validation import OHLCV_COLUMNS, validate_ohlcv


def _is_rate_limit_error(error: Exception | None) -> bool:
    if error is None:
        return False
    message = str(error).lower()
    return any(
        token in message
        for token in (
            "rate limit",
            "too many requests",
            "yfratelimiterror",
            "429",
            "connection closed abruptly",
            "curl: (56)",
        )
    )


class YFinanceFetcher(MarketDataFetcher):
    """Fetch OHLCV data from yfinance with retries and backoff."""

    def __init__(
        self,
        *,
        max_retries: int = 8,
        retry_backoff_seconds: float = 20.0,
        rate_limit_backoff_seconds: float = 120.0,
        max_rate_limit_wait_seconds: float = 900.0,
        delay_between_symbols_seconds: float = 5.0,
        jitter_min_seconds: float = 0.0,
        jitter_max_seconds: float = 0.0,
    ) -> None:
        self.max_retries = max_retries
        self.retry_backoff_seconds = retry_backoff_seconds
        self.rate_limit_backoff_seconds = rate_limit_backoff_seconds
        self.max_rate_limit_wait_seconds = max_rate_limit_wait_seconds
        self.delay_between_symbols_seconds = delay_between_symbols_seconds
        self.jitter_min_seconds = jitter_min_seconds
        self.jitter_max_seconds = jitter_max_seconds

    def fetch(self, symbols: Sequence[str], start: str, end: str) -> pd.DataFrame:
        normalized_symbols = normalize_symbols(symbols)
        try:
            import yfinance as yf
        except ImportError as exc:
            raise ImportError(
                "YFinanceFetcher requires yfinance. Install it with "
                "`python -m pip install -r requirements-data.txt`."
            ) from exc

        frames: list[pd.DataFrame] = []
        failures: list[str] = []
        for index, symbol in enumerate(normalized_symbols):
            if index > 0 and self.delay_between_symbols_seconds > 0:
                time.sleep(self.delay_between_symbols_seconds)
            try:
                frames.append(self._download_symbol(yf, symbol, start, end))
                print(f"[download] OK {symbol} {start} -> {end} (yfinance)")
                self._sleep_jitter()
            except Exception as exc:
                failures.append(f"{symbol}: {exc}")
                print(f"[download] FAIL {symbol}: {exc}")

        if not frames:
            detail = "; ".join(failures) if failures else "no symbols succeeded"
            raise ValueError(f"No market data returned by yfinance. {detail}.")
        if failures:
            print(f"[download] warning: skipped failed symbols: {', '.join(failures)}")
        return validate_ohlcv(pd.concat(frames, ignore_index=True))

    def _sleep_jitter(self) -> None:
        if self.jitter_max_seconds <= 0:
            return
        wait = random.uniform(max(0.0, self.jitter_min_seconds), self.jitter_max_seconds)
        if wait > 0:
            print(f"[download] jitter sleep {wait:.0f}s")
            time.sleep(wait)

    def _retry_wait_seconds(self, attempt: int, error: Exception | None) -> float:
        if _is_rate_limit_error(error):
            wait = self.rate_limit_backoff_seconds * (2 ** (attempt - 1))
            return min(wait, self.max_rate_limit_wait_seconds)
        return self.retry_backoff_seconds * attempt

    def _download_symbol(self, yf_module, symbol: str, start: str, end: str) -> pd.DataFrame:
        last_error: Exception | None = None
        for attempt in range(1, self.max_retries + 1):
            for fetch_method in (self._fetch_via_history, self._fetch_via_download):
                try:
                    downloaded = fetch_method(yf_module, symbol, start, end)
                    if downloaded is not None and not downloaded.empty:
                        return self._frame_for_symbol(downloaded, symbol)
                except Exception as exc:
                    last_error = exc
            last_error = last_error or ValueError("empty response")
            if attempt < self.max_retries:
                wait = self._retry_wait_seconds(attempt, last_error)
                reason = "rate limit" if _is_rate_limit_error(last_error) else "retry"
                print(f"[download] {reason} {symbol} in {wait:.0f}s")
                time.sleep(wait)
        raise RuntimeError(
            f"Failed to download {symbol} after {self.max_retries} attempts: {last_error}"
        )

    @staticmethod
    def _fetch_via_history(yf_module, symbol: str, start: str, end: str) -> pd.DataFrame:
        history = yf_module.Ticker(symbol).history(start=start, end=end, auto_adjust=False)
        if history is None or history.empty:
            raise ValueError("empty history response")
        return history

    @staticmethod
    def _fetch_via_download(yf_module, symbol: str, start: str, end: str) -> pd.DataFrame:
        downloaded = yf_module.download(
            tickers=symbol,
            start=start,
            end=end,
            auto_adjust=False,
            progress=False,
            threads=False,
        )
        if downloaded is None or downloaded.empty:
            raise ValueError("empty download response")
        return downloaded

    @staticmethod
    def _frame_for_symbol(downloaded: pd.DataFrame, symbol: str) -> pd.DataFrame:
        data = downloaded[symbol].copy() if isinstance(downloaded.columns, pd.MultiIndex) else downloaded.copy()
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
