from __future__ import annotations

import pandas as pd
import pytest

from quant_mas.features import build_feature_table


def make_ohlcv(symbol: str, closes: list[float]) -> pd.DataFrame:
    rows = []
    for index, close in enumerate(closes):
        rows.append(
            {
                "date": pd.Timestamp("2026-01-01") + pd.Timedelta(days=index),
                "symbol": symbol,
                "open": close,
                "high": close + 1.0,
                "low": close - 1.0,
                "close": close,
                "volume": 1000 + index,
            }
        )
    return pd.DataFrame(rows)


def test_build_feature_table_adds_expected_columns() -> None:
    raw = make_ohlcv("AAA", [10, 11, 12, 13, 14])

    features = build_feature_table(
        raw,
        moving_average_windows=(2, 3),
        volatility_windows=(2,),
        volume_windows=(2,),
        rsi_window=2,
        label_horizon=2,
    )

    expected_columns = {
        "return_1",
        "ma_2",
        "ma_3",
        "ma_distance_2",
        "ma_distance_3",
        "volatility_2",
        "volume_change_1",
        "volume_ma_2",
        "volume_ratio_2",
        "rsi_2",
        "future_return_2",
        "future_direction_2",
    }
    assert expected_columns.issubset(features.columns)
    assert features.loc[1, "ma_2"] == pytest.approx(10.5)
    assert features.loc[1, "ma_distance_2"] == pytest.approx(11 / 10.5 - 1.0)
    assert features.loc[0, "future_return_2"] == pytest.approx(12 / 10 - 1.0)
    assert pd.isna(features.loc[4, "future_return_2"])
    assert pd.isna(features.loc[4, "future_direction_2"])


def test_build_feature_table_does_not_mix_symbols() -> None:
    raw = pd.concat(
        [
            make_ohlcv("AAA", [10, 20, 30]),
            make_ohlcv("BBB", [100, 200, 300]),
        ],
        ignore_index=True,
    ).sort_values("date")

    features = build_feature_table(
        raw,
        moving_average_windows=(2,),
        volatility_windows=(2,),
        volume_windows=(2,),
        rsi_window=2,
        label_horizon=1,
    )

    aaa = features[features["symbol"] == "AAA"].reset_index(drop=True)
    bbb = features[features["symbol"] == "BBB"].reset_index(drop=True)
    assert pd.isna(aaa.loc[0, "return_1"])
    assert pd.isna(bbb.loc[0, "return_1"])
    assert aaa.loc[1, "ma_2"] == pytest.approx(15.0)
    assert bbb.loc[1, "ma_2"] == pytest.approx(150.0)


def test_build_feature_table_sorts_within_symbol_before_rolling() -> None:
    raw = make_ohlcv("AAA", [10, 20, 30]).iloc[[2, 0, 1]].reset_index(drop=True)

    features = build_feature_table(
        raw,
        moving_average_windows=(2,),
        volatility_windows=(2,),
        volume_windows=(2,),
        rsi_window=2,
        label_horizon=1,
    )

    assert features["date"].tolist() == sorted(features["date"].tolist())
    assert features.loc[1, "ma_2"] == pytest.approx(15.0)
    assert features.loc[0, "future_return_1"] == pytest.approx(20 / 10 - 1.0)
