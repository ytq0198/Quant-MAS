# StrategyCandidate Batch OOS Comparison

Updated: 2026-06-04  
Scope: M11.8, batch validation for M11.7 StrategyCandidate OOS.

M11.8 validates multiple exported `StrategyCandidate` records with the same
walk-forward OOS hook introduced in M11.7. It does not add a new trading rule,
broker path, LLM call, or model-training path.

```text
candidates.json
  -> run_candidate_batch_walk_forward
  -> per-candidate M11.7 OOS reports
  -> candidate_oos_comparison.csv / .md
  -> ExperimentMemory family=strategy_candidate_oos_batch
```

## Research Boundary

- M11.6 exports candidates and may write `population.*`, `simulation.*`, or smoke `backtest.*`.
- M11.7 is the first hook allowed to write per-candidate `oos.*`.
- M11.8 only batches M11.7 results and ranks candidates by `oos.sharpe`.
- Paper main baseline remains `EXP-20260602-008` with `oos.sharpe = 0.586`.
- Batch candidate OOS belongs in ablation or mechanism analysis unless a later protocol promotes it.

## CLI

```bash
python scripts/batch_validate_candidates.py --help

python scripts/batch_validate_candidates.py \
  --candidate-json outputs/candidates/candidates.json \
  --features-path /mnt/localDisk3/weizian/datasets/features/features.parquet \
  --config configs/candidate_oos.yaml \
  --top-k 5 \
  --no-dry-run
```

Optional explicit subset:

```bash
python scripts/batch_validate_candidates.py \
  --candidate-json outputs/candidates/candidates.json \
  --candidate-ids cand_mean_rev_1 cand_momentum_2 \
  --features-path /mnt/localDisk3/weizian/datasets/features/features.parquet \
  --no-dry-run
```

## Artifacts

Non-dry-run writes:

```text
outputs/candidate_oos_batch/
  metrics.json
  candidate_oos_comparison.csv
  candidate_oos_comparison.md
  candidates/<candidate_id>/
    metrics.json
    windows.csv
    oos_equity_curve.csv
    oos_trades.csv
    summary.md
```

The comparison table includes:

- `candidate_id`
- `agent_type`
- `oos.sharpe`
- `oos.total_return`
- `oos.max_drawdown`
- `summary.vs_baseline_sharpe`
- `exceeds_baseline`

## Server Validation (EXP-POP-006)

Validated on a6000-9961 @ `9477c3d` (2026-06-04):

- `python -m pytest -v` → **266 passed** in **45.63s**
- `batch_validate_candidates.py --top-k 5 --no-dry-run` → **4 candidates**, **77 windows**
- Best: `cand_mean_rev_1_g1_1_g2_2` **oos.sharpe 1.039** vs baseline **0.586** (+0.453)
- All **4/4** exceed baseline; Population input rank ≠ OOS rank
- Artifacts: `outputs/candidate_oos_batch/candidate_oos_comparison.csv` / `.md`
- ExperimentMemory: `family=strategy_candidate_oos_batch`

Compare with **EXP-POP-005** (single `cand_mean_rev_1` **1.036**) and **EXP-20260602-008** (ML **0.586**).
