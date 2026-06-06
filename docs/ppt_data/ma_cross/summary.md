# server_ma_cross_real_001

## Metrics

| Metric | Value |
|--------|-------|
| total_return | 2.02453 |
| annualized_return | 0.148766 |
| sharpe | 1.00066 |
| max_drawdown | -0.205808 |
| final_equity | 302453 |
| bars | 2011 |

## Parameters

| Parameter | Value |
|-----------|-------|
| symbols | ["AAPL", "MSFT", "SPY"] |
| start | 2018-01-01 |
| end | 2025-12-31 |
| strategy | ma_cross |
| features_config | configs/features.yaml |
| backtest_config | configs/backtest.yaml |
| backtest | {"strategy": {"name": "moving_average_cross", "fast_window": 5, "slow_window": 20}, "portfolio": {"initial_cash": 100000}, "costs": {"commission_bps": 1.0, "slippage_bps": 1.0}} |

## Artifacts

- `metrics.json`
- `equity_curve.csv`
- `trades.csv`
