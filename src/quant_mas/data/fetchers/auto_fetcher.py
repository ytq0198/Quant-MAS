"""Automatic OHLCV fetcher fallback."""

from __future__ import annotations

from collections.abc import Sequence

import pandas as pd

from quant_mas.data.fetchers.base import MarketDataFetcher
from quant_mas.data.fetchers.stooq_fetcher import StooqFetcher
from quant_mas.data.fetchers.yfinance_fetcher import YFinanceFetcher


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
