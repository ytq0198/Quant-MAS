"""Feature engineering package."""

from quant_mas.features.labels import add_future_return_label
from quant_mas.features.pipelines import (
    build_feature_table,
    build_feature_table_from_config,
)
from quant_mas.features.text_signals import (
    assert_no_future_text_leakage,
    merge_text_signals_into_features,
)
from quant_mas.features.technical import (
    add_ma_distance,
    add_moving_averages,
    add_returns,
    add_rsi,
    add_volatility,
    add_volume_features,
)

__all__ = [
    "add_future_return_label",
    "add_ma_distance",
    "add_moving_averages",
    "add_returns",
    "add_rsi",
    "add_volatility",
    "add_volume_features",
    "build_feature_table",
    "build_feature_table_from_config",
    "assert_no_future_text_leakage",
    "merge_text_signals_into_features",
]
