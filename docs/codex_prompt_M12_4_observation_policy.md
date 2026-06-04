# Codex Prompt M12.4 Observation-Aware RL Policy

请为 Quant MAS v3 实现 **M12.4：Observation-Aware RL Policy**。

## 当前基线

- M12.1：RL training loop 双端通过
- M12.2：RL policy export 双端通过
- M12.3：RL candidate OOS 已通过，结果 `oos.sharpe=0.0`
- 当前 pytest：**308 passed**（M12.4 本地实现完成）

## 背景结论

EXP-POP-009 的 RL OOS 为 0.0，不是 bug。原因是当前 logits policy 不读取市场观测，argmax 选择 action index 0，即 `target_weight=0.0`，形成全现金策略。

M12.4 的目标是让 RL policy 读取 observation，产生状态相关 target weight。

## 目标

实现一个轻量、无 torch 依赖的 `FeatureLinearPolicyAgent`：

```text
observation features
  -> linear score per action
  -> action index
  -> target_weight
```

训练仍然只写 `training.*` / `simulation.*`。OOS 仍然只通过 M11.7/M11.8。

## 需要实现

### 1. `src/quant_mas/rl/feature_policy.py`

实现：

```python
@dataclass
class FeaturePolicyState:
    feature_names: list[str]
    action_weights: list[list[float]]
    action_bias: list[float]
    step_count: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)


class FeatureLinearPolicyAgent:
    def act(self, observation: dict[str, float], info: dict[str, Any]) -> int: ...
    def snapshot(self) -> FeaturePolicyState: ...
    def load_snapshot(self, state: FeaturePolicyState) -> None: ...
    def update_from_group_advantages(...): ...
```

默认 feature names：

- `position_weight`
- `last_return`
- `rolling_vol_5`
- `volume`
- `close`

归一化：

- `position_weight`: raw
- `last_return`: raw
- `rolling_vol_5`: raw
- `volume`: `log1p(volume) / 20`
- `close`: `log1p(close) / 10`

### 2. `src/quant_mas/rl/training_loop.py`

支持 policy 类型：

- logits / `GRPOPolicyAgent`
- feature_linear / `FeatureLinearPolicyAgent`

不要破坏现有 M12.1 测试。

### 3. `scripts/run_rl_experiment.py`

新增 CLI：

- `--policy-type logits|feature_linear`

配置读取：

```yaml
policy:
  type: feature_linear
  feature_names: [...]
```

### 4. `src/quant_mas/rl/policy_export.py`

支持导出 `FeaturePolicyState`：

`StrategyCandidate`：

- `source="rl_training"`
- `agent_type="feature_linear_policy"`
- params 包含：
  - `policy_type`
  - `feature_names`
  - `action_weights`
  - `action_bias`
  - `step_count`
  - `action_levels`

仍然拒绝 `oos.*`。

### 5. `src/quant_mas/research/candidate_validation.py`

扩展 `CandidateStrategyAdapter`：

- 支持 `agent_type="feature_linear_policy"`
- 从 OHLCV 生成与 TradingEnv 一致的 observation features
- 用 exported policy params 计算 action index
- 映射到 `target_weight`
- 严禁读取 `future_*`

### 6. 配置

更新：

- `configs/rl_training.yaml`
- `configs/rl_policy_export.yaml`

### 7. 测试：`tests/test_rl_observation_policy.py`

至少 12 项：

1. feature policy 对不同 observation 给出不同 action。
2. deterministic snapshot round-trip。
3. update increments step_count。
4. training loop supports `policy_type=feature_linear`。
5. metrics 不含 `oos.*`。
6. CLI dry-run supports `--policy-type feature_linear`。
7. export supports feature policy state。
8. exported candidate agent_type 正确。
9. params 包含 feature weights。
10. CandidateStrategyAdapter generates non-constant target weights。
11. adapter ignores future labels。
12. synthetic M11.7 OOS hook can run with feature-linear candidate。

## 验收命令

```bash
python -m pytest tests/test_rl_observation_policy.py -v
python -m pytest tests/test_rl_training.py tests/test_rl_policy_export.py -v
python scripts/run_rl_experiment.py --config configs/rl_training.yaml --policy-type feature_linear --max-steps 10 --dry-run
python -m pytest -v
```

预期：`296+ passed`。

## 科研边界

M12.4 成功标准不是高 Sharpe，而是：

- policy 不再是全现金常数策略
- OOS adapter 能生成状态相关 target_weight
- simulation 和 OOS 继续严格隔离

论文主 baseline 仍是 `EXP-20260602-008 / oos.sharpe=0.586`。
