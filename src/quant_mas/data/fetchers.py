"""Market data fetchers."""

from __future__ import annotations

import io
import os
import random
import time
import urllib.error
import urllib.request
from abc import ABC, abstractmethod
from collections.abc import Sequence
from datetime import datetime

import pandas as pd

from quant_mas.data.validation import OHLCV_COLUMNS, validate_ohlcv

STOOQ_SYMBOL_SUFFIX = ".us"
STOOQ_USER_AGENT = "Mozilla/5.0 (compatible; QuantMAS/1.0)"
STOOQ_API_KEY_URL = "https://stooq.com/q/d/?s=aapl.us&get_apikey"


def resolve_stooq_api_key(explicit: str | None = None) -> str:
    """Return Stooq API key from CLI arg or ``STOOQ_API_KEY`` env var."""

    if explicit and explicit.strip():
        return explicit.strip()

    env_key = os.environ.get("STOOQ_API_KEY", "").strip()
    if env_key:
        return env_key

    raise ValueError(
        "Stooq requires an API key. Set STOOQ_API_KEY in .env or pass --stooq-api-key. "
        f"Get one at {STOOQ_API_KEY_URL}"
    )


class MarketDataFetcher(ABC):
    """Abstract interface for market data fetchers."""

    @abstractmethod
    def fetch(self, symbols: Sequence[str], start: str, end: str) -> pd.DataFrame:
        """Fetch OHLCV data for symbols between start and end dates."""


def _normalize_symbols(symbols: Sequence[str]) -> list[str]:
    normalized = [symbol.upper() for symbol in symbols]
    if not normalized:
        raise ValueError("At least one symbol is required")
    return normalized


def _to_yyyymmdd(date_text: str) -> str:
    return datetime.strptime(date_text, "%Y-%m-%d").strftime("%Y%m%d")


def _is_rate_limit_error(error: Exception | None) -> bool:
    if error is None:
        return False
    message = str(error).lower()
    rate_limit_tokens = (
        "rate limit",
        "too many requests",
        "yfratelimiterror",
        "429",
        "connection closed abruptly",
        "curl: (56)",
    )
    return any(token in message for token in rate_limit_tokens)


class YFinanceFetcher(MarketDataFetcher):
    """Fetch OHLCV data from yfinance.

    Downloads one symbol at a time with retries, jitter, and exponential backoff
    when rate-limited.
    """

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
        normalized_symbols = _normalize_symbols(symbols)

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
            hint = (
                "yfinance rate limit or network error. Wait 30–60 min, use "
                "`--source stooq` or `SOURCE=stooq bash server/download_data_resilient.sh`, "
                "or place manual CSV in datasets/raw/manual/."
            )
            detail = "; ".join(failures) if failures else "no symbols succeeded"
            raise ValueError(f"No market data returned by yfinance. {detail}. {hint}")

        if failures:
            print(f"[download] warning: skipped failed symbols: {', '.join(failures)}")

        return validate_ohlcv(pd.concat(frames, ignore_index=True))

    def _sleep_jitter(self) -> None:
        if self.jitter_max_seconds <= 0:
            return
        low = max(0.0, self.jitter_min_seconds)
        high = max(low, self.jitter_max_seconds)
        wait = random.uniform(low, high)
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
        fetch_methods = (
            self._fetch_via_history,
            self._fetch_via_download,
        )

        for attempt in range(1, self.max_retries + 1):
            for fetch_method in fetch_methods:
                try:
                    downloaded = fetch_method(yf_module, symbol, start, end)
                    if downloaded is not None and not downloaded.empty:
                        return self._frame_for_symbol(downloaded, symbol)
                except Exception as exc:
                    last_error = exc

            last_error = last_error or ValueError(
                f"empty response (attempt {attempt}/{self.max_retries})"
            )

            if attempt < self.max_retries:
                wait = self._retry_wait_seconds(attempt, last_error)
                reason = "rate limit" if _is_rate_limit_error(last_error) else "retry"
                print(
                    f"[download] {reason} {symbol} in {wait:.0f}s "
                    f"(attempt {attempt}/{self.max_retries})"
                )
                time.sleep(wait)

        raise RuntimeError(
            f"Failed to download {symbol} after {self.max_retries} attempts: {last_error}"
        )

    @staticmethod
    def _fetch_via_history(yf_module, symbol: str, start: str, end: str) -> pd.DataFrame:
        ticker = yf_module.Ticker(symbol)
        history = ticker.history(start=start, end=end, auto_adjust=False)
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


def _parse_stooq_csv_payload(payload: bytes, symbol: str) -> pd.DataFrame:
    if not payload.strip():
        raise ValueError(f"empty Stooq response for {symbol}")

    preview = payload[:400].decode("utf-8", errors="replace")
    lowered = preview.lower()
    if "get your apikey" in lowered or (
        "apikey" in lowered and not preview.lstrip().startswith("Date,")
    ):
        raise ValueError(
            "Stooq returned API-key instructions instead of CSV. "
            f"Set STOOQ_API_KEY (see {STOOQ_API_KEY_URL})."
        )

    if not preview.lstrip().startswith("Date,"):
        raise ValueError(f"unexpected Stooq response for {symbol}: {preview[:120]!r}")

    frame = pd.read_csv(io.BytesIO(payload))
    if frame.empty:
        raise ValueError(f"empty Stooq CSV for {symbol}")

    renamed = frame.rename(
        columns={
            "Date": "date",
            "Open": "open",
            "High": "high",
            "Low": "low",
            "Close": "close",
            "Volume": "volume",
        }
    )
    renamed["symbol"] = symbol
    renamed["date"] = pd.to_datetime(renamed["date"])
    return renamed.loc[:, OHLCV_COLUMNS]


