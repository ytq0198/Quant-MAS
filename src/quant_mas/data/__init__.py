"""Data layer package."""

from quant_mas.data.catalog import DataCatalog
from quant_mas.data.fetchers import (
    AlphaVantageFetcher,
    AutoMarketDataFetcher,
    DataSourceRegistry,
    FinnhubFetcher,
    FREDFetcher,
    MarketDataFetcher,
    SECEDGARFetcher,
    StooqFetcher,
    YFinanceFetcher,
    create_market_data_fetcher,
    default_data_source_registry,
    resolve_alpha_vantage_api_key,
    resolve_finnhub_api_key,
    resolve_fred_api_key,
    resolve_sec_edgar_user_agent,
    resolve_stooq_api_key,
)
from quant_mas.data.merge import merge_parquet_files
from quant_mas.data.storage import ParquetStorage
from quant_mas.data.validation import OHLCV_COLUMNS, validate_ohlcv

__all__ = [
    "AutoMarketDataFetcher",
    "AlphaVantageFetcher",
    "DataSourceRegistry",
    "DataCatalog",
    "FinnhubFetcher",
    "FREDFetcher",
    "MarketDataFetcher",
    "SECEDGARFetcher",
    "StooqFetcher",
    "YFinanceFetcher",
    "create_market_data_fetcher",
    "default_data_source_registry",
    "resolve_alpha_vantage_api_key",
    "resolve_finnhub_api_key",
    "resolve_fred_api_key",
    "resolve_sec_edgar_user_agent",
    "resolve_stooq_api_key",
    "merge_parquet_files",
    "OHLCV_COLUMNS",
    "ParquetStorage",
    "validate_ohlcv",
]
