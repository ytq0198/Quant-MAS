# Plus v3 M12：强化学习训练实验 — Codex 提示词

**状态：📋 待实现（前置 M11–M11.8 ✅ 双端闭环，266 pytest，2026-06-04）**

更新时间：2026-06-04

> **用法**：先粘贴下方「固定前缀」，再粘贴「M12 主任务」整段交给 Codex。  
> **设计依据**：[项目v3设计.md §M12](../项目v3设计.md#m12强化学习训练实验) · 配套：新建 `docs/rl_experiment.md` · 前置：**M7 ✅**（180 pytest，TradingEnv + GRPO ranking）· **M11–M11.8 ✅**（266 pytest，Population → StrategyCandidate → OOS batch）

---

## 固定前缀（每次必贴）

```
你正在开发 Quant MAS 科研项目（v3 阶段）。
路径：D:\scientific reasearch and work\SRTP\Quant MAS

测试基线：本地+服务器 **266 passed**（v3 M11.8，EXP-033 / EXP-POP-006 @ `f7cd591`）。
OOS 主 baseline：EXP-20260602-008，oos.sharpe **0.586**（ML walk-forward，19 窗）。
M11 候选 OOS（ablation）：EXP-POP-005 / EXP-POP-006 — 规则型 mean-reversion **1.036–1.039**，**非** ML 主 baseline 替代。
M6 text OOS exploratory：EXP-TEXT-WF-001，oos.sharpe **0.563** vs **0.586**。
M7/M12 RL：simulation only；训练产出 **simulation.*** / **training.***；**禁止**在训练 loop 内直接写 `oos.*`。

硬性原则：
1. **simulation / training only** — 不接 broker、不下实盘单、LLM **不直接**输出 target_weight 绕过 RiskAgent。
2. M12 训练 loop 写入 ExperimentMemory 时 family 建议 **`rl_training`** 或 **`grpo_training`**；metrics 前缀 **`simulation.*`** / **`training.*`**，**禁止**写入 `oos.sharpe`（OOS 仅能通过既有 M11.7 `validate_candidate_oos.py` / M11.8 batch hook 事后评估）。
3. 策略/env 每步 target_weight **必须**经 `RiskAgent` 或 `check_position_limits` 裁剪（与 M11 一致）。
4. pytest **不联网、不跑 GPU 长训练、不依赖 torch 必选**；synthetic OHLCV + **≤10 training steps** + 确定性 seed；若引入 torch 须 optional extra + skip 测试。
5. **禁止 future leakage**：TradingEnv 观测与 M7 一致，仅 `t` 及之前信息。
6. 请只实现当前 **M12** 一个模块；改完后 `python -m pytest -v` 全量通过（M12 基线 **266+**，增量在 `tests/test_rl_training.py`）。
7. **不得破坏** M7 `TradingEnv` / `run_rl_baseline.py` / `test_trading_env.py` / `test_grpo_experiment.py`；**不得破坏** M11 `CompetitiveEpisodeRunner` / population / candidate OOS 链路。
8. 禁止 commit `.env`、API key、大 checkpoint（>1MB 测试 fixture 除外且须 gitignore）。
9. GRPO 第一版是 **可运行的训练 loop 骨架**（group-relative advantage + 简单策略更新），不是完整 LLM-GRPO 或大规模 PPO 库封装。
10. 论文主指标仍为 walk-forward OOS **0.586**；RL 训练 sharpe **不得**替代 OOS 写主结论。
```

---

## M12 主任务（复制给 Codex）

```
请为 Quant MAS v3 实现 **M12：强化学习训练实验**（mock-first，与 M13 编排解耦）。

## 背景

v2 / v3 已有（M7）：
- rl/trading_env.py — 单 agent 离散仓位 TradingEnv（下一 bar open 成交）
- rl/baseline_policy.py — Random / BuyAndHold / MLCopy
- rl/grpo_experiment.py — CandidateRun + rank_candidates_by_group_relative_reward（**仅排名，无梯度/参数更新**）
- rl/reward.py、rl/mock_data.py、rl/env_schema.py
- scripts/run_rl_baseline.py — 单 policy 单 episode dry-run
- configs/rl.yaml
- tests/test_trading_env.py（13）、tests/test_grpo_experiment.py（6）

v3 已有（M11–M11.8）：
- agents/strategy_agent.py — MomentumAgent、MeanReversionAgent；propose → target_weight
- agents/risk_agent.py — clip/veto
- agents/population_manager.py — Elo、Top-K、autocurriculum mutate
- rl/competitive_runner.py — CompetitiveEpisodeRunner（多 agent × 多 window mock）
- rl/population_training.py — PopulationTrainingLoop（多代 simulation）
- rl/candidate_bridge.py — Population Top-K → StrategyCandidate（M11.6）
- research/candidate_validation.py — run_candidate_walk_forward（M11.7，**唯一**候选写 oos.*）
- scripts/run_competitive_experiment.py、run_population_training.py、export_population_candidates.py、validate_candidate_oos.py、batch_validate_candidates.py

M12 **尚无**：
- 可迭代 **GRPO / PPO 训练 loop**（参数更新 + checkpoint）
- Trainable policy agent（非固定 heuristic StrategyAgent）
- run_rl_experiment.py CLI
- 训练后 → StrategyCandidate 导出 **stub hook**（可选 walk-forward 评估占位）

M12 目标（第一版）：
1. **GRPOPolicyAgent** — 可训练离散策略（action index logits / 简单 tabular 权重）；观测 → action；支持 `update_from_group_advantages()`。
2. **TrainingLoop** — 在 TradingEnv 上收集 rollouts；按 window/group 做 group-relative advantage（**复用** grpo_experiment.rank_candidates_by_group_relative_reward）；执行 **≥1 次**策略更新；写 checkpoint + metrics。
3. **PPOTrainer 骨架** — 接口 + stub 实现（`train_step` 可 no-op 或 mock 更新）；配置 `algorithm: grpo | ppo`，ppo 路径 pytest 可跑通但不需真实 PPO 库。
4. **MARL 接口预留** — `MultiAgentTrainingProtocol` 或 `MARLTrainingStub`（文档说明 CTDE 扩展点，第一版不实现真实多 agent 梯度）。
5. **与 M11 衔接（可选薄层）** — 可从 PopulationManager Top-1 spec 初始化 heuristic agent 对照组；训练产出 **TrainablePolicy** 与 **StrategyAgent** 并列评估（simulation only）。
6. **CLI** — `scripts/run_rl_experiment.py`（`--algorithm grpo|ppo`、`--dry-run`、`--max-steps 10`、`--no-dry-run` 写 ExperimentMemory）。
7. **事后 OOS hook（stub）** — `training_loop.export_strategy_candidate_stub()` 或 `schedule_walk_forward_eval_stub()`：仅返回说明/空 artifacts，**不**在 M12 内复制 walk_forward 逻辑；文档指向 M11.7。
8. **文档** — `docs/rl_experiment.md`（指标族、与 0.586 / M11 OOS 关系、M13 衔接）。
9. **测试** — `tests/test_rl_training.py`（≥12 项 mock smoke）。

第一版**不做**：真实 GPU 大规模训练、PyTorch 必选依赖、神经网络 MARL、LLM policy、broker、pytest 内 77 窗 walk-forward、在训练 loop 写 `oos.*`。

## 需要实现的文件

### 1. 包结构

src/quant_mas/rl/
  grpo_agent.py           # GRPOPolicyAgent, PolicyState, group-relative update
  training_loop.py        # RLTrainingLoop, TrainingRunResult, checkpoint I/O
  ppo_trainer.py          # PPOTrainer stub + TrainerProtocol
  marl_stub.py            # MARLTrainingStub / protocol only（可选合并进 training_loop.py）

configs/rl_training.yaml

scripts/run_rl_experiment.py

docs/rl_experiment.md

tests/test_rl_training.py   # ≥12 项

增量更新（小改即可）：
- src/quant_mas/rl/__init__.py — export 新公开 API
- docs/rl_plan.md — 增加「M12 训练 loop」小节 + 指向 rl_experiment.md（勿删 M7 历史）

### 2. grpo_agent.py

```python
@dataclass
class PolicyState:
    """Serializable trainable policy state (logits or weights)."""
    action_logits: list[float]   # len = action_space_n
    step_count: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)

