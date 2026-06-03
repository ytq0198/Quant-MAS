# Plus v3 M11：竞争学习 / 策略种群 — Codex 提示词

**状态：✅ 已完成（M11 EXP-029/POP-002 + M11.5 EXP-030/POP-003 + M11.6 EXP-031，248 passed 本地，2026-06-03）**

更新时间：2026-06-03

> **用法**：先粘贴下方「固定前缀」，再粘贴「M11 主任务」整段交给 Codex。  
> **设计依据**：[项目v3设计.md §M11](../项目v3设计.md#m11竞争学习--自博弈--策略种群) · 配套：新建 `docs/competitive_learning.md` · 前置：**M1–M8 ✅**、**M9/M10 ✅**（212 pytest，EXP-026 + EXP-LLM-002）· **M11.5** 见 [population_training.md](population_training.md)（237 pytest，EXP-030/POP-003）

---

## 固定前缀（每次必贴）

```
你正在开发 Quant MAS 科研项目（v3 阶段）。
路径：D:\scientific reasearch and work\SRTP\Quant MAS

测试基线：本地 **248 passed**（v3 M11.6，EXP-20260602-031）；M11.5 双端 **237**（EXP-POP-003）。
OOS 主 baseline：EXP-20260602-008，oos.sharpe **0.586**（walk-forward，19 窗）。
M6 text OOS exploratory：EXP-TEXT-WF-001，oos.sharpe **0.563** vs baseline **0.586**（不可替代主指标）。
M7 RL：simulation only；`simulation.*` / Population Elo **不得**与 `oos.*` 混比或替代论文主指标。
M9/M10：Postgres/pgvector（EXP-026）、local_vllm（EXP-LLM-002）已完成；M11 **不依赖**真实 DB/vLLM。

硬性原则：
1. **simulation / population only** — 不接 broker、不下实盘单、LLM **不直接**输出 target_weight 绕过 RiskAgent。
2. Population **Elo**、episode sharpe、group-relative reward 均为 **辅助研究指标**；ExperimentMemory 用 `population.*` / `simulation.*` 命名，**禁止**写入 `oos.sharpe` 除非走真实 walk_forward 评估 hook（第一版仅 mock/stub）。
3. 所有 StrategyAgent 的 `propose()` 输出 target_weight **必须**经 RiskAgent（或 `check_position_limits`）裁剪后再进入 env。
4. pytest **不联网、不跑长训练、不依赖 GPU**；synthetic OHLCV + 2～5 个 mock agent + 确定性 Elo。
5. **禁止 future leakage**：观测与 M7 TradingEnv 一致，仅 `t` 及之前信息。
6. 请只实现当前 **M11** 一个模块；改完后 `python -m pytest -v` 全量通过（M11 基线 225+；含 M11.5 后 **237**，增量在 `tests/test_population_training_loop.py`）。
7. **不得破坏** M7 现有 `TradingEnv` / `run_rl_baseline.py` / `test_trading_env.py` 行为（向后兼容）。
8. 禁止 commit `.env`、API key、大 checkpoint。
9. 新实验 family 建议：`competitive_learning` 或 `population_simulation`；与 `walk_forward` 族别分离。
10. 论文主指标仍为 walk-forward OOS；Population 排名 **不等于** OOS 0.586。
```

---

## M11 主任务（复制给 Codex）

```
请为 Quant MAS v3 实现 **M11：竞争学习 / 自博弈 / 策略种群**（mock-first，与 M12 训练 loop 解耦）。

## 背景

v2 / v3 已有：
- rl/trading_env.py — 单 agent 离散仓位 TradingEnv（下一 bar open 成交，与 BacktestEngine 一致）
- rl/baseline_policy.py — Random / BuyAndHold / MLCopy
- rl/grpo_experiment.py — CandidateRun + rank_candidates_by_group_relative_reward（group-relative，tie-break 按 name）
- rl/mock_data.py — build_synthetic_ohlcv、build_synthetic_ml_signals
- rl/reward.py — step reward + episode metrics
- risk/limits.py、check_position_limits — RiskTool 同源逻辑
- research/baseline.py — BaselineRegistry、compare 表
- memory/experiment_memory.py — JSON ExperimentMemory；factory 支持 postgres（pytest 仍 mock）
- scripts/run_rl_baseline.py — 单 policy 单 episode dry-run
- tests/test_trading_env.py、tests/test_grpo_experiment.py — M7 全绿

M11 **尚无**：
- 多 StrategyAgent 同场 propose / evaluate
- PopulationManager + Elo + Top-K + autocurriculum 骨架
- Multi-agent env 或等价编排
- run_competitive_experiment.py CLI

M11 目标（第一版）：
1. **StrategyAgent 抽象** — `propose()` → target_weight；`evaluate()` → episode metrics；至少 **2 个**可运行子类（Momentum + MeanReversion，或 Momentum + MLSignal mock）。
2. **RiskAgent** — 对 propose 结果做 position/drawdown 裁剪（复用 risk 模块，非 LLM）。
3. **PopulationManager** — 注册 agent、按 window/episode 收集 score、**Elo 更新**、Top-K 保留、autocurriculum 下一代候选（参数 mutate 骨架即可）。
4. **Multi-agent 编排** — 新 `MultiAgentTradingEnv` 或 `CompetitiveEpisodeRunner`（推荐独立文件，**不破坏**单 agent TradingEnv API）。
5. **CLI** — `scripts/run_competitive_experiment.py`（`--mode mock` 默认、`--dry-run`、写 ExperimentMemory + metrics.json）。
6. **文档** — `docs/competitive_learning.md`（指标族别、与 OOS 0.586 关系、M12 衔接）。
7. **测试** — `tests/test_population_training.py`（≥12 项 mock smoke）。

第一版**不做**：真实 walk-forward 19 窗全量跑数、神经网络 MARL 训练（留 M12）、LLM 策略 agent、Neo4j 图写入、pytest 连 Postgres。

## 需要实现的文件

### 1. 包结构

src/quant_mas/agents/
  strategy_agent.py       # StrategyAgent ABC + MomentumAgent + MeanReversionAgent（+ 可选 MLSignalAgent mock）
  population_manager.py   # PopulationManager, AgentSpec, EloState, GenerationResult
  risk_agent.py           # RiskAgent — clip/veto target_weight（thin wrapper over risk.limits）

src/quant_mas/rl/
  competitive_runner.py   # CompetitiveEpisodeRunner — 多 agent × 多 window mock 编排
  elo_rating.py             # update_elo, initial_rating, deterministic tie-break（可复用 grpo 风格）

configs/competitive.yaml

scripts/run_competitive_experiment.py

docs/competitive_learning.md

tests/test_population_training.py   # ≥12 项

增量更新（小改即可）：
- src/quant_mas/agents/__init__.py — export 新类
- src/quant_mas/rl/__init__.py — export CompetitiveEpisodeRunner（若公开）

### 2. strategy_agent.py

```python
@dataclass(frozen=True)
class AgentProposal:
    agent_id: str
    target_weight: float
    confidence: float = 1.0
    metadata: dict[str, Any] = field(default_factory=dict)

@dataclass(frozen=True)
class AgentEvaluation:
    agent_id: str
    metrics: dict[str, float]   # simulation.sharpe, simulation.total_return, ...
    reward: float
    window_id: int = 0

class StrategyAgent(ABC):
    agent_id: str
    name: str

    @abstractmethod
    def propose(self, observation: dict[str, float], info: dict[str, Any]) -> AgentProposal: ...

    def evaluate_episode(self, equity_curve: list[float], *, window_id: int = 0) -> AgentEvaluation:
        """Default: derive reward/metrics from equity curve via rl.reward.compute_episode_metrics."""
```

**MomentumAgent**（示例）：
- 读 observation 中 `last_return` 或 `ma_distance_5`（mock env 需提供键；缺则 0）
- 正动量 → 较高 target_weight；负动量 → 较低

**MeanReversionAgent**（示例）：
- 与 Momentum 相反逻辑（如 ma_distance 高 → 减仓）

**MLSignalAgent**（可选第三 agent，mock）：
- 构造时注入 synthetic signals DataFrame（复用 MLCopyPolicy 对齐逻辑），propose 最近 action_level 对应 weight
- **不**在 pytest 中训练 LightGBM

所有 agent **deterministic**（给定 seed + 相同 observation → 相同 proposal）。

### 3. risk_agent.py

```python
class RiskAgent:
    def __init__(self, limits: RiskLimits | None = None): ...

    def apply(self, proposal: AgentProposal, *, current_weight: float, equity: float) -> AgentProposal:
        """Clip target_weight via check_position_limits; record violations in metadata."""
```

禁止 bypass；violations 写入 proposal.metadata["risk_violations"]。

### 4. population_manager.py

```python
@dataclass
class AgentSpec:
    agent_id: str
    agent_type: str          # momentum | mean_reversion | ml_signal
    params: dict[str, Any]
    elo: float = 1500.0

class PopulationManager:
    def register(self, spec: AgentSpec) -> None: ...
    def record_match(self, winner_id: str, loser_id: str, *, window_id: int) -> None: ...
    def record_evaluation(self, evaluation: AgentEvaluation) -> None: ...
    def rankings(self) -> list[AgentSpec]: ...          # by elo desc, tie-break agent_id
    def top_k(self, k: int) -> list[AgentSpec]: ...
    def next_generation(self, *, mutate_sigma: float = 0.05) -> list[AgentSpec]:
        """Autocurriculum skeleton: copy top-K params + small deterministic jitter; 新 agent_id。"""
```

Elo 更新：
- 使用标准期望得分公式；`K=32` 可配置
- **同分时**按 `agent_id` 字典序（与 grpo_experiment tie-break 一致）
- 提供 `export_state() -> dict` 供 CLI / memory

与 M7 `CandidateRun` 关系：可将每 agent 每 window 的 evaluation 转为 `CandidateRun` 并调用 `rank_candidates_by_group_relative_reward` 作 **交叉验证**（可选，测试至少一种排名路径）。

### 5. rl/elo_rating.py

```python
def expected_score(rating_a: float, rating_b: float) -> float: ...
def update_elo(rating: float, expected: float, score: float, *, k: float = 32.0) -> float: ...
```

纯函数、无 IO；单元测试覆盖平局、强弱对手、确定性。

### 6. rl/competitive_runner.py

```python
@dataclass
class CompetitiveRunConfig:
    n_windows: int = 3
    bars_per_window: int = 32
    seed: int = 42
    aggregation: str = "mean"   # mean | best_elo — 第一版 mean 即可

class CompetitiveEpisodeRunner:
    def __init__(
        self,
        *,
        market_data: pd.DataFrame | None = None,
        agents: list[StrategyAgent],
        risk_agent: RiskAgent,
        population: PopulationManager,
        config: CompetitiveRunConfig,
    ): ...

    def run_mock(self) -> dict[str, Any]:
        """
        1) 将 synthetic OHLCV 切分为 n_windows（或每 window 独立 synthetic episode）
        2) 每 window：各 agent propose → risk apply → env step（共享 market path 或独立 shadow equity）
        3) evaluate_episode → record_evaluation；两两或 round-robin Elo 更新
        4) 返回 summary：rankings, top_k, simulation metrics, population.elo_top
        """
```

**实现建议**（二选一，文档说明选用方案）：
- **A（推荐）**：每 agent 独立 `TradingEnv` 实例跑同一 window 切片（简单、与 M7 兼容、易测）
- **B**：扩展 `TradingEnv` 多槽位 — 若选 B，必须保持原单 agent 构造/测试 **零回归**

Shadow equity：每个 agent 维护自己的 position/equity；**不**合并成组合实盘单。

### 7. configs/competitive.yaml

```yaml
competitive:
  simulation_only: true
  mode: mock                    # mock | walk_forward（walk_forward 第一版仅 CLI stub + NotImplemented 或 dry-run 警告）
  seed: 42
  n_windows: 3
  bars_per_window: 32
  top_k: 2
population:
  initial_elo: 1500.0
  k_factor: 32.0
  mutate_sigma: 0.05
agents:
  - id: momentum_1
    type: momentum
    params: {lookback: 5, scale: 1.0}
  - id: mean_rev_1
    type: mean_reversion
    params: {lookback: 5, scale: 1.0}
paths:
  market_data: null              # mock 时忽略
  output_dir: outputs/competitive
experiment:
  name: competitive_mock_001
  family: competitive_learning
memory:
  json_path: outputs/reports/experiments.json
baseline:
  oos_reference: EXP-20260602-008
  oos_sharpe: 0.586              # 文档对照用，勿写入 population 记录的 oos.sharpe
```

### 8. scripts/run_competitive_experiment.py

CLI：
- `--config configs/competitive.yaml`
- `--mode mock|walk_forward`（walk_forward 第一版：**stub only**，打印 warning，不虚构 OOS 数字）
- `--dry-run` — 不写 memory，只 stdout summary
- `--output-dir`、`--seed`、`--memory-path`
- `--help`

行为：
- 构建 agents + PopulationManager + CompetitiveEpisodeRunner
- `run_mock()` → 写 `output_dir/metrics.json`、`summary.md`
- 非 dry-run：追加 **ExperimentMemory** 一条记录：
  - `name`: experiment.name
  - `metrics`: `{ "population": { "elo_top": ..., "top_agent": ... }, "simulation": { "sharpe": ..., "max_drawdown": ... } }`
  - **不得**含 `oos.sharpe`（除非未来真实 walk_forward hook）
- summary.md **必须**含：`simulation_only: true`、OOS baseline 对照说明（文字，非冒充数值）

可选：调用 `BaselineRegistry.add_baseline` 生成 compare 表一行（family=`competitive_learning`）。

### 9. docs/competitive_learning.md

必含章节：
| 章节 | 内容 |
|------|------|
| 定位 | M11 population vs M7 单 policy vs M12 训练 loop |
| Agent Pool | Momentum / MeanReversion / MLSignal / TextSignal / Risk 路线图（TextSignal 可标 planned） |
| 指标族别 | `population.elo` ≠ `oos.sharpe`；论文主指标仍 EXP-20260602-008 |
| CLI | run_competitive_experiment.py 示例 |
| M12 衔接 | PopulationManager / Elo 将被 training_loop 复用 |
| 安全 | 无 broker、RiskAgent 必经 |

### 10. tests/test_population_training.py（≥12 项）

全部 synthetic，**不联网**：

1. MomentumAgent propose 确定性（固定 seed + observation）
2. MeanReversionAgent 与 Momentum 在构造用例上 proposal 不同
3. RiskAgent clip 超重 target_weight
4. Elo update：强者胜弱者 → rating 上升
5. Elo 平局 deterministic tie-break
6. PopulationManager.top_k 顺序正确
7. next_generation 产生新 agent_id，params 有 jitter 且 deterministic
8. CompetitiveEpisodeRunner.run_mock 返回 rankings
9. 2+ agents 跑完一轮后 ExperimentMemory 可写入（tmp_path json）
10. 写入记录的 metrics **不含** oos.sharpe 键（assert）
11. run_competitive_experiment.py --help
12. run_competitive_experiment.py --dry-run --mode mock 退出码 0
13. （可选）与 rank_candidates_by_group_relative_reward 集成 smoke
14. test_trading_env / test_grpo_experiment **保持通过**

## 兼容性要求

- **不得修改** walk_forward.py / BacktestEngine 默认行为
- **不得**让 SupervisorAgent 直接跑 competitive CLI 下单
- M10 ResearchAgent **不受影响**（可不注册 competitive 为 Tool，第一版不必）
- run_rl_baseline.py 行为不变
- ExperimentMemory 新 run 的 family 与 walk_forward 区分

## 禁止

- 连接 broker / 实盘 API
- pytest 中 multi-hour RL 训练或 GPU
- 将 Population Elo 或 simulation.sharpe **标注或写入**为论文 OOS 主结论
- 虚构 walk_forward OOS 数字（walk_forward mode stub 即可）
- future feature / label 进入 observation
- LLM 生成 target_weight 绕过 RiskAgent

## 验收命令

python -m pytest tests/test_population_training.py -v
python -m pytest tests/test_trading_env.py tests/test_grpo_experiment.py -v
python -m pytest -v                                    # 全量 212+ passed
python scripts/run_competitive_experiment.py --help
python scripts/run_competitive_experiment.py --config configs/competitive.yaml --mode mock --dry-run

## 预期 pytest 增量

+12～+20 项（population + competitive CLI），全量 **212 → ~230** 左右（视实现而定）。
```

---

## Cursor 后续（Codex 完成后）

1. ~~创建/对齐 `docs/competitive_learning.md` 与实现~~ ✅
2. ~~更新 `docs/architecture.md` — Competitive Learning Layer~~ ✅
3. ~~更新 `docs/experiment_log.md` — **EXP-20260602-029** / **EXP-POP-001**~~ ✅
4. ~~更新 `docs/progress.md`、`项目进度.md`、`项目v3设计.md` — M11 状态~~ ✅
5. ~~服务器 pull + pytest + `run_competitive_experiment.py --dry-run`（**EXP-POP-002**）~~ ✅
6. ~~`docs/server_commands.md` — §6.14 M11 命令块~~ ✅

**科研说明**：Population Elo、`simulation.*` 为辅助指标；主 baseline 仍为 walk-forward **oos.sharpe 0.586**。

---

## 参考现有代码

| 模块 | 路径 |
|------|------|
| TradingEnv | `src/quant_mas/rl/trading_env.py` |
| GRPO ranking | `src/quant_mas/rl/grpo_experiment.py` |
| Baseline policies | `src/quant_mas/rl/baseline_policy.py` |
| Mock OHLCV | `src/quant_mas/rl/mock_data.py` |
| Reward / episode metrics | `src/quant_mas/rl/reward.py` |
| Risk limits | `src/quant_mas/risk/limits.py` |
| BaselineRegistry | `src/quant_mas/research/baseline.py` |
| ExperimentMemory | `src/quant_mas/memory/experiment_memory.py` |
| run_rl_baseline | `scripts/run_rl_baseline.py` |
| M7 prompt（历史） | `docs/codex_prompt_M7.md` |
| M10 prompt（已完成） | `docs/codex_prompt_M10.md` |

---

## 与 M7 / M10 / M12 / M13 的关系

| 模块 | 关系 |
|------|------|
| **M7** RL 模拟 | M11 **复用** TradingEnv、reward、mock_data；扩展为多 agent 编排 |
| **M10** LLM | 无硬依赖；StrategyAgent **不是** LLM agent |
| **M12** RL 训练 | 后续复用 PopulationManager、Elo、CompetitiveEpisodeRunner |
| **M13** 编排 | 后续可将 competitive experiment 挂 LangGraph 节点 |
| **M9** 企业 DB | 可选 postgres memory；pytest 仍 json mock |

---

## Agent Pool 路线图（第一版 vs 后续）

| Agent | M11 第一版 | 说明 |
|-------|------------|------|
| MomentumAgent | ✅ 必做 | OHLCV 特征 → weight |
| MeanReversionAgent | ✅ 必做 | 与 Momentum 对照 |
| MLSignalAgent | 可选 mock | synthetic signals，不训练 LGBM |
| TextSignalAgent | 📋 stub/文档 | 读 text_signals 列；完整版随 EXP-TEXT-WF-002 |
| RiskAgent | ✅ 必做 | 裁剪 propose，非策略竞争者 |

---

## 实验编号（验收后写入 experiment_log）

| 编号 | 内容 |
|------|------|
| **EXP-20260602-029** | M11 本地 pytest + population mock | ✅ **225 passed**（population 13/13） |
| **EXP-POP-001** | competitive `--mode mock --dry-run` 本地 | ✅ |
| **EXP-POP-002** | 服务器 competitive dry-run | ✅ **225 passed** + dry-run（17.32s @ `64a5b2a`） |
| **EXP-20260602-030** | M11.5 本地 population training loop | ✅ **237 passed**（loop 12/12） |
| **EXP-POP-003** | 服务器 population training dry-run | ✅ **237 passed** + 3-gen dry-run（41.83s @ `aa841d4`） |
| **EXP-20260602-031** | M11.6 本地 candidate bridge | ✅ **248 passed**（bridge 11/11） |
| **EXP-POP-004** | 服务器 candidate export dry-run | 📋 待做 |
| （未来） | `--mode walk_forward` 真实 OOS 与 **0.586** 对照 — **Cursor 科研任务**，Codex 仅 stub |

论文主指标仍为 **EXP-20260602-008**（oos.sharpe **0.586**）。

**M11.6 补充（2026-06-03）**：`StrategyCandidate` + `candidate_bridge` + `export_population_candidates.py` — 见 [strategy_candidate_bridge.md](strategy_candidate_bridge.md)。
