# Population Training Loop

Updated: 2026-06-03  
Scope: M11.5, a mock-first training loop for strategy populations.

M11 introduced one competitive evaluation round. M11.5 adds a short training
loop:

```text
initial population
  -> competitive mock evaluation
  -> Elo / reward rankings
  -> Top-K retention
  -> deterministic mutation
  -> next generation
```

This remains simulation-only. It does not connect to brokers, LLMs, databases,
or GPUs.

## Relationship To M11 And M12

| Stage | Purpose | Status |
| --- | --- | --- |
| M11 | Single competitive mock evaluation | Implemented |
| M11.5 | Multi-generation population loop | Implemented |
| M12 | Heavier RL / autocurriculum training | Planned |

M11.5 gives M12 a small reusable backbone: `PopulationTrainingLoop`,
`GenerationSummary`, generation artifacts, and ExperimentMemory logging.

## Metric Families

Population training records only auxiliary metrics:

- `population.*`: generations, final top agent, Elo
- `simulation.*`: mean reward, mean Sharpe, drawdown

It must not write `oos.*`. Paper-level evidence remains the walk-forward OOS
baseline:

- `EXP-20260602-008`
- `oos.sharpe = 0.586`

## CLI

```bash
python scripts/run_population_training.py --help

python scripts/run_population_training.py \
  --config configs/population_training.yaml \
  --dry-run
```

To write artifacts and ExperimentMemory:

```bash
python scripts/run_population_training.py \
  --config configs/population_training.yaml \
  --no-dry-run
```

Artifacts:

```text
outputs/population_training/
  generation_001_metrics.json
  generation_002_metrics.json
  generation_003_metrics.json
  rankings.csv
  summary.md
```

`summary.md` explicitly states:

```text
simulation_only: true
Population metrics are not walk-forward OOS metrics.
Paper baseline remains EXP-20260602-008 oos.sharpe 0.586.
```

## Safety

- No live trading.
- No broker APIs.
- No LLM-generated target weights.
- RiskAgent remains mandatory before simulation steps.
- No synthetic population metric can be treated as a paper OOS result.

## Verification

| Experiment | Environment | Result |
| --- | --- | --- |
| **EXP-20260602-030** | Local | **237 passed**; loop tests **12/12** |
| **EXP-POP-003** | Server a6000-9961 @ `aa841d4` | **237 passed** (41.83s); 3-gen `--dry-run` OK |
| **EXP-POP-004** | Server @ `7ab510f` | **248 passed** (55.15s); M11.6 export dry-run OK |

Server dry-run observed deterministic mutation (e.g. `mean_rev_1_g1_1` scale 1.01 → `mean_rev_1_g1_1_g2_2` scale 1.03), Elo draws at 1500 on mock data, and `simulation.sharpe_mean` ≈ 7.15 — **not** walk-forward OOS **0.586**.

## M11.6 Handoff

After population training, export Top-K candidates for Quant Engine smoke validation:

```bash
python scripts/export_population_candidates.py \
  --population-config configs/population_training.yaml \
  --top-k 2 \
  --run-backtest-smoke \
  --dry-run
```

See [strategy_candidate_bridge.md](strategy_candidate_bridge.md) for the full M11.6 bridge (`StrategyCandidate`, `backtest.*`, walk-forward stub).

Next step: [strategy_candidate_oos.md](strategy_candidate_oos.md) — M11.7 walk-forward OOS hook (writes `oos.*`).