class GRPOPolicyAgent:
    """Discrete-action policy trainable via group-relative advantages."""

    def __init__(
        self,
        *,
        agent_id: str,
        action_space_n: int,
        seed: int = 42,
        initial_logits: list[float] | None = None,
    ): ...

    def act(self, observation: dict[str, float], info: dict[str, Any]) -> int:
        """Deterministic or seeded stochastic action index."""

    def snapshot(self) -> PolicyState: ...
    def load_snapshot(self, state: PolicyState) -> None: ...

    def update_from_group_advantages(
        self,
        trajectories: list["TrajectoryRecord"],
        *,
        ranked: list[CandidateRun],
        learning_rate: float = 0.05,
    ) -> dict[str, float]:
        """
        Use group-relative ranks from grpo_experiment to nudge action logits.
        Must be deterministic given seed + same inputs.
        Return training.* metrics (e.g. training.policy_delta_norm).
        """
```

规则：
- **不依赖** torch 作为硬依赖；可用 numpy-free 纯 Python float 列表。
- act() 输入 observation 键与 TradingEnv 一致（position_weight, last_return 等）。
- update 后 `step_count += 1`；metrics **不得**含 `oos.*`。

### 3. training_loop.py

```python
@dataclass(frozen=True)
class TrajectoryRecord:
    agent_id: str
    window_id: int
    action_indices: list[int]
    rewards: list[float]
    episode_reward: float
    metrics: dict[str, float]   # simulation.sharpe, simulation.total_return, ...

