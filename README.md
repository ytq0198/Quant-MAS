# Quant MAS

Quant MAS is a research project for a multi-agent quantitative research and trading platform.

The first phase focuses on a deterministic quant research loop:

1. Load data
2. Build features
3. Run strategies
4. Backtest
5. Check risk
6. Record experiments and reports

LLM agents are planned for research, planning, explanation, reporting, and tool orchestration. They must not place live orders directly.

## Development

```powershell
pip install -e .
pytest
python -c "import quant_mas"
```

## Project Principles

- Quant Engine owns deterministic computation: data, features, models, strategy, backtest, risk, and execution.
- Agent Layer owns research, planning, explanation, reporting, and orchestration.
- All trading signals must pass backtesting, risk checks, audit, and human confirmation before any live action.
- Tests must not rely on real network requests or real LLM APIs.

