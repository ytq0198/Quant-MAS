# M12.4 Observation-Aware RL Policy

Updated: 2026-06-04  
Status: M12.4 ✅ dual-end; EXP-POP-010 OOS sharpe **0.387** (ablation vs baseline **0.586**)

## Implementation Status

M12.4 has been implemented as the first observation-aware RL policy path:

- `FeatureLinearPolicyAgent` reads `position_weight`, `last_return`, `rolling_vol_5`, `volume`, and `close`.
- `run_rl_experiment.py` supports `--policy-type logits|feature_linear`.
- RL policy export now supports `FeaturePolicyState` and emits `agent_type="feature_linear_policy"`.
- M11.7 `CandidateStrategyAdapter` can replay the exported feature-linear policy on OHLCV bars and generate state-dependent `target_weight`.
- Local validation: `python -m pytest tests/test_rl_observation_policy.py -v` -> **12 passed**.
- Full local validation: `python -m pytest -v` -> **308 passed**.

The current implementation still follows the M12 boundary: training metrics remain `training.*` / `simulation.*`; only M11.7/M11.8 may write `oos.*`.

M12.4 is the next small step after the M12.1-M12.3 smoke pipeline. The goal is
to make the RL policy depend on market observations instead of selecting a
constant action from flat logits.

## Motivation

EXP-POP-009 validated the full RL path:

```text
M12.1 training
  -> M12.2 StrategyCandidate export
  -> M11.7 OOS validation
  -> oos.sharpe = 0.0
```

This was not a bug. The exported policy selected `argmax(logits)=0`, and
`action_levels[0] = 0.0`, so the candidate stayed fully in cash.

M12.4 addresses the next bottleneck:

> The policy must read market state before it can produce non-constant exposure.

## Boundary

M12.4 remains:

- simulation-only during training
- no broker
- no LLM
- no network
- no mandatory torch/GPU
- no `oos.*` inside training

OOS validation remains external:

```text
M12.4 train/export
  -> StrategyCandidate
  -> M11.7 validate_candidate_oos.py or M11.8 batch_validate_candidates.py
```

## Design

### FeatureLinearPolicyAgent

Implementation:

```text
src/quant_mas/rl/feature_policy.py
```

Public API:

```python
@dataclass
class FeaturePolicyState:
    feature_names: list[str]
    action_weights: list[list[float]]  # action_space_n x feature_count
    action_bias: list[float]
    step_count: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)


class FeatureLinearPolicyAgent:
    def act(self, observation: dict[str, float], info: dict[str, Any]) -> int: ...
    def snapshot(self) -> FeaturePolicyState: ...
    def load_snapshot(self, state: FeaturePolicyState) -> None: ...
    def update_from_group_advantages(...): ...
```

Default feature set:

- `position_weight`
- `last_return`
- `rolling_vol_5`
- `volume`
- `close`

The policy computes:

```text
score[action] = bias[action] + sum(weight[action, feature] * normalized_feature)
```

Then picks `argmax(score)`.

Normalization should be simple and deterministic:

- `last_return`: use raw value
- `rolling_vol_5`: use raw value
- `position_weight`: raw value in `[0, 1]`
- `volume`: `log1p(volume) / 20`
- `close`: `log1p(close) / 10`

### Training Loop Integration

M12.4 extends M12.1:

- `RLTrainingLoop` accepts either `GRPOPolicyAgent` or `FeatureLinearPolicyAgent`.
- CLI adds `--policy-type logits|feature_linear`.
- Config adds `policy.type` and `policy.feature_names`.

Example:

```yaml
policy:
  type: feature_linear
  feature_names:
    - position_weight
    - last_return
    - rolling_vol_5
    - volume
    - close
```

### Export Bridge

M12.2 export supports both states:

- `PolicyState` from logits policy → `agent_type=grpo_policy`
- `FeaturePolicyState` from feature-linear policy → `agent_type=feature_linear_policy`
- **`agent_type` is auto-detected** from checkpoint; stale `grpo_policy` in config is ignored

`StrategyCandidate.params` should include:

- `policy_type`
- `feature_names`
- `action_weights`
- `action_bias`
- `step_count`

M12.4 updated the existing policy export logic. It still rejects `oos.*`.

### OOS Adapter

`CandidateStrategyAdapter` supports `momentum`, `mean_reversion`, `grpo_policy`,
and `feature_linear_policy`. For feature-linear candidates the adapter:

- compute the same observation features from OHLCV bars
- apply the exported linear policy
- map action index to target weight using `action_levels`
- still drop `future_*` columns before signal generation

This is the only M12.4 path that should produce OOS metrics, and only through
M11.7/M11.8.

## Files

| Component | Path |
|-----------|------|
| Feature policy | `src/quant_mas/rl/feature_policy.py` |
| Training integration | `src/quant_mas/rl/training_loop.py` |
| Export integration | `src/quant_mas/rl/policy_export.py` |
| Candidate adapter | `src/quant_mas/research/candidate_validation.py` |
| Config | `configs/rl_training.yaml` / `configs/rl_policy_export.yaml` |
| CLI | `scripts/run_rl_experiment.py` / `scripts/export_rl_policy_candidate.py` |
| Tests | `tests/test_rl_observation_policy.py` |

## Test Results (Local)

| Suite | Result |
|-------|--------|
| `tests/test_rl_observation_policy.py` | **12 passed** |
| `tests/test_rl_training.py` + `tests/test_rl_policy_export.py` | **28 passed** |
| `tests/test_candidate_oos_validation.py` + `tests/test_candidate_oos_batch.py` | **20 passed** |
| Full `python -m pytest -v` | **308 passed** |

## Test Plan (Coverage)

1. feature policy reads `last_return` and changes action when observation changes.
2. fixed seed / fixed state is deterministic.
3. snapshot round-trip.
4. update increments `step_count`.
5. training loop runs with `policy_type=feature_linear`.
6. metrics remain `training.*` / `simulation.*`.
7. export writes `agent_type=feature_linear_policy`.
8. exported candidate contains feature weights and action levels.
9. candidate adapter generates non-constant target weights on synthetic trend/reversal data.
10. adapter ignores `future_*` labels.
11. M11.7 OOS hook runs on synthetic feature-linear candidate.
12. full pytest remains green.

## Research Interpretation

M12.4 should be reported as:

> an observation-aware RL policy prototype that can produce state-dependent
> exposure, followed by the same independent walk-forward OOS validation hook.

It should not be reported as:

> a production RL trading strategy.

## Success Criteria

The first success criterion is not high Sharpe. It is:

- exported policy is no longer trivially all-cash
- OOS adapter produces state-dependent target weights
- simulation metrics and OOS metrics remain separated

Only after that should performance be compared against:

- ML baseline `0.586`
- population candidate OOS `1.036–1.039`
