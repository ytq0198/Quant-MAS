# Competitive Learning / Strategy Population

Updated: 2026-06-03  
Scope: v3 M11 mock-first competitive learning layer.

M11 adds a simulation-only population layer above the existing M7 trading
environment. It is designed for comparing strategy-agent ideas, not for live
trading and not for replacing walk-forward OOS evidence.

## Positioning

| Layer | Purpose | Status |
| --- | --- | --- |
| M7 RL simulation | Single policy in `TradingEnv` | Implemented |
| M11 population | Multiple `StrategyAgent` instances, RiskAgent, Elo, Top-K | Implemented, mock-first |
| M12 training loop | Longer autocurriculum / RL training loop | Planned |

Each agent runs a shadow episode on the same synthetic market window. The runner
uses the existing `TradingEnv`, so action timing remains next-bar execution. No
broker, order API, or live account is connected.

## Agent Pool

| Agent | M11 Status | Notes |
| --- | --- | --- |
| `MomentumAgent` | Implemented | Increases exposure when recent signal is positive |
| `MeanReversionAgent` | Implemented | Contrarian baseline against momentum |
| `MLSignalAgent` | Planned | Could read mock ML target-weight signals |
| `TextSignalAgent` | Planned | Could read M6 text-signal columns after OOS validation |
| `RiskAgent` | Implemented | Clips proposals through shared risk-limit logic |

Every `StrategyAgent.propose()` returns a target weight proposal. The proposal
must pass through `RiskAgent` before entering the environment.

## Metric Families

Competitive learning writes only auxiliary metrics:

- `population.*`: Elo, top agent, agent count, window count
- `simulation.*`: mean episode Sharpe, return, drawdown, reward

These are not paper-level OOS metrics. They must not be mixed with
`oos.sharpe`. Current paper baseline remains:

- `EXP-20260602-008`
- walk-forward `oos.sharpe = 0.586`

## CLI

```bash
python scripts/run_competitive_experiment.py --help

python scripts/run_competitive_experiment.py \
  --config configs/competitive.yaml \
  --mode mock \
  --dry-run
```

Non-dry-run writes:

- `outputs/competitive/metrics.json`
- `outputs/competitive/summary.md`
- one `ExperimentMemory` record with family metadata `competitive_learning`

`--mode walk_forward` is intentionally a stub in M11. It must not fabricate OOS
metrics; a real hook belongs in a later research task.

## Safety

- Simulation only; no broker integration.
- LLM agents do not generate target weights for this layer.
- Risk clipping is mandatory before environment steps.
- Population Elo and simulation Sharpe are research aids, not investment advice.

## M12 Handoff

M12 can reuse:

- `PopulationManager`
- `AgentSpec`
- `CompetitiveEpisodeRunner`
- Elo utilities in `quant_mas.rl.elo_rating`

The first M11 implementation deliberately keeps training out of scope so the
pytest suite remains fast, deterministic, and offline.
