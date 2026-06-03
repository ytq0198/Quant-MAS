# Plus M7：强化学习 / GRPO 实验 — Codex 提示词

**状态：✅ 已完成（本地 EXP-20260602-021，180 passed，2026-06-01）**

更新时间：2026-06-01（M7 第一版 skeleton 本地验收）

> **用法**：先粘贴下方「固定前缀」，再粘贴「M7 主任务」整段交给 Codex。  
> **设计依据**：[项目plus设计.md §M7](../项目plus设计.md#m7强化学习--grpo-实验) · 配套：[rl_plan.md](rl_plan.md) · 前置：**M1–M6 ✅**（EXP-TEXT-WF-001 可选，非阻塞）

---

## 固定前缀（每次必贴）

```
你正在开发 Quant MAS 科研项目。
路径：D:\scientific reasearch and work\SRTP\Quant MAS

测试基线：本地 + 服务器 **161 passed**（Plus M6，EXP-20260602-019/020）。
OOS 主 baseline：EXP-20260602-008，oos.sharpe **0.586**（walk-forward，19 窗）。
Walk-forward + text（exploratory）：EXP-TEXT-WF-001，oos.sharpe **0.563**。

硬性原则：
1. M7 是 **simulation only** — 不接 broker、不下实盘单、不新增 live order API。
2. **RL / GRPO 不替代** LightGBM + walk-forward 的论文主指标；RL reward 为 **模拟层辅助指标**，报告须标注 simulation。
3. 策略/env 输出的 target_weight **必须**可接入现有 `RiskTool` / `check_position_limits`（与 Prompt 18 一致）。
4. pytest **不联网、不跑真实 PPO/SAC 长训练、不依赖 GPU**；全部 synthetic OHLCV + mock policy + 确定性 reward。
5. **禁止 future leakage**：env step 只能使用 `t` 及之前观测；奖励用 `t→t+1` 收益，不得用未来特征/标签。
6. 请只实现当前 **M7** 一个模块；改完后 `python -m pytest -v` 全量通过（预期 161+，新增 test_trading_env + test_grpo_experiment）。
7. WANDB 仅 `.env`；不要 commit API key、大 checkpoint、或实盘相关配置。
8. 新实验结论若涉及收益对比，须与 **EXP-20260602-008 OOS sharpe 0.586** 区分族别（family=`rl_simulation` ≠ `walk_forward`），不得用单段 ML sharpe 2.78 冒充 OOS。
```

---

## M7 主任务（复制给 Codex）

```
请为 Quant MAS v2 增加 RL 模拟实验模块（Plus M7）。

## 背景

v1 / Plus 已有：
- backtest/engine.py — BacktestEngine，**下一根 bar 成交**（open 价调仓）
- backtest/metrics.py — sharpe、drawdown、total_return
- backtest/walk_forward.py — OOS 主指标（EXP-20260602-008，oos.sharpe 0.586）
- risk/ — RiskLimits、check_position_limits、check_drawdown；RiskTool（Prompt 18）
- strategies/ — MovingAverageCrossStrategy、MLSignalStrategy（读 pred_proba → target_weight）
- research/baseline.py — BaselineRegistry、compare_experiments（M1）
- **尚无** gymnasium 风格 TradingEnv、RL baseline CLI、GRPO-style 候选排序

M7 目标：
1. **TradingEnv** — 在 synthetic / parquet OHLCV 上模拟 long-only 离散仓位交互。
2. **Reward** — 可解释 reward（return − cost − turnover − drawdown 惩罚）。
3. **Baseline policies** — Random / BuyAndHold / MLCopy（读已有 ML target_weight 列）。
4. **GRPO-style ranking** — 对**多候选策略**在同一 OOS 窗口组内做 **group-relative reward 排名**（研究用，非 LLM GRPO 训练框架）。
5. **CLI** — run_rl_baseline.py（--help + mock dry-run）。

第一版重点：**mock pytest 全绿** + CLI help；不在 pytest 中调用 gymnasium 真实 `env.render()` 或 multi-hour 训练。

## 需要实现的文件

### 1. 包结构

src/quant_mas/rl/
  __init__.py
  env_schema.py          # TradingEnvState, StepResult, ActionSpace 定义
  trading_env.py         # TradingEnv（gymnasium-like API，可不硬依赖 gymnasium）
  reward.py              # compute_step_reward / compute_episode_metrics
  baseline_policy.py     # RandomPolicy, BuyAndHoldPolicy, MLCopyPolicy
  grpo_experiment.py     # rank_candidates_by_group_relative_reward
  mock_data.py           # build_synthetic_ohlcv_episode 供测试

configs/rl.yaml

scripts/run_rl_baseline.py

tests/test_trading_env.py      # ≥10 项
tests/test_grpo_experiment.py  # ≥6 项

docs/rl_plan.md                # 若不存在则创建；简要说明 M7 定位与验收

### 2. env_schema.py

```python
@dataclass
class TradingEnvConfig:
    initial_cash: float = 100_000.0
    action_levels: tuple[float, ...] = (0.0, 0.25, 0.5, 1.0)  # long-only target weights
    commission_rate: float = 0.0005
    slippage_bps: float = 1.0
    max_steps: int | None = None

@dataclass
class StepResult:
    observation: dict[str, float] | np.ndarray
    reward: float
    terminated: bool
    truncated: bool
    info: dict[str, Any]
```

提供序列化 / 校验 helper；action 必须是 `action_levels` 之一。

### 3. trading_env.py

实现 `class TradingEnv`（**不强制** inherit `gymnasium.Env`，但 API 对齐）：

```python
class TradingEnv:
    def __init__(self, market_data: pd.DataFrame, *, config: TradingEnvConfig, symbol: str | None = None): ...
    def reset(self, *, seed: int | None = None) -> tuple[Any, dict]: ...
    def step(self, action_index: int) -> StepResult: ...
    @property
    def action_space_n(self) -> int: ...
    @property
    def observation_dim(self) -> int: ...
```

规则：
- `market_data` 须含 `date, open, high, low, close, volume`（单 symbol 或 env 内 filter 一个 symbol）
- **按 date 升序**；`step i` 在 bar `i` 观测，在 bar `i+1` **open** 执行调仓（与 BacktestEngine 一致）
- 最后一根 bar：`terminated=True`
- 观测仅含当前及历史：如 `[position_weight, last_return, rolling_vol_5]` — **不得**含 future label 列
- 提供 `render_episode_summary() -> dict` 返回 episode return、max_dd、turnover（供 CLI / memory）

可选：若 `import gymnasium` 成功，提供 `as_gymnasium_env()` wrapper；pytest 不依赖 gymnasium 也须全绿。

### 4. reward.py

```python
def compute_step_reward(
    *,
    prev_equity: float,
    equity: float,
    turnover: float,
    drawdown: float,
    config: RewardConfig,
) -> float: ...

def compute_episode_metrics(equity_curve: pd.Series) -> dict[str, float]:
    """sharpe, total_return, max_drawdown, turnover_sum — 复用 backtest.metrics 若可"""
```

`RewardConfig` 权重可来自 `configs/rl.yaml`：
- `w_return`, `w_cost`, `w_turnover`, `w_drawdown_penalty`
- reward 为标量，数值有限（pytest 可断言符号/范围）

### 5. baseline_policy.py

```python
class Policy(Protocol):
    def act(self, observation: Any, info: dict) -> int: ...  # action index

class RandomPolicy: ...          # 确定性 seed
class BuyAndHoldPolicy: ...    # 始终 max long action
class MLCopyPolicy: ...        # 读 features/signals parquet 的 target_weight → 最近 action_level
```

`MLCopyPolicy` 构造时传入 `signals: pd.DataFrame`（含 date, target_weight）；**按 date 对齐**，无 future row。

提供 `build_policy(name: str, **kwargs) -> Policy` factory。

### 6. grpo_experiment.py

**注意**：第一版是 **GRPO-style group-relative ranking**，不是完整 GRPO 梯度训练。

```python
@dataclass
class CandidateRun:
    name: str
    policy: str
    window_id: int
    reward: float
    metrics: dict[str, float]

def rank_candidates_by_group_relative_reward(
    candidates: list[CandidateRun],
    *,
    group_key: str = "window_id",
) -> list[CandidateRun]:
    """
    在每个 group（如 walk-forward window）内，按 reward 做 relative ranking。
    可选：减去 group mean（group-relative advantage 风格），再全局排序。
    返回按 rank 降序列表，并写入 rank / group_mean / relative_reward 字段。
    """
```

提供 `summarize_grpo_ranking(ranked) -> dict` 供 CLI / ExperimentMemory metadata。

与 M1 关系：若接入 ExperimentMemory，family=`rl_simulation` 或 `grpo_ranking`；**不得**覆盖 walk_forward 的 `oos.sharpe`。

### 7. mock_data.py

- `build_synthetic_ohlcv(n_bars=64, symbol="SYN") -> pd.DataFrame` — 确定性价格路径
- `build_synthetic_ml_signals(ohlcv, *, weight=0.5) -> pd.DataFrame` — MLCopyPolicy 测试用

### 8. configs/rl.yaml

```yaml
rl:
  simulation_only: true
  initial_cash: 100000.0
  action_levels: [0.0, 0.25, 0.5, 1.0]
  max_steps: null
reward:
  w_return: 1.0
  w_cost: 0.1
  w_turnover: 0.05
  w_drawdown_penalty: 0.2
paths:
  market_data: data/sample/market_data.parquet
  signals: null
  output_dir: outputs/rl_baseline
policy:
  name: random   # random | buy_hold | ml_copy
experiment:
  name: rl_baseline_mock_001
  seed: 42
grpo:
  group_key: window_id
```

### 9. scripts/run_rl_baseline.py

CLI：
- `--config configs/rl.yaml`
- `--policy random|buy_hold|ml_copy`（覆盖 yaml）
- `--market-data-path`、`--signals-path`、`--output-dir`
- `--seed`、`--dry-run`、`--help`

行为：
- 读 yaml + 路径；缺 parquet 时 **dry-run** 可用 synthetic（与 train_text_model mock 一致）
- 跑单 episode 或短 rollouts；写 `metrics.json`、`episode_summary.json`、`summary.md`
- summary **必须**含 `"simulation_only": true`
- 可选：经 `RiskTool` 或 `check_position_limits` 对每步 target_weight 做 clip 审计，metadata 记录 violations
- 不调用 broker；不写入 live order

### 10. pyproject.toml 可选依赖（可选）

```toml
rl = [
    "gymnasium>=0.29",
]
```

核心 `pip install -e .` **不装** gymnasium；TradingEnv 自实现 API 即可。若安装 `[rl]`，可增加 optional wrapper 测试（可 skip）。

### 11. tests/test_trading_env.py（≥10 项）

全部 synthetic，**不联网**：

1. TradingEnvConfig 校验（非法 action_levels）
2. reset 初始 observation 维度 / 键一致
3. step 递增 date，不越界
4. 最后一步 terminated=True
5. 下一 bar 执行：调仓后 position 与 action_level 一致（允许数值误差）
6. 观测不含未来 bar 的 close
7. reward 有限且 deterministic（固定 seed）
8. episode summary 含 total_return / max_drawdown
9. BuyAndHoldPolicy 全 episode 高仓位
10. RandomPolicy 确定性 seed 可复现
11. MLCopyPolicy 与 signals 日期对齐
12. test_end_to_end_pipeline / test_walk_forward **保持通过**

### 12. tests/test_grpo_experiment.py（≥6 项）

1. 单 group 内排序顺序正确
2. 多 group 各自 relative ranking 互不影响
3. group mean  subtraction（若实现）改变 relative_reward 但不改变组内序关系（构造用例）
4. 空 candidates → 空列表或明确 error
5. summarize_grpo_ranking 输出含 top candidate name
6. tie-breaking 确定性（同 reward 按 name 排序）

## 兼容性要求

- **不得修改** BacktestEngine / walk_forward 默认行为
- **不得**让 Supervisor 直接调用 RL env 下单；RL 仅新 CLI + 可选 future Tool（第一版可不注册 ToolRegistry）
- M5 ResearchAgent / M6 text_signals **不受影响**
- ExperimentMemory 新 run：`family="rl_simulation"`，metrics 用 `simulation.sharpe` 等命名，**避免**与 `oos.sharpe` 混淆

## 禁止

- 连接 broker / 实盘 API / 真实下单
- pytest 中 multi-epoch 神经网络 RL 训练
- 用 RL episode sharpe **替代** walk-forward OOS 写论文主结论
- future feature / label 进入 observation
- commit `.env`、W&B API key、大 checkpoint

## 验收命令

python -m pytest tests/test_trading_env.py -v
python -m pytest tests/test_grpo_experiment.py -v
python -m pytest -v                                    # 全量 161+ passed
python scripts/run_rl_baseline.py --help
python scripts/run_rl_baseline.py --config configs/rl.yaml --policy random --dry-run
```

---

## Cursor 后续（Codex 完成后）

1. ~~确认 `docs/rl_plan.md` 与实现对齐~~ ✅
2. ~~更新 `docs/architecture.md` — RL Simulation Layer~~ ✅
3. ~~更新 `docs/experiment_log.md` — EXP-20260602-021 / EXP-RL-001~~ ✅
4. ~~更新 `docs/progress.md` / `项目进度.md` — M7 状态~~ ✅
5. 服务器 pull + pytest **180 passed** + `run_rl_baseline.py --dry-run`（EXP-20260602-022 待做）
6. ~~`docs/server_commands.md` §6.10 M7 命令块~~ ✅

**科研说明**：RL metrics 为 `simulation.*`；主 baseline 仍为 walk-forward **oos.sharpe 0.586**。

---

## 参考现有代码

| 模块 | 路径 |
|------|------|
| BacktestEngine | `src/quant_mas/backtest/engine.py` |
| Metrics | `src/quant_mas/backtest/metrics.py` |
| Walk-forward | `src/quant_mas/backtest/walk_forward.py` |
| Risk | `src/quant_mas/risk/limits.py`、`tools/quant/risk_tool.py` |
| MLSignalStrategy | `src/quant_mas/strategies/ml_signal_strategy.py` |
| Research baseline | `src/quant_mas/research/baseline.py` |
| M6 text（不替代） | `src/quant_mas/features/text_signals.py` |

---

## 与 M6 / M8 的关系

| 模块 | 用途 |
|------|------|
| **M6** FinBERT/text | 结构化特征 → LightGBM → **OOS 主指标** |
| **M7** RL/GRPO | **模拟环境** + 候选策略 group-relative 排名（辅助研究） |
| **M8** MCP/A2A | 协议 adapter（在 M7 之后；不接外部 MCP server） |

M7 **不**替换 LightGBM，**不**让 LLM/RL 直接输出未经 RiskTool 的订单。

---

## 实验编号（验收后写入 experiment_log）

| 编号 | 内容 |
|------|------|
| **EXP-RL-001** | TradingEnv + baseline policies（random / buy_hold / ml_copy）mock 或服务器 dry-run |
| **EXP-RL-002** | GRPO-style group-relative ranking smoke（synthetic candidates） |

论文主指标仍为 **EXP-20260602-008**（oos.sharpe **0.586**）。
