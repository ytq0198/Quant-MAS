# server_walk_forward_text_002

## Metrics

### summary

| Metric | Value |
|--------|-------|
| window_count | 19 |
| feature_count | 16 |
| target_column | future_direction_5 |
| device_requested | auto |
| device_resolved | cuda |
| device_fallback | False |
| device_reason |  |

### train

| Metric | Value |
|--------|-------|
| accuracy_mean | 0.972849 |
| auc_mean | 0.997325 |
| positive_rate_mean | 0.611007 |
| samples | 28728 |
| start_date | 2018-01-31 |
| end_date | 2024-08-05 |

### val

| Metric | Value |
|--------|-------|
| accuracy_mean | 0.497354 |
| auc_mean | 0.491178 |
| positive_rate_mean | 0.536898 |
| samples | 7182 |
| start_date | 2020-02-03 |
| end_date | 2025-02-05 |

### test

| Metric | Value |
|--------|-------|
| accuracy_mean | 0.486076 |
| auc_mean | 0.48897 |
| positive_rate_mean | 0.533417 |
| samples | 7182 |
| start_date | 2020-08-03 |
| end_date | 2025-08-07 |

### oos

| Metric | Value |
|--------|-------|
| accuracy_mean | 0.480368 |
| auc_mean | 0.476077 |
| positive_rate_mean | 0.520746 |
| samples | 3591 |
| start_date | 2021-02-02 |
| end_date | 2025-11-05 |
| total_return | 0.442816 |
| annualized_return | 0.0802347 |
| sharpe | 0.57868 |
| max_drawdown | -0.264678 |
| final_equity | 144282 |
| bars | 1197 |
| backtest_total_return_mean | 0.0206293 |
| backtest_sharpe_mean | 0.9107 |
| backtest_max_drawdown_mean | -0.0599986 |

### walk_forward

| Metric | Value |
|--------|-------|
| train_window | 504 |
| validation_window | 126 |
| test_window | 126 |
| oos_window | 63 |
| step | 63 |
| max_windows |  |

## Parameters

| Parameter | Value |
|-----------|-------|
| features_path | /mnt/localDisk3/weizian/datasets/features/features_with_text_wf002.parquet |
| feature_columns | ["open", "high", "low", "close", "volume", "return_1", "ma_5", "ma_20", "ma_distance_5", "ma_distance_20", "volatility_20", "volume_change_1", "volume_ma_20", "volume_ratio_20", "rsi_14", "finbert_sentiment"] |
| target_column | future_direction_5 |
| config | {"model": {"name": "lightgbm_direction", "device": "auto", "params": {"n_estimators": 100, "learning_rate": 0.05, "num_leaves": 31, "random_state": 42}}, "target": "future_direction", "data": {"features_path": "data/features/features.parquet"}, "walk_forward": {"train_window": 504, "validation_window": 126, "test_window": 126, "oos_window": 63, "step": 63, "max_windows": null}, "strategy": {"name": "ml_signal", "buy_threshold": 0.6, "sell_threshold": 0.4, "max_weight": 1.0}, "portfolio": {"initial_cash": 100000}, "costs": {"commission_bps": 1.0, "slippage_bps": 1.0}, "output": {"dir": "outputs/reports/walk_forward_latest"}, "experiment": {"name": "walk_forward_oos"}} |

## Artifacts

- `metrics.json`
- `windows.csv`
- `oos_equity_curve.csv`
- `oos_trades.csv`