@dataclass(frozen=True)
class TrainingRunResult:
    algorithm: str
    metrics: dict[str, Any]     # simulation.*, training.*, summary.*
    policy_state: PolicyState
    artifacts: dict[str, str]

class RLTrainingLoop:
    def __init__(
        self,
        *,
        env: TradingEnv,
        policy: GRPOPolicyAgent,
        config: dict[str, Any],
        risk_agent: RiskAgent | None = None,
    ): ...

    def run(
        self,
        *,
        max_steps: int = 10,
        n_groups: int = 2,
        rollouts_per_group: int = 2,
        seed: int = 42,
    ) -> TrainingRunResult:
        """
        1. For each group/window: collect rollouts (self-policy + optional baseline candidates).
        2. Build CandidateRun list → rank_candidates_by_group_relative_reward.
        3. policy.update_from_group_advantages(...).
        4. Aggregate simulation.* episode metrics.
        """

    def save_checkpoint(self, output_dir: Path) -> dict[str, str]: ...
    def export_strategy_candidate_stub(self) -> dict[str, Any]:
        """Return stub dict explaining M11.6 bridge; no oos.*."""

def schedule_walk_forward_eval_stub(**kwargs) -> dict[str, str]:
    """Document-only hook pointing to validate_candidate_oos.py; return empty artifacts."""
```

行为：
- 每步通过 RiskAgent 裁剪 env 内 target weight（复用 TradingEnv 已有 risk 或显式 RiskAgent.propose 路径）。
- `run()` 在 mock 配置下 **≤10 steps** 必 finish，不 hang。
- checkpoint：`outputs/rl_training/<experiment_name>/policy_state.json`、`metrics.json`、`summary.md`。
- summary.md **必须**含 `simulation_only: true` 与 baseline experiment id **EXP-20260602-008**。

### 4. ppo_trainer.py

```python
class TrainerProtocol(Protocol):
    def train_step(self, batch: list[TrajectoryRecord]) -> dict[str, float]: ...

class PPOTrainer:
    """Stub trainer — records training.ppo_stub=true, optional mock loss."""

    def train_step(self, batch: list[TrajectoryRecord]) -> dict[str, float]:
        return {"training.ppo_stub": 1.0, "training.loss": 0.0}
```

`RLTrainingLoop` 在 `algorithm=ppo` 时调用 PPOTrainer；pytest 断言 stub metrics 存在。

### 5. marl_stub.py（或 training_loop 内文档化 Protocol）

```python
class MultiAgentTrainingProtocol(Protocol):
    """CTDE / league training extension point for M13+."""

    def train_joint(self, agents: list[Any], env: Any) -> dict[str, Any]: ...


class MARLTrainingStub:
    def train_joint(self, agents, env) -> dict[str, Any]:
        raise NotImplementedError("MARL training is reserved for a future milestone")
```

pytest：调用 stub 预期 `NotImplementedError` 或返回 `{"training.marl_stub": true}`（二选一，文档写明）。

### 6. configs/rl_training.yaml

```yaml
rl_training:
  simulation_only: true
  algorithm: grpo          # grpo | ppo
  max_steps: 10
  n_groups: 2
  rollouts_per_group: 2
  learning_rate: 0.05
  seed: 42
  baseline_experiment_id: EXP-20260602-008
  baseline_oos_sharpe: 0.586

env:
  initial_cash: 100000.0
  action_levels: [0.0, 0.25, 0.5, 1.0]
  max_steps: 32            # per-episode cap in training

paths:
  market_data: null        # null → synthetic in dry-run
  output_dir: outputs/rl_training

experiment:
  name: rl_training_grpo_001
  family: rl_training
  memory_path: null

