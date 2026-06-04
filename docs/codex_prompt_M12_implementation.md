# Codex Prompt M12 Implementation

请为 Quant MAS v3 实现 **M12.1：最小 RL Training Loop**。

## 当前基线

- 项目路径：`D:\scientific reasearch and work\SRTP\Quant MAS`
- 测试基线：`266 passed`
- M7 已有：`TradingEnv`、baseline policies、GRPO group-relative ranking
- M11–M11.8 已完成：Population → StrategyCandidate → walk-forward OOS batch
- 论文主 baseline：`EXP-20260602-008`，`oos.sharpe = 0.586`

## 核心原则

1. M12 是 **simulation-only RL training prototype**。
2. 训练 loop 只能写 `training.*`、`simulation.*`、`summary.*`。
3. 禁止在 M12 内写任何 `oos.*`。
4. 若训练 policy 需要 OOS，必须事后走 M11.7 / M11.8。
5. 不接 broker，不调用真实 LLM，不联网，不依赖 GPU。
6. pytest 用 synthetic data，训练步数 ≤ 10。
7. 不破坏 M7 / M11 / M11.8 现有测试。

## 需要实现

### 新文件

1. `src/quant_mas/rl/grpo_agent.py`
   - `PolicyState`
   - `GRPOPolicyAgent`
   - `act()`
   - `snapshot()`
   - `load_snapshot()`
   - `update_from_group_advantages()`

2. `src/quant_mas/rl/training_loop.py`
   - `TrajectoryRecord`
   - `TrainingRunResult`
   - `RLTrainingLoop`
   - checkpoint 写入：`policy_state.json`、`metrics.json`、`summary.md`
   - `export_strategy_candidate_stub()`
   - `schedule_walk_forward_eval_stub()`

3. `src/quant_mas/rl/ppo_trainer.py`
   - `TrainerProtocol`
   - `PPOTrainer` stub

4. `src/quant_mas/rl/marl_stub.py`
   - `MultiAgentTrainingProtocol`
   - `MARLTrainingStub`

5. `configs/rl_training.yaml`

6. `scripts/run_rl_experiment.py`
   - `--config`
   - `--algorithm grpo|ppo`
   - `--market-data-path`
   - `--max-steps`
   - `--seed`
   - `--output-dir`
   - `--memory-path`
   - `--dry-run / --no-dry-run`

7. `tests/test_rl_training.py`

### 修改文件

- `src/quant_mas/rl/__init__.py`
- `docs/rl_plan.md`
- `docs/rl_experiment.md`

## Metrics Contract

必须包含：

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

禁止包含：

- `oos.sharpe`
- `oos.total_return`
- 任意 `oos.*`

## 测试要求

`tests/test_rl_training.py` 至少覆盖：

1. `GRPOPolicyAgent.act()` 返回合法 action index。
2. 固定 seed 行为确定。
3. `update_from_group_advantages()` 更新 logits 或递增 step_count。
4. `PolicyState` snapshot round-trip。
5. `RLTrainingLoop.run(max_steps=10)` 不 crash。
6. metrics 含 `training.*` / `simulation.*`。
7. metrics 不含 `oos.*`。
8. 复用 `rank_candidates_by_group_relative_reward`。
9. checkpoint 文件写入。
10. PPO stub 返回稳定 metrics。
11. MARL stub 行为明确。
12. OOS stub 不写 `oos.*`。
13. `run_rl_experiment.py --help` 正常。
14. dry-run CLI 正常。
15. non-dry-run 写 ExperimentMemory。

## 验收命令

```bash
python -m pytest tests/test_rl_training.py -v
python -m pytest tests/test_trading_env.py tests/test_grpo_experiment.py -v
python scripts/run_rl_experiment.py --help
python scripts/run_rl_experiment.py --config configs/rl_training.yaml --algorithm grpo --max-steps 10 --dry-run
python scripts/run_rl_experiment.py --config configs/rl_training.yaml --algorithm ppo --max-steps 10 --dry-run
python -m pytest -v
```

预期：全量 pytest 从 `266` 增加到 `278+`。

## 文档口径

M12 只能表述为：

> simulation-only RL training prototype

不得表述为：

> RL 已经在 OOS 上超过 baseline

除非训练策略另行通过 M11.7/M11.8 walk-forward OOS 验证。
