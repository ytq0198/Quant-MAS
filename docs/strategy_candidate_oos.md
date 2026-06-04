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
- Label columns may exist in the input parquet (server `features.parquet`); they are dropped before signal generation.
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

**Local / pytest** use `data/features/features.parquet` (synthetic).  
**Server (a6000)** use the same path as walk-forward EXP-008:

```text
/mnt/localDisk3/weizian/datasets/features/features.parquet
```

1. Export population candidates with M11.6 (**`--no-dry-run`** writes `candidates.json`; `--dry-run` does not).
2. Point `--candidate-json` to `outputs/candidates/candidates.json`.
3. Point `--features-path` to the real server feature parquet (see above).
4. Run `validate_candidate_oos.py --no-dry-run`.
5. Compare resulting `oos.sharpe` against `EXP-20260602-008`.

```bash
# Step 1 — required before validate_candidate_oos
python scripts/export_population_candidates.py \
  --population-config configs/population_training.yaml \
  --top-k 2 \
  --run-backtest-smoke \
  --no-dry-run

# Step 2 — OOS validation (server path)
python scripts/validate_candidate_oos.py \
  --candidate-json outputs/candidates/candidates.json \
  --candidate-id cand_mean_rev_1 \
  --features-path /mnt/localDisk3/weizian/datasets/features/features.parquet \
  --config configs/candidate_oos.yaml \
  --dry-run
```

Do not record candidate claims in papers until the real server walk-forward run
has completed and the artifacts are stored in ExperimentMemory.

## Verification

| Experiment | Environment | Result |
| --- | --- | --- |
| **EXP-20260602-032** | Local mock | **259 passed**; OOS tests **11/11** |
| **EXP-POP-005** | Server @ `ffef849` | ✅ **259 passed**; `cand_mean_rev_1` **oos.sharpe 1.036**（77 wf windows）vs baseline **0.586** |

## EXP-POP-005 Result (server, 2026-06-04)

| Field | Value |
| --- | --- |
| Candidate | `cand_mean_rev_1` (mean_reversion) |
| Windows | **77** |
| OOS range | 2019-07-05 → 2025-12-08 |
| **oos.sharpe** | **1.036** |
| ML baseline (EXP-008) | **0.586** |
| vs_baseline | **+0.450** |

This is a **rule-based population candidate** OOS result. It does not replace the paper's ML walk-forward baseline.

```bash
python -m pytest tests/test_candidate_oos_validation.py -v   # 11 passed
python scripts/validate_candidate_oos.py --help
python -m pytest -v   # 259 passed
```
