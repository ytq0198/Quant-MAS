# RL / GRPO 模拟实验计划（Plus M7）

更新时间：2026-06-01（M7 第一版本地 ✅ EXP-20260602-021）

> Codex 任务：[codex_prompt_M7.md](codex_prompt_M7.md) · 设计：[项目plus设计.md §M7](../项目plus设计.md#m7强化学习--grpo-实验)

## 定位

M7 **不是**实盘 RL 交易系统，也**不是**用 RL 替代 LightGBM 或 walk-forward OOS 主指标。

```
OHLCV (+ 可选 ML signals)
    → TradingEnv（simulation only）
    → baseline policy / 多候选 rollouts
    → reward + RiskTool 审计（可选）
    → GRPO-style group-relative 排名（研究用）
```

**论文主指标**仍为 **EXP-20260602-008**：walk-forward **oos.sharpe 0.586**。  
RL 产出使用 `family=rl_simulation`，metrics 命名如 `simulation.sharpe`，**不得**与 `oos.sharpe` 混比。

## 已交付（第一版）

| 组件 | 路径 |
|------|------|
| Schema | `src/quant_mas/rl/env_schema.py` — `TradingEnvConfig`, `RewardConfig`, `StepResult` |
| TradingEnv | `trading_env.py` — gymnasium-like API；当前 bar 观察，下一根 bar open 执行 |
| Reward | `reward.py` — `compute_step_reward`, `compute_episode_metrics` |
| Policies | `baseline_policy.py` — Random / BuyAndHold / MLCopy |
| GRPO ranking | `grpo_experiment.py` — `CandidateRun`, `rank_candidates_by_group_relative_reward` |
| Mock data | `mock_data.py` — synthetic OHLCV + ML signals |
| CLI | `scripts/run_rl_baseline.py` |
| 配置 | `configs/rl.yaml` |
| 测试 | `test_trading_env.py` **13 passed**；`test_grpo_experiment.py` **6 passed** |
| 可选依赖 | `pyproject.toml` — `rl = ["gymnasium>=0.29"]` |

## 安全边界

- 不接 broker；不新增 live order API
- pytest 不联网、不依赖 GPU、不跑真实长训练
- 报告与 metrics 须含 `simulation_only: true` / `simulation.*` 前缀

## 已验证（本地）

```bash
python -m pytest tests/test_trading_env.py -v    # 13 passed
python -m pytest tests/test_grpo_experiment.py -v  # 6 passed
python -m pytest -v                              # 180 passed
python scripts/run_rl_baseline.py --config configs/rl.yaml --policy random --dry-run
```

记录：**EXP-20260602-021**（本地）；服务器待 **EXP-20260602-022**。

## 待验证

| 编号 | 内容 |
|------|------|
| EXP-20260602-022 | 服务器 pytest 180 + `run_rl_baseline.py --dry-run` |
| EXP-RL-003 | 可选：真实 features 上 MLCopy vs buy_hold（仍 simulation） |

## 相关文档

- [experiment_log.md](experiment_log.md)
- [research_protocol.md](research_protocol.md)
- [server_commands.md](server_commands.md) §6.10
