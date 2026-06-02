"""Data source registry."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from quant_mas.data.fetchers.alpha_vantage_fetcher import AlphaVantageFetcher
from quant_mas.data.fetchers.auto_fetcher import AutoMarketDataFetcher
from quant_mas.data.fetchers.finnhub_fetcher import FinnhubFetcher
from quant_mas.data.fetchers.fred_fetcher import FREDFetcher
from quant_mas.data.fetchers.sec_edgar_fetcher import SECEDGARFetcher
from quant_mas.data.fetchers.stooq_fetcher import StooqFetcher
from quant_mas.data.fetchers.yfinance_fetcher import YFinanceFetcher


@dataclass(frozen=True)
class DataSourceSpec:
    name: str
    kind: str
    factory: Callable[..., object]


class DataSourceRegistry:
    """Registry of OHLCV and non-OHLCV data source factories."""

    def __init__(self) -> None:
        self._sources: dict[str, DataSourceSpec] = {}

    def register(self, name: str, kind: str, factory: Callable[..., object]) -> None:
        normalized = name.lower().strip()
        self._sources[normalized] = DataSourceSpec(normalized, kind, factory)

    def create_fetcher(self, source: str, **kwargs) -> object:
        normalized = source.lower().strip()
        if normalized not in self._sources:
            raise ValueError(
                f"Unknown data source: {source}. Available sources: {', '.join(self.names())}"
            )
        return self._sources[normalized].factory(**kwargs)

    def get(self, source: str) -> DataSourceSpec:
        normalized = source.lower().strip()
        if normalized not in self._sources:
            raise ValueError(
                f"Unknown data source: {source}. Available sources: {', '.join(self.names())}"
            )
        return self._sources[normalized]

    def names(self) -> list[str]:
        return sorted(self._sources)


def default_data_source_registry() -> DataSourceRegistry:
    registry = DataSourceRegistry()
    registry.register("yfinance", "ohlcv", YFinanceFetcher)
    registry.register("stooq", "ohlcv", StooqFetcher)
    registry.register("auto", "ohlcv", AutoMarketDataFetcher)
    registry.register("alpha_vantage", "ohlcv", AlphaVantageFetcher)
    registry.register("finnhub", "ohlcv", FinnhubFetcher)
    registry.register("fred", "macro", FREDFetcher)
    registry.register("sec_edgar", "filings", SECEDGARFetcher)
    return registry
