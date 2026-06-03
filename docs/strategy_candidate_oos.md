# StrategyCandidate Walk-forward OOS Validation

Updated: 2026-06-03  
Scope: M11.7, validating population-selected candidates with walk-forward OOS.

M11.6 exports `StrategyCandidate` objects and can run a synthetic backtest
smoke. M11.7 is the first layer that is allowed to produce `oos.*` metrics,
because it uses chronological walk-forward windows.

```text
StrategyCandidate
  -> CandidateStrategyAdapter
  -> build_walk_forward_windows
  -> OOS BacktestEngine
  -> oos.* metrics
  -> ExperimentMemory
```

## Boundary

- No broker integration.
- No LLM calls.
- No model training.
- Candidate signals must not use `future_*`, label, or target columns.
- `backtest.*` smoke metrics from M11.6 are not OOS.
- `oos.*` is allowed only after this walk-forward hook runs.

Paper baseline remains:

- `EXP-20260602-008`
- `oos.sharpe = 0.586`

## CLI

```bash
python scripts/validate_candidate_oos.py --help

python scripts/validate_candidate_oos.py \
  --candidate-json outputs/candidates/candidates.json \
  --features-path data/features/features.parquet \
  --config configs/candidate_oos.yaml \
  --dry-run
```

Non-dry-run writes:

```text
outputs/candidate_oos/
  metrics.json
  windows.csv
  oos_equity_curve.csv
  oos_trades.csv
  summary.md
```

The summary explicitly reports the candidate OOS Sharpe, baseline Sharpe, and
their difference. It is still research output, not investment advice.

## Server Workflow

1. Export population candidates with M11.6.
2. Point `--candidate-json` to the generated `candidates.json`.
3. Point `--features-path` to the real server feature parquet.
4. Run `validate_candidate_oos.py --no-dry-run`.
5. Compare resulting `oos.sharpe` against `EXP-20260602-008`.

Do not record candidate claims in papers until the real server walk-forward run
has completed and the artifacts are stored in ExperimentMemory.

## Verification

| Experiment | Environment | Result |
| --- | --- | --- |
| **EXP-20260602-032** | Local mock | **259 passed**; OOS tests **11/11** |
| **EXP-POP-005** | Server real features | 📋 pending — compare `oos.sharpe` vs **0.586** |

Local acceptance:

```bash
python -m pytest tests/test_candidate_oos_validation.py -v   # 11 passed
python scripts/validate_candidate_oos.py --help
python -m pytest -v   # 259 passed
```