walk_forward_eval:
  enabled: false           # M12 第一版禁止 true；stub only
  note: "Use scripts/validate_candidate_oos.py after StrategyCandidate export"
```

### 7. scripts/run_rl_experiment.py

CLI：
- `--config configs/rl_training.yaml`
- `--algorithm grpo|ppo`（覆盖 yaml）
- `--market-data-path`（可选；缺省 + dry-run → synthetic）
- `--max-steps`、`--seed`、`--output-dir`、`--memory-path`
- `--dry-run`（默认 true 或 argparse BooleanOptionalAction）
- `--help`

行为：
- dry-run：stdout JSON summary，**不写** ExperimentMemory。
- `--no-dry-run`：写 checkpoint + ExperimentMemory（family=`rl_training`）。
- metrics 含 `summary.baseline_oos_sharpe`、`summary.simulation_only=true`；**无** `oos.sharpe`。
- 不调用 broker；不 import LLM。

### 8. docs/rl_experiment.md

必含章节：
1. M12 定位（M7 ranking → M12 training loop）
2. 指标族：`training.*`、`simulation.*` vs `oos.*` vs `population.*`
3. 与 **EXP-20260602-008（0.586）** 关系：训练后若需 OOS，走 M11.6 export → M11.7 validate
4. GRPO vs PPO vs MARL stub 边界
5. CLI 示例与 pytest 基线
6. 服务器 GPU smoke 建议（**不在 pytest**）：`--max-steps 50` 可选，记录 EXP-RL-003

### 9. tests/test_rl_training.py（≥12 项）

全部 synthetic，**不联网、不用 GPU**：

1. GRPOPolicyAgent act 返回合法 action index
2. act 确定性（固定 seed）
3. update_from_group_advantages 改变 logits（或 step_count 递增）
4. PolicyState snapshot round-trip
5. RLTrainingLoop.run max_steps=10 不 crash
6. run 产出 metrics 含 `simulation.*` 或 `training.*`
7. run 产出 **不含** `oos.sharpe` / `oos.total_return`
8. rank 集成：mock trajectories → 使用 grpo_experiment 排序
9. save_checkpoint 写入 policy_state.json + metrics.json
10. PPOTrainer stub train_step 返回 stub metrics
11. MARLTrainingStub 行为符合文档
12. export_strategy_candidate_stub / walk_forward stub 不写 oos.*
13. run_rl_experiment.py --help
14. run_rl_experiment dry-run CLI（subprocess 或 调用 main）
15. non-dry-run 写 ExperimentMemory（tmp path）
16. 全量 pytest 266+ 仍通过（test 内可只断言本文件；全量在验收命令跑）

## 兼容性要求

- **不得修改** walk_forward.py、candidate_validation.py 默认行为
- **不得**让 Supervisor / LLM 直接调用训练 loop 下单
- ExperimentMemory 新 run：`params["family"]="rl_training"`；metrics 禁止 `oos.*`
- 复用 `rank_candidates_by_group_relative_reward`，**不要**复制粘贴改语义
- M11 Population Elo **不等于** M12 训练 loss；两者 metrics 分开

## 禁止

- 连接 broker / 实盘 API
- pytest 中 multi-hour / GPU 训练
- 用 training simulation sharpe **替代** walk-forward OOS 写论文主结论
- 在 M12 训练代码内写 `oos.*`（包括 `oos.sharpe`）
- future feature / label 进入 observation
- commit 大 checkpoint、`.env`、W&B key

## 验收命令

python -m pytest tests/test_rl_training.py -v
python -m pytest tests/test_trading_env.py tests/test_grpo_experiment.py -v   # M7 回归
python -m pytest -v                                                           # 全量 266+ passed
python scripts/run_rl_experiment.py --help
python scripts/run_rl_experiment.py --config configs/rl_training.yaml --algorithm grpo --dry-run
python scripts/run_rl_experiment.py --config configs/rl_training.yaml --algorithm ppo --max-steps 10 --dry-run

预期：全量 pytest 从 **266** 增加到约 **278+**（+12 左右）。
```

---

## Cursor 后续（Codex 完成后）

1. 创建/对齐 `docs/rl_experiment.md` 与实现对齐
2. 更新 `docs/rl_plan.md` — M12 训练 loop 小节
3. 更新 `docs/experiment_log.md` — **EXP-20260602-034**（本地）、**EXP-RL-003** / **EXP-POP-007**（服务器 smoke 模板）
4. 更新 `docs/progress.md` / `项目进度.md` / `项目v3设计.md` — M12 状态
5. 更新 `docs/architecture.md` — RL Training Layer
6. 更新 `docs/server_commands.md` — §6.19 M12 命令块
7. 更新 `docs/index.md` — 链到 `codex_prompt_M12.md` / `rl_experiment.md`
8. 服务器（可选）：`run_rl_experiment.py --no-dry-run --max-steps 50` GPU smoke，**仍 simulation only**

