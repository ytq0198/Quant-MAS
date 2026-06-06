# server_ml_backtest_001

## Metrics

| Metric | Value |
|--------|-------|
| total_return | 68.2713 |
| annualized_return | 0.700753 |
| sharpe | 2.78099 |
| max_drawdown | -0.246427 |
| final_equity | 6.92713e+06 |
| bars | 2011 |

## Parameters

| Parameter | Value |
|-----------|-------|
| strategy | {"name": "ml_signal", "buy_threshold": 0.6, "sell_threshold": 0.4, "max_weight": 1.0} |
| features_path | /mnt/localDisk3/weizian/datasets/features/features.parquet |
| model_path | /mnt/localDisk3/weizian/models/lightgbm_direction_latest/model.pkl |
| feature_columns | ["open", "high", "low", "close", "volume", "return_1", "ma_5", "ma_20", "ma_distance_5", "ma_distance_20", "volatility_20", "volume_change_1", "volume_ma_20", "volume_ratio_20", "rsi_14"] |

## Artifacts

- `metrics.json`
- `equity_curve.csv`
- `trades.csv`
