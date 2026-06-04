# M12 RL Training Experiment Design

Updated: 2026-06-04  
Status: M12.1 implemented locally; server smoke pending

M12 extends the existing M7 simulation environment from **ranking only** to a
minimal, auditable **training loop**. It is intentionally mock-first and
simulation-only. It does not replace walk-forward OOS, and it does not create a
live trading path.

## Positioning

```text
M7 TradingEnv + baseline policies + GRPO ranking
    -> M12 trainable policy state + short training loop
    -> simulation.* / training.* metrics
    -> optional StrategyCandidate export stub
    -> M11.7 / M11.8 walk-forward OOS only after separate validation
```

The paper main baseline remains:

- `EXP-20260602-008`
- ML walk-forward `oos.sharpe = 0.586`

M11 competition candidates remain ablation/mechanism results:

- `EXP-POP-005` / `EXP-POP-006`
- rule-based mean-reversion candidates, `oos.sharpe = 1.036-1.039`
- not a replacement for the ML main baseline

M12 metrics must use:

- `training.*`
- `simulation.*`
- `summary.*`

M12 training code must not write:

- `oos.sharpe`
- `oos.total_return`
- any `oos.*` metric

If a trained policy should be evaluated out-of-sample, it must first be exported
or mapped into a `StrategyCandidate`, then validated through M11.7 or M11.8.

## Phase Split

### M12.1 Minimal GRPO Training Loop

Goal: prove a short deterministic training loop can update a policy state.

Deliverables:

| Component | Path |
|-----------|------|
| Trainable policy | `src/quant_mas/rl/grpo_agent.py` |
| Training loop | `src/quant_mas/rl/training_loop.py` |
| PPO stub | `src/quant_mas/rl/ppo_trainer.py` |
| MARL stub | `src/quant_mas/rl/marl_stub.py` |
| Config | `configs/rl_training.yaml` |
| CLI | `scripts/run_rl_experiment.py` |
| Tests | `tests/test_rl_training.py` |

Key design:

- `GRPOPolicyAgent` stores simple serializable action logits.
- `act()` returns a legal discrete action index for `TradingEnv`.
- `update_from_group_advantages()` reuses
  `rank_candidates_by_group_relative_reward`; no copied ranking semantics.
- `RLTrainingLoop.run(max_steps <= 10 in tests)` collects synthetic rollouts,
  ranks grouped candidate runs, updates policy state at least once, and reports
  simulation/training metrics.
- `PPOTrainer` is a stub with stable mock metrics.
- `MARLTrainingStub` is an explicit future extension point.

### M12.2 Policy Export Bridge

Goal: make the training output compatible with the existing research validation
chain without duplicating OOS code.

First version:

- `export_strategy_candidate_stub()` returns a documented stub.
- `schedule_walk_forward_eval_stub()` points to `scripts/validate_candidate_oos.py`
  and `scripts/batch_validate_candidates.py`.
- No automatic walk-forward execution inside M12.

Later version:

```text
trained policy
  -> StrategyCandidate / deterministic adapter
  -> M11.7 single OOS or M11.8 batch OOS
  -> ablation table
```

### M12.3 Optional Server Smoke

Goal: ensure the CLI and checkpoints run on the server without making pytest slow.

Recommended command:

```bash
python scripts/run_rl_experiment.py \
  --config configs/rl_training.yaml \
  --algorithm grpo \
  --max-steps 50 \
  --no-dry-run
```

This remains simulation-only. Record as `EXP-RL-003` or `EXP-POP-007` depending
on the experiment log convention.

## Proposed Public API

```python
@dataclass
class PolicyState:
    action_logits: list[float]
    step_count: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)


class GRPOPolicyAgent:
    def act(self, observation: dict[str, float], info: dict[str, Any]) -> int: ...
    def snapshot(self) -> PolicyState: ...
    def load_snapshot(self, state: PolicyState) -> None: ...
    def update_from_group_advantages(...) -> dict[str, float]: ...
```

```python
@dataclass(frozen=True)
class TrajectoryRecord:
    agent_id: str
    window_id: int
    action_indices: list[int]
    rewards: list[float]
    episode_reward: float
    metrics: dict[str, float]


@dataclass(frozen=True)
class TrainingRunResult:
    algorithm: str
    metrics: dict[str, Any]
    policy_state: PolicyState
    artifacts: dict[str, str]
```

## Metrics Contract

Required:

- `summary.algorithm`
- `summary.simulation_only = true`
- `summary.baseline_experiment_id = EXP-20260602-008`
- `summary.baseline_oos_sharpe = 0.586`
- `training.policy_step_count`
- `training.policy_delta_norm`
- `simulation.episode_reward_mean`
- `simulation.sharpe_mean`
- `simulation.total_return_mean`
- `simulation.max_drawdown_mean`

Forbidden:

- `oos.*`
- broker/order/live execution metrics
- LLM-generated `target_weight`

## Safety Rules

- No broker integration.
- No live order API.
- No real LLM calls.
- No network.
- No mandatory GPU or torch dependency.
- No future labels in observations.
- Every action must stay inside `TradingEnv` discrete action levels and its risk
  clipping path.
- Checkpoints must be small JSON artifacts.

## CLI Contract

```bash
python scripts/run_rl_experiment.py --help

python scripts/run_rl_experiment.py \
  --config configs/rl_training.yaml \
  --algorithm grpo \
  --max-steps 10 \
  --dry-run

python scripts/run_rl_experiment.py \
  --config configs/rl_training.yaml \
  --algorithm ppo \
  --max-steps 10 \
  --dry-run
```

Dry-run prints a JSON summary and does not write ExperimentMemory.

Non-dry-run writes:

```text
outputs/rl_training/<experiment_name>/
  policy_state.json
  metrics.json
  summary.md
```

ExperimentMemory:

- `family = rl_training`
- metrics contain `training.*` and `simulation.*`
- metrics do not contain `oos.*`

## Test Plan

`tests/test_rl_training.py` should cover at least:

1. `GRPOPolicyAgent.act()` returns a legal action index.
2. Fixed seed behavior is deterministic.
3. Group-relative update changes logits or increments `step_count`.
4. `PolicyState` snapshot round-trip.
5. `RLTrainingLoop.run(max_steps=10)` completes on synthetic data.
6. Metrics include `training.*` and `simulation.*`.
7. Metrics do not contain any `oos.*`.
8. GRPO ranking integration uses `rank_candidates_by_group_relative_reward`.
9. Checkpoint files are written.
10. PPO stub returns stable mock metrics.
11. MARL stub behavior is explicit.
12. Walk-forward export/eval stub does not write OOS.
13. `run_rl_experiment.py --help` works.
14. Dry-run CLI works.
15. Non-dry-run writes ExperimentMemory.

Regression tests:

```bash
python -m pytest tests/test_rl_training.py -v
python -m pytest tests/test_trading_env.py tests/test_grpo_experiment.py -v
python -m pytest -v
```

Expected baseline after implementation: `282+ passed`.

## Paper Usage

M12 is best described as:

> A simulation-only RL training prototype that learns/update policy parameters
> under risk-constrained discrete trading actions.

Do not write:

> RL outperforms the ML OOS baseline.

Unless the trained policy is separately validated through M11.7/M11.8
walk-forward OOS.
