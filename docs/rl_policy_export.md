# M12.2 RL Policy Export Bridge

Updated: 2026-06-04  
Status: M12.2 + M12.3 OOS adapter implemented; EXP-POP-008 server export ✅

M12.2 converts M12.1 simulation-trained policy artifacts into the existing
`StrategyCandidate` schema. It is a bridge only. It must not run walk-forward
OOS, and it must not write `oos.*` metrics.

## Positioning

```text
M12.1 RL training
  -> policy_state.json + metrics.json
  -> M12.2 export RL StrategyCandidate
  -> candidates.json / candidates.csv
  -> M11.7 validate_candidate_oos.py or M11.8 batch_validate_candidates.py
  -> oos.* metrics after separate validation
```

This keeps the same research boundary used by M11:

- simulation and training metrics select candidates
- walk-forward OOS metrics validate candidates
- no live trading path is created

## Input Contract

Required input artifacts:

```text
outputs/rl_training/<experiment_name>/
  policy_state.json
  metrics.json
```

`policy_state.json` should contain:

- `action_logits`
- `step_count`
- `metadata.agent_id`
- `metadata.simulation_only`

`metrics.json` should contain:

- `summary.*`
- `training.*`
- `simulation.*`
- no `oos.*`

## Output Contract

M12.2 writes:

```text
outputs/rl_candidates/
  candidates.json
  candidates.csv
  export_summary.md
```

Candidate schema:

```python
StrategyCandidate(
    candidate_id="rl_<agent_id>_<step_count>",
    source="rl_training",
    agent_id=<metadata.agent_id>,
    agent_type="grpo_policy",
    params={
        "policy_state_path": ".../policy_state.json",
        "action_logits": [...],
        "step_count": ...,
        "action_policy": "discrete_logits",
    },
    selection_metrics={
        "training.policy_step_count": ...,
        "training.policy_delta_norm": ...,
        "simulation.sharpe_mean": ...,
        "simulation.total_return_mean": ...,
        "simulation.max_drawdown_mean": ...,
    },
    notes="Exported from M12 RL simulation; requires M11.7/M11.8 OOS validation.",
)
```

The export must call `assert_no_oos_metrics()` before writing.

## Proposed Files

| Component | Path |
|-----------|------|
| Bridge module | `src/quant_mas/rl/policy_export.py` |
| CLI | `scripts/export_rl_policy_candidate.py` |
| Config | `configs/rl_policy_export.yaml` |
| Tests | `tests/test_rl_policy_export.py` |

Small API:

```python
def load_policy_state(path: str | Path) -> PolicyState: ...
def load_training_metrics(path: str | Path) -> dict[str, Any]: ...
def export_policy_candidate(...) -> StrategyCandidate: ...
def write_rl_candidates(candidates, output_dir) -> dict[str, str]: ...
```

## CLI Contract

```bash
python scripts/export_rl_policy_candidate.py --help

python scripts/export_rl_policy_candidate.py \
  --policy-state outputs/rl_training/rl_training_grpo_001/policy_state.json \
  --metrics outputs/rl_training/rl_training_grpo_001/metrics.json \
  --output-dir outputs/rl_candidates \
  --dry-run

python scripts/export_rl_policy_candidate.py \
  --policy-state outputs/rl_training/rl_training_grpo_001/policy_state.json \
  --metrics outputs/rl_training/rl_training_grpo_001/metrics.json \
  --output-dir outputs/rl_candidates \
  --no-dry-run
```

Optional arguments:

- `--candidate-id`
- `--agent-type grpo_policy`
- `--experiment-name`
- `--memory-path`

Dry-run returns JSON and writes nothing.

Non-dry-run writes candidates and an ExperimentMemory record:

- `family = rl_policy_export`
- metrics use `training.*` / `simulation.*`
- no `oos.*`

## Validation Rules

M12.2 must reject:

- missing policy state
- missing metrics
- metrics containing `oos` or `oos.*`
- non-simulation artifacts pretending to be OOS

M12.2 must allow:

- `summary.baseline_oos_sharpe` as reference metadata
- `summary.baseline_experiment_id`

These are summary references, not RL OOS results.

## M12.3 OOS Adapter (`grpo_policy`)

After export, M11.7 `CandidateStrategyAdapter` maps `grpo_policy` candidates to walk-forward signals:

- Read `params.action_logits` from the exported candidate
- Pick argmax logit index (deterministic tie-break: lowest index)
- Map index → `target_weight` via `params.action_levels` or default `[0.0, 0.25, 0.5, 1.0]`

Current M12.1 `GRPOPolicyAgent.act()` ignores observations, so OOS uses a **constant** target weight per symbol. This matches simulation behavior but is not state-dependent.

```bash
python scripts/validate_candidate_oos.py \
  --candidate-json outputs/rl_candidates/candidates.json \
  --features-path /path/to/features.parquet \
  --config configs/candidate_oos.yaml \
  --no-dry-run
```

Only M11.7/M11.8 write `oos.*` metrics for these candidates.

## Test Plan

`tests/test_rl_policy_export.py` should cover:

1. load `policy_state.json` round-trip.
2. load `metrics.json` and extract training/simulation fields.
3. export candidate with `source=rl_training`.
4. candidate contains policy path and action logits.
5. candidate selection metrics contain training/simulation values.
6. export rejects metrics containing `oos.*`.
7. dry-run CLI writes nothing.
8. non-dry-run writes `candidates.json`, `candidates.csv`, `export_summary.md`.
9. non-dry-run writes ExperimentMemory with `family=rl_policy_export`.
10. output candidates can be loaded by `StrategyCandidate.from_dict`.
11. `export_strategy_candidate_stub()` from M12.1 remains no-OOS.
12. full M7/M12.1 tests remain green.

## Relationship To OOS

After export, run OOS separately:

```bash
python scripts/validate_candidate_oos.py \
  --candidate-json outputs/rl_candidates/candidates.json \
  --features-path /mnt/localDisk3/weizian/datasets/features/features.parquet \
  --config configs/candidate_oos.yaml \
  --no-dry-run
```

If multiple RL candidates exist:

```bash
python scripts/batch_validate_candidates.py \
  --candidate-json outputs/rl_candidates/candidates.json \
  --features-path /mnt/localDisk3/weizian/datasets/features/features.parquet \
  --top-k 5 \
  --no-dry-run
```

Only those M11.7/M11.8 commands may write `oos.*`.

## Paper Usage

Correct wording:

> RL training produced a simulation-trained policy candidate, which was exported
> into the same StrategyCandidate schema and then evaluated through the same
> walk-forward OOS validation hook.

Incorrect wording:

> RL simulation Sharpe outperformed the OOS baseline.
