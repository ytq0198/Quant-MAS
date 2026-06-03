# Strategy Candidate Bridge

Updated: 2026-06-03  
Scope: M11.6, connecting population winners back to deterministic Quant Engine validation.

M11 and M11.5 produce `population.*` and `simulation.*` rankings. M11.6 turns
those rankings into auditable `StrategyCandidate` records and optionally runs a
small deterministic backtest smoke.

```text
PopulationTrainingLoop result
  -> StrategyCandidate
  -> candidates.json / candidates.csv
  -> synthetic backtest smoke
  -> future walk-forward OOS hook
```

## Boundary

This module does not run real walk-forward OOS in its first version. It must not
write `oos.*` metrics. The paper-level baseline remains:

- `EXP-20260602-008`
- `oos.sharpe = 0.586`

Metric families:

- `population.*`: selection information from the population layer
- `simulation.*`: short simulation evidence from population training
- `backtest.*`: deterministic synthetic backtest smoke
- `oos.*`: only allowed after a real walk-forward job, not in M11.6

## CLI

Dry-run candidate export with backtest smoke:

```bash
python scripts/export_population_candidates.py \
  --population-config configs/population_training.yaml \
  --top-k 2 \
  --run-backtest-smoke \
  --dry-run
```

Write artifacts and ExperimentMemory:

```bash
python scripts/export_population_candidates.py \
  --config configs/candidate_validation.yaml \
  --no-dry-run
```

Artifacts:

```text
outputs/candidates/
  candidates.json
  candidates.csv
  summary.md
```

`--run-walk-forward` is a stub in M11.6. It returns metadata explaining that no
OOS metrics were produced.

## Why This Matters

The competitive layer becomes useful to the main research loop only when its
winners can be converted into Quant Engine candidates. This bridge is the
handoff:

```text
strategy discovery -> candidate validation -> future walk-forward OOS comparison
```

Population Elo is a search signal. It is not the final research claim.

## Verification

| Experiment | Environment | Result |
| --- | --- | --- |
| **EXP-20260602-031** | Local | **248 passed**; bridge tests **11/11** |
| **EXP-POP-004** | Server a6000-9961 | 📋 pending pull + pytest + export dry-run |

Local acceptance:

```bash
python -m pytest tests/test_strategy_candidate_bridge.py -v   # 11 passed
python scripts/export_population_candidates.py \
  --population-config configs/population_training.yaml \
  --top-k 2 \
  --run-backtest-smoke \
  --dry-run
```
