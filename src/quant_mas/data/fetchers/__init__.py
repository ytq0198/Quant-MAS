"""Data fetcher package with backward-compatible exports."""

from quant_mas.data.fetchers.alpha_vantage_fetcher import (
    AlphaVantageFetcher,
    resolve_alpha_vantage_api_key,
)
from quant_mas.data.fetchers.auto_fetcher import AutoMarketDataFetcher
from quant_mas.data.fetchers.base import MarketDataFetcher
from quant_mas.data.fetchers.finnhub_fetcher import FinnhubFetcher, resolve_finnhub_api_key
from quant_mas.data.fetchers.fred_fetcher import FREDFetcher, resolve_fred_api_key
from quant_mas.data.fetchers.registry import (
    DataSourceRegistry,
    default_data_source_registry,
)
from quant_mas.data.fetchers.sec_edgar_fetcher import (
    SECEDGARFetcher,
    resolve_sec_edgar_user_agent,
)
from quant_mas.data.fetchers.stooq_fetcher import (
    StooqFetcher,
    _parse_stooq_csv_payload,
    resolve_stooq_api_key,
)
from quant_mas.data.fetchers.yfinance_fetcher import YFinanceFetcher


def create_market_data_fetcher(source: str, **kwargs) -> MarketDataFetcher:
    """Build an OHLCV fetcher from source name."""
    registry = default_data_source_registry()
    fetcher = registry.create_fetcher(source, **_filter_kwargs_for_source(source, kwargs))
    if not isinstance(fetcher, MarketDataFetcher):
        raise ValueError(f"Data source is not OHLCV: {source}")
    return fetcher


def _filter_kwargs_for_source(source: str, kwargs: dict) -> dict:
    common = {
        "max_retries",
        "retry_backoff_seconds",
        "rate_limit_backoff_seconds",
        "delay_between_symbols_seconds",
        "jitter_min_seconds",
        "jitter_max_seconds",
        "stooq_api_key",
    }
    normalized = source.lower().strip()
    if normalized in {"yfinance", "auto"}:
        result = {key: value for key, value in kwargs.items() if key in common}
        if normalized == "yfinance":
            result.pop("stooq_api_key", None)
        return result
    if normalized == "stooq":
        return {
            "api_key": kwargs.get("stooq_api_key"),
            "delay_between_symbols_seconds": kwargs.get("delay_between_symbols_seconds", 3.0),
        }
    if normalized in {"alpha_vantage", "finnhub"}:
        return {"api_key": kwargs.get("api_key")}
    return kwargs


__all__ = [
    "AlphaVantageFetcher",
    "AutoMarketDataFetcher",
    "DataSourceRegistry",
    "FinnhubFetcher",
    "FREDFetcher",
    "MarketDataFetcher",
    "SECEDGARFetcher",
    "StooqFetcher",
    "YFinanceFetcher",
    "_parse_stooq_csv_payload",
    "create_market_data_fetcher",
    "default_data_source_registry",
    "resolve_alpha_vantage_api_key",
    "resolve_finnhub_api_key",
    "resolve_fred_api_key",
    "resolve_sec_edgar_user_agent",
    "resolve_stooq_api_key",
]
