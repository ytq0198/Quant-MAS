"""Data layer package."""

from quant_mas.data.catalog import DataCatalog
from quant_mas.data.fetchers import (
    AutoMarketDataFetcher,
    MarketDataFetcher,
    StooqFetcher,
    YFinanceFetcher,
    create_market_data_fetcher,
    resolve_stooq_api_key,
)
from quant_mas.data.merge import merge_parquet_files
from quant_mas.data.storage import ParquetStorage
from quant_mas.data.validation import OHLCV_COLUMNS, validate_ohlcv

__all__ = [
    "AutoMarketDataFetcher",
    "DataCatalog",
    "MarketDataFetcher",
    "StooqFetcher",
    "YFinanceFetcher",
    "create_market_data_fetcher",
    "resolve_stooq_api_key",
    "merge_parquet_files",
    "OHLCV_COLUMNS",
    "ParquetStorage",
    "validate_ohlcv",
]