**科研说明**：训练 metrics 为 `simulation.*` / `training.*`；主 baseline 仍为 walk-forward **oos.sharpe 0.586**。若训练策略要进 ablation OOS 表，须走 M11.6 → M11.7/M11.8，**不得**跳过 walk-forward hook。

---

## 参考现有代码

| 模块 | 路径 |
|------|------|
| TradingEnv | `src/quant_mas/rl/trading_env.py` |
| GRPO ranking（复用） | `src/quant_mas/rl/grpo_experiment.py` |
| Baseline policies | `src/quant_mas/rl/baseline_policy.py` |
| Competitive / Population | `src/quant_mas/rl/competitive_runner.py`、`population_training.py` |
| StrategyAgent | `src/quant_mas/agents/strategy_agent.py` |
| RiskAgent | `src/quant_mas/agents/risk_agent.py` |
| Candidate OOS（勿改） | `src/quant_mas/research/candidate_validation.py` |
| M7 CLI | `scripts/run_rl_baseline.py` |
| M11 CLI | `scripts/run_competitive_experiment.py`、`run_population_training.py` |

---

## 与 M7 / M11 / M11.7 的关系

| 模块 | 用途 | 指标 |
|------|------|------|
| **M7** | TradingEnv + baseline + **GRPO ranking** | `simulation.*` |
| **M11** | Population / Elo / 多 agent mock 竞争 | `population.*`、`simulation.*` |
| **M11.7–M11.8** | StrategyCandidate **walk-forward OOS** | `oos.*`（ablation） |
| **M12** | **GRPO/PPO 训练 loop** + checkpoint | `training.*`、`simulation.*` |
| **论文主指标** | ML LightGBM walk-forward | **oos.sharpe 0.586**（EXP-008） |

推荐叙事链路（论文 ablation，非 M12 自动完成）：

```text
M12 GRPO train (simulation)
  → export StrategyCandidate stub / 手工映射为 mean_reversion 参数
  → M11.7 validate_candidate_oos
  → 与 0.586 对比（机制分析，非主 baseline 替代）
```

---

## 实验编号（验收后写入 experiment_log）

| 编号 | 内容 |
|------|------|
| **EXP-20260602-034** | M12 本地 pytest + GRPO training loop mock（**278+ passed** 预期） |
| **EXP-RL-003** | 本地/服务器 `run_rl_experiment.py --dry-run` + `--no-dry-run` smoke |
| **EXP-POP-007** | 服务器 pytest 回归 + 可选 GPU `--max-steps 50`（simulation only） |
| （可选科研） | 训练策略 → StrategyCandidate → M11.7 OOS vs **0.586** — **Cursor 科研任务**，非 M12 第一版必做 |

论文主指标仍为 **EXP-20260602-008**（oos.sharpe **0.586**）。

---

## Agent / 算法路线图（M12 第一版 vs 后续）

| 组件 | M12 第一版 | 后续 |
|------|------------|------|
| GRPOPolicyAgent | ✅ tabular logits + group-relative update | 神经网络 policy（optional torch extra） |
| PPOTrainer | ✅ stub only | 真实 PPO / SB3 适配层 |
| MARL | ✅ Protocol + stub | CTDE、league 联合训练 |
| Walk-forward eval | ✅ stub 指向 M11.7 | 自动化 export + validate |
| GPU 训练 | 📋 服务器 smoke 文档 | 长 horizon、真实 features |

---

## 服务器 smoke 模板（Codex 完成后人工跑，不写进 pytest）

```bash
cd /mnt/localDisk3/weizian/Quant-MAS
conda activate /mnt/localDisk3/weizian/conda_envs/quant-mas
git pull origin main

python -m pytest -v                                    # 预期 278+ passed
python scripts/run_rl_experiment.py \
  --config configs/rl_training.yaml \
  --algorithm grpo \
  --max-steps 10 \
  --dry-run

python scripts/run_rl_experiment.py \
  --config configs/rl_training.yaml \
  --algorithm grpo \
  --max-steps 50 \
  --no-dry-run
```

记录为 **EXP-POP-007** / **EXP-RL-003**；metrics 仍 **simulation only**。
