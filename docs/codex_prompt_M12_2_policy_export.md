# Codex Prompt M12.2 Policy Export

请为 Quant MAS v3 实现 **M12.2：RL Policy → StrategyCandidate Export Bridge**。

## 当前基线

- M12.1 已双端闭环：`282 passed`
- 服务器 EXP-POP-007 / EXP-RL-003 已通过
- RL 训练产物：

```text
outputs/rl_training/rl_training_grpo_001/
  policy_state.json
  metrics.json
  summary.md
```

- M11.7 / M11.8 已提供 OOS 验证：
  - `scripts/validate_candidate_oos.py`
  - `scripts/batch_validate_candidates.py`

## 目标

把 M12.1 的 `policy_state.json` + `metrics.json` 转换为统一的
`StrategyCandidate`，方便后续通过 M11.7 / M11.8 做 walk-forward OOS。

M12.2 只做 bridge，不跑 OOS，不写 `oos.*`。

## 必须遵守

1. 不调用 broker。
2. 不调用 LLM。
3. 不联网。
4. 不训练模型。
5. 不运行 walk-forward。
6. 不写任何 `oos.*` metric。
7. 允许保留 `summary.baseline_oos_sharpe` 作为 reference metadata。
8. 输出 `StrategyCandidate` 必须通过 `assert_no_oos_metrics()`。

## 需要实现

### 1. `src/quant_mas/rl/policy_export.py`

实现：

```python
def load_policy_state(path: str | Path) -> PolicyState: ...
def load_training_metrics(path: str | Path) -> dict[str, Any]: ...
def export_policy_candidate(
    *,
    policy_state_path: str | Path,
    metrics_path: str | Path,
    candidate_id: str | None = None,
    agent_type: str = "grpo_policy",
) -> StrategyCandidate: ...
def write_rl_candidates(candidates: list[StrategyCandidate], output_dir: str | Path) -> dict[str, str]: ...
```

Candidate 约定：

- `source="rl_training"`
- `agent_id` 来自 `policy_state.metadata.agent_id`，缺省 `"rl_policy"`
- `candidate_id` 缺省：`rl_<agent_id>_<step_count>`
- `agent_type="grpo_policy"`
- `params` 包含：
  - `policy_state_path`
  - `action_logits`
  - `step_count`
  - `action_policy="discrete_logits"`
- `selection_metrics` 只包含：
  - `training.*`
  - `simulation.*`
  - 可选 `summary.algorithm`
  - 可选 `summary.baseline_experiment_id`
  - 可选 `summary.baseline_oos_sharpe`
- `notes` 明确：requires M11.7/M11.8 OOS validation

如果 metrics 中存在顶层 `oos` 或 key 以 `oos.` 开头，必须 raise `ValueError`。

### 2. `scripts/export_rl_policy_candidate.py`

CLI：

- `--policy-state`
- `--metrics`
- `--output-dir`
- `--candidate-id`
- `--agent-type`
- `--memory-path`
- `--experiment-name`
- `--dry-run / --no-dry-run`

行为：

- dry-run：打印 candidate JSON，不写文件、不写 ExperimentMemory。
- non-dry-run：
  - 写 `candidates.json`
  - 写 `candidates.csv`
  - 写 `export_summary.md`
  - 写 ExperimentMemory，`family="rl_policy_export"`

### 3. `configs/rl_policy_export.yaml`

包含默认：

```yaml
rl_policy_export:
  policy_state: outputs/rl_training/rl_training_grpo_001/policy_state.json
  metrics: outputs/rl_training/rl_training_grpo_001/metrics.json
  output_dir: outputs/rl_candidates
  agent_type: grpo_policy

experiment:
  name: rl_policy_export_001
  family: rl_policy_export
  memory_path: null
```

### 4. 更新导出

`src/quant_mas/rl/__init__.py` export 新函数。

### 5. 文档

更新：

- `docs/rl_policy_export.md`
- `docs/rl_experiment.md`
- `docs/rl_plan.md`

### 6. 测试：`tests/test_rl_policy_export.py`

至少 12 项：

1. load policy state round-trip。
2. load metrics。
3. export candidate 基本字段正确。
4. params 包含 action_logits / step_count / policy_state_path。
5. selection_metrics 包含 training/simulation。
6. rejects top-level `oos`。
7. rejects `oos.sharpe`。
8. write candidates artifacts。
9. CLI help。
10. CLI dry-run 不写文件。
11. non-dry-run 写 ExperimentMemory。
12. 输出 candidates 可被 `StrategyCandidate.from_dict` 读取。

## 验收命令

```bash
python -m pytest tests/test_rl_policy_export.py -v
python -m pytest tests/test_rl_training.py tests/test_strategy_candidate_bridge.py -v
python scripts/export_rl_policy_candidate.py --help
python -m pytest -v
```

预期全量 pytest：`282+ passed`。

## 论文口径

正确：

> RL training exports a simulation-trained StrategyCandidate, then OOS is evaluated through M11.7/M11.8.

错误：

> RL simulation Sharpe is OOS Sharpe.