class StooqFetcher(MarketDataFetcher):
    """Fetch daily OHLCV from Stooq CSV export (requires ``STOOQ_API_KEY``).

    US symbols use the ``.us`` suffix, e.g. AAPL -> ``aapl.us``.
    """

    def __init__(
        self,
        *,
        api_key: str | None = None,
        delay_between_symbols_seconds: float = 3.0,
        request_timeout_seconds: float = 60.0,
    ) -> None:
        self.api_key = resolve_stooq_api_key(api_key)
        self.delay_between_symbols_seconds = delay_between_symbols_seconds
        self.request_timeout_seconds = request_timeout_seconds

    def fetch(self, symbols: Sequence[str], start: str, end: str) -> pd.DataFrame:
        normalized_symbols = _normalize_symbols(symbols)
        frames: list[pd.DataFrame] = []
        failures: list[str] = []

        d1 = _to_yyyymmdd(start)
        d2 = _to_yyyymmdd(end)

        for index, symbol in enumerate(normalized_symbols):
            if index > 0 and self.delay_between_symbols_seconds > 0:
                time.sleep(self.delay_between_symbols_seconds)

            try:
                frames.append(self._download_symbol(symbol, d1, d2))
                print(f"[download] OK {symbol} {start} -> {end} (stooq)")
            except Exception as exc:
                failures.append(f"{symbol}: {exc}")
                print(f"[download] FAIL {symbol}: {exc}")

        if not frames:
            detail = "; ".join(failures) if failures else "no symbols succeeded"
            raise ValueError(f"No market data returned by Stooq. {detail}")

        if failures:
            print(f"[download] warning: skipped failed symbols: {', '.join(failures)}")

        return validate_ohlcv(pd.concat(frames, ignore_index=True))

    @staticmethod
    def _stooq_ticker(symbol: str) -> str:
        return f"{symbol.lower()}{STOOQ_SYMBOL_SUFFIX}"

    def _download_symbol(self, symbol: str, d1: str, d2: str) -> pd.DataFrame:
        stooq_symbol = self._stooq_ticker(symbol)
        url = (
            f"https://stooq.com/q/d/l/?s={stooq_symbol}&d1={d1}&d2={d2}"
            f"&i=d&apikey={self.api_key}"
        )
        request = urllib.request.Request(url, headers={"User-Agent": STOOQ_USER_AGENT})

        try:
            with urllib.request.urlopen(
                request, timeout=self.request_timeout_seconds
            ) as response:
                payload = response.read()
        except urllib.error.URLError as exc:
            raise RuntimeError(f"Stooq request failed for {symbol}: {exc}") from exc

        return _parse_stooq_csv_payload(payload, symbol)


def create_market_data_fetcher(
    source: str,
    *,
    max_retries: int = 8,
    retry_backoff_seconds: float = 20.0,
    rate_limit_backoff_seconds: float = 120.0,
    delay_between_symbols_seconds: float = 5.0,
    jitter_min_seconds: float = 0.0,
    jitter_max_seconds: float = 0.0,
    stooq_api_key: str | None = None,
) -> MarketDataFetcher:
    """Build a fetcher from CLI source name."""

    normalized = source.lower().strip()
    if normalized == "yfinance":
        return YFinanceFetcher(
            max_retries=max_retries,
            retry_backoff_seconds=retry_backoff_seconds,
            rate_limit_backoff_seconds=rate_limit_backoff_seconds,
            delay_between_symbols_seconds=delay_between_symbols_seconds,
            jitter_min_seconds=jitter_min_seconds,
            jitter_max_seconds=jitter_max_seconds,
        )
    if normalized == "stooq":
        return StooqFetcher(
            api_key=stooq_api_key,
            delay_between_symbols_seconds=delay_between_symbols_seconds,
        )
    if normalized == "auto":
        return AutoMarketDataFetcher(
            max_retries=max_retries,
            retry_backoff_seconds=retry_backoff_seconds,
            rate_limit_backoff_seconds=rate_limit_backoff_seconds,
            delay_between_symbols_seconds=delay_between_symbols_seconds,
            jitter_min_seconds=jitter_min_seconds,
            jitter_max_seconds=jitter_max_seconds,
            stooq_api_key=stooq_api_key,
        )
    raise ValueError(f"Unknown data source: {source}. Use yfinance, stooq, or auto.")


class AutoMarketDataFetcher(MarketDataFetcher):
    """Try yfinance once, then fall back to Stooq."""

    def __init__(
        self,
        *,
        max_retries: int = 8,
        retry_backoff_seconds: float = 20.0,
        rate_limit_backoff_seconds: float = 120.0,
        delay_between_symbols_seconds: float = 5.0,
        jitter_min_seconds: float = 0.0,
        jitter_max_seconds: float = 0.0,
        stooq_api_key: str | None = None,
    ) -> None:
        self.yfinance_fetcher = YFinanceFetcher(
            max_retries=max(1, min(max_retries, 2)),
            retry_backoff_seconds=retry_backoff_seconds,
            rate_limit_backoff_seconds=rate_limit_backoff_seconds,
            delay_between_symbols_seconds=delay_between_symbols_seconds,
            jitter_min_seconds=jitter_min_seconds,
            jitter_max_seconds=jitter_max_seconds,
        )
        self.stooq_fetcher = StooqFetcher(
            api_key=stooq_api_key,
            delay_between_symbols_seconds=delay_between_symbols_seconds,
        )

    def fetch(self, symbols: Sequence[str], start: str, end: str) -> pd.DataFrame:
        try:
            return self.yfinance_fetcher.fetch(symbols, start, end)
        except Exception as exc:
            print(f"[download] yfinance unavailable ({exc}); falling back to stooq")
            return self.stooq_fetcher.fetch(symbols, start, end)
