## Highlights

- Deterministic quant pipeline: data, features, strategies, backtest, risk, reports
- LightGBM direction model + walk-forward OOS evaluation
- **161 passing pytest** cases (mock/synthetic in tests)
- Agent layer: SupervisorAgent, ResearchAgent, optional LLM narration (**no live orders**)
- Memory/RAG v2, optional LangGraph workflow
- Text signal layer (M6 skeleton)

## Verified research baseline

- Walk-forward OOS sharpe **0.586** (EXP-20260602-008, server walk-forward)

## Install

```bash
git clone https://github.com/ytq0198/Quant-MAS.git
cd Quant-MAS
python -m pip install -e .
python -m pytest -v
```

## Not included

- No live trading / broker integration
- M7 RL / M8 MCP are roadmap only (not implemented)

MIT License · Research & education only — not financial advice.
