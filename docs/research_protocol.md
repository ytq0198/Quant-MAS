# Quant MAS Research Protocol

This protocol defines the minimum record required for a Quant MAS experiment to be comparable across MA Cross, LightGBM, MLSignalStrategy, Walk-forward, and future RAG/LLM/RL experiments.

## Required Record

Every experiment must record:

- Data range: start date, end date, data source, and whether data is synthetic or real.
- Symbols: all instruments used in training, validation, testing, and backtesting.
- Features: feature config, label horizon, and any feature-selection rules.
- Model or strategy: strategy name, model type, training params, device, and random seed when applicable.
- Split: chronological train/validation/test split, walk-forward window sizes, and whether the result is OOS.
- Costs: commission, slippage, and any execution assumptions.
- Risk: risk config, position limits, drawdown guard, and whether human approval is required.
- Primary metric: the declared main metric before running the experiment.
- Artifacts: metrics file, report summary, equity curve, trades, model artifacts, and config snapshots.

## Main Paper Metric

The main metric used in thesis or paper conclusions must come from Walk-forward OOS evaluation.

Single split validation, in-sample training metrics, and non-OOS backtests may be used for debugging and ablation, but they are not sufficient as the final research claim.

## Comparison Families

Current comparison families:

- `ma_cross`: deterministic moving-average strategy baseline.
- `lightgbm`: supervised direction model training baseline.
- `ml_backtest`: ML probability signal backtest.
- `walk_forward`: walk-forward sample-out evaluation.
- `other`: future RAG, LLM, RL, and exploratory experiments until a more specific family is added.

## Reporting Rule

Use `scripts/compare_experiments.py` to produce `comparison.csv` and `comparison.md` from ExperimentMemory before writing conclusions. Missing metrics must remain blank rather than being guessed.
