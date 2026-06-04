# Quant MAS 实验记录

更新时间：2026-06-04（v3 M11.8 ✅ **266 双端 + EXP-POP-006 批量 OOS**）

本文件用于记录真实实验和重要验证。不要记录未经实际运行的数据结果；尚未真实运行的项目标记为「待验证」。

## OOS 主 baseline（全文引用）

**EXP-20260602-008** 为 Walk-forward 样本外主 baseline。**后续所有研究结论必须与此对比**；单段 ML 回测（如 EXP-20260602-005 sharpe 2.78）**不得**作为论文主指标。

| 字段 | 值 | 来源 |
|------|-----|------|
| 实验编号 | EXP-20260602-008 | 已验证 |
| 是否 OOS | **是**（19 窗 walk-forward） | 已验证 |
| **oos.sharpe** | **0.586** | 已验证 |
| oos.total_return | 0.443 | 已验证 |
| oos.max_drawdown | -0.255 | 已验证 |
| oos.auc_mean | 0.472 | 已验证 |
| 产物 | `outputs/reports/walk_forward_latest/` | 服务器 |

## 实验比较表

> 由 `scripts/compare_experiments.py` 从 ExperimentMemory 自动生成；下表为**手工维护的快照**，与 CLI 输出应对齐。  
> **规则**：缺失指标留空，**禁止猜测**；未跑过的实验标「待验证」。

### 比较表模板（复制用于新快照）

```markdown
### 快照：COMP-YYYYMMDD-001

- 生成方式：`python scripts/compare_experiments.py --output-dir outputs/research`
- Memory 路径：（填写 experiments.json 路径）
- 对照 baseline：**EXP-20260602-008**（OOS sharpe **0.586**）
- 主指标列：`oos.sharpe`（论文结论唯一依据）

| run_id / name | family | is_oos | sharpe | oos.sharpe | total_return | oos.total_return | max_drawdown | test_auc | vs OOS baseline | 备注 |
|---------------|--------|--------|--------|------------|--------------|------------------|--------------|----------|-----------------|------|
| （填写） | ma_cross / lightgbm / ml_backtest / walk_forward / other | 是/否 | | | | | | | ↑/↓/≈ / 待验证 | |
```

### 当前快照：COMP-20260603-001（text walk-forward，**6 rows**）

- 生成：`python scripts/compare_experiments.py --storage-config configs/storage.server.yaml --memory-path /mnt/localDisk3/weizian/reports/experiments.json --output-dir /mnt/localDisk3/weizian/reports/research`
- Memory：`/mnt/localDisk3/weizian/reports/experiments.json`
- 对照 baseline：**EXP-20260602-008**，`oos.sharpe = 0.586`

| name | family | sharpe | oos.sharpe | total_return | oos.total_return | max_drawdown | test_auc | vs OOS baseline | 备注 |
|------|--------|--------|------------|--------------|------------------|--------------|----------|-----------------|------|
| server_ma_cross_real_001 | ma_cross | 1.001 | — | 2.025 | — | -0.206 | — | 不可直接比 OOS | EXP-20260601-004 |
| server_lgbm_001 | lightgbm | — | — | — | — | — | 0.466 | 不可直接比 OOS | EXP-20260601-006 |
| server_lgbm_gpu_001 | lightgbm | — | — | — | — | — | 0.479 | 不可直接比 OOS | EXP-20260602-004 |
| server_ml_backtest_001 | ml_backtest | **2.781** | — | 68.27 | — | -0.246 | — | ⚠️ in-sample | EXP-20260602-005 |
| server_walk_forward_001 | walk_forward | — | **0.586** | — | 0.443 | — | — | **baseline** | EXP-20260602-008 |
| server_walk_forward_text_001 | walk_forward | — | **0.563** | — | 0.420 | — | — | ↓ -0.023 | EXP-TEXT-WF-001 |

**说明：**

- CLI 输出 `oos.sharpe` 精确值 **0.585673** ≈ 报告 **0.586**，与 EXP-20260602-008 一致。
- 仅 **walk_forward** 行可用于论文主结论。
- EXP-TEXT-WF-001：200/6033 text 覆盖 + fillna(0)，**exploratory**；Δ oos.sharpe **-0.023**。
- 产物：`/mnt/localDisk3/weizian/reports/research/comparison.md`

### 历史快照：COMP-20260602-002（5 rows，EXP-20260602-010，text 实验前）

## 实验记录模板

复制以下块追加到「当前验证记录」或「待验证实验」。**禁止**填写未运行结果的 metrics；API key 不得入库。

### 通用模板（工程 / pytest / CLI）

```markdown
## 实验编号：EXP-YYYYMMDD-NNN

- 日期：
- 阶段：（Prompt / Plus M1–M8）
- 环境：（本地 Windows / 服务器 a6000-9961；Python；git commit）
- 命令：
  ```bash
  # 粘贴实际命令
  ```
- 结果摘要：
- 指标：（仅填已验证数值；OOS 须标注 is_oos=是）
- 产物路径：
- 问题：
- 下一步：
```

### Walk-forward / 论文主指标模板

```markdown
## 实验编号：EXP-YYYYMMDD-NNN

- 日期：
- 阶段：Walk-forward OOS
- 数据：`features.parquet` 路径与行数
- 配置：`configs/walk_forward.yaml` 窗口参数
- 参数：`--experiment-name`、device
- **OOS 指标**（论文唯一主指标）：
  - oos.sharpe：
  - oos.total_return：
  - oos.max_drawdown：
  - window_count：
- 与 baseline 对比：**EXP-20260602-008** oos.sharpe **0.586** → ↑/↓/≈
- 产物：`metrics.json`、`summary.md`、`windows.csv`
- 问题：
- 下一步：
```

### LLM / ResearchAgent smoke 模板（不写 key）

```markdown
## 实验编号：EXP-LLM-NNN

- 日期：
- 阶段：Plus M5
- 环境：`llm_provider`（mock / openai_compatible）
- 命令：`run_research_agent.py --use-llm ...`
- 结果摘要：（baseline 是否命中、RAG 命中文件、latency 可选）
- **禁止记录**：API key、完整 prompt 中的 secrets
- 下一步：
```

### 文本模型 smoke 模板（FinBERT / LoRA）

```markdown
## 实验编号：EXP-TEXT-NNN

- 日期：
- 阶段：Plus M6
- 模式：mock / finbert_baseline / lora
- 文本来源：（jsonl 路径、条数、是否 synthetic）
- 产物：`signals.parquet`、`metadata.json`
- 是否加载真实 HF 权重：是 / 否
- walk-forward 对比 baseline：**待验证 / 已对比 0.586**
- 问题：
- 下一步：
```

### 比较表快照模板

```markdown
### 快照：COMP-YYYYMMDD-001

- 生成：`python scripts/compare_experiments.py --storage-config ... --output-dir ...`
- Memory 路径：
- 对照 baseline：**EXP-20260602-008**（OOS sharpe **0.586**）

| name | family | is_oos | oos.sharpe | vs baseline | 备注 |
|------|--------|--------|------------|-------------|------|
| | walk_forward / ml_backtest / ... | 是/否 | | ↑/↓/≈ | |
```

### 历史简短模板（兼容旧记录）

```markdown
## 实验编号：EXP-YYYYMMDD-001

- 日期：
- 阶段：
- 数据：
- 策略 / 模型：
- 参数：
- 指标：
  - total_return：
  - sharpe：
  - max_drawdown：
  - final_equity：
  - 其他：
- 产物路径：
  - metrics：
  - equity_curve：
  - trades：
  - summary：
  - model：
- 问题：
- 下一步：
```

## 当前验证记录

### EXP-POP-006：v3 M11.8 服务器批量候选 OOS ✅

- 日期：2026-06-04
- 阶段：**M11.8** 服务器 @ **`9477c3d`**
- 环境：a6000-9961；conda `quant-mas`；Python **3.11.15**
- 数据：`/mnt/localDisk3/weizian/datasets/features/features.parquet`；Top-4 mean_reversion 候选（export `--top-k 5` 实际产出 4 条）
- 命令与结果：
  - `python -m pytest -v` → **266 passed** in **45.63s** ✅
  - `export_population_candidates.py ... --top-k 5 --no-dry-run` → ✅（`f9030c6adbf94db5a5a4cb4a189eb9cb`）
  - `batch_validate_candidates.py ... --top-k 5 --no-dry-run` → ✅
- **批量 OOS 比较表**（77 windows；baseline **0.586**）：

| OOS Rank | Candidate | scale | oos.sharpe | vs baseline | exceeds |
|----------|-----------|-------|------------|-------------|---------|
| 1 | `cand_mean_rev_1_g1_1_g2_2` | 1.03 | **1.039** | +0.453 | ✅ |
| 2 | `cand_mean_rev_1_g2_1` | 1.015 | **1.037** | +0.451 | ✅ |
| 3 | `cand_mean_rev_1_g1_1` | 1.01 | **1.037** | +0.451 | ✅ |
| 4 | `cand_mean_rev_1` | 1.0 | **1.036** | +0.450 | ✅ |

- 汇总：`best_oos_sharpe` **1.039**；`exceeds_baseline_count` **4/4**；Population 输入 rank 与 OOS rank **不一致**（scale 微调在 OOS 上略优）
- 与 EXP-POP-005：`cand_mean_rev_1` **1.036** vs 本次 **1.036**（一致，四舍五入）
- **科研边界**：规则型 Population 候选 OOS，用于 **ablation / 竞争学习机制**；论文主指标仍为 **EXP-20260602-008** `oos.sharpe = 0.586`
- 产物：`outputs/candidate_oos_batch/candidate_oos_comparison.csv` / `.md`；ExperimentMemory `family=strategy_candidate_oos_batch`
- 问题：无
- 下一步：**M12** RL 训练；EXP-TEXT-WF-002；论文 ablation 表可引用上表

### EXP-20260602-033：v3 M11.8 批量候选 OOS 本地验证 ✅

- 日期：2026-06-04
- 阶段：**M11.8** — 批量复用 M11.7 `run_candidate_walk_forward`，Top-K / 显式 ID 子集
- 环境：本地
- 交付：
  - `research/candidate_validation.py` — `run_candidate_batch_walk_forward`、`save_candidate_batch_validation_report`
  - `scripts/batch_validate_candidates.py`、`configs/candidate_oos.yaml`（复用）
  - `docs/candidate_oos_batch.md`、`tests/test_candidate_oos_batch.py` — **7** 项
  - `项目v3设计.md` — v3-3e 行更新
- 命令与结果：
  - `python scripts/batch_validate_candidates.py --help` → ✅
  - `python -m pytest tests/test_candidate_oos_batch.py -v` → **7 passed**
  - `python -m pytest tests/test_strategy_candidate_bridge.py tests/test_candidate_oos_validation.py tests/test_candidate_oos_batch.py -v` → **29 passed**
  - 全量 `python -m pytest -v` → **266 passed**（259→266，+7）
- 边界：无 LLM / 网络 / 模型训练 / broker；仅 batch M11.7 OOS；Memory `family=strategy_candidate_oos_batch`
- 问题：无
- 下一步：~~服务器 EXP-POP-006~~ ✅；**M12** RL 训练；EXP-TEXT-WF-002

### EXP-POP-005：v3 M11.7 服务器 candidate Walk-forward OOS ✅

- 日期：2026-06-04
- 阶段：**M11.7** 服务器 @ **`ffef849`**（label 列 fix）+ candidate export
- 环境：a6000-9961；conda `quant-mas`；Python **3.11.15**
- 数据：`/mnt/localDisk3/weizian/datasets/features/features.parquet`；候选 `cand_mean_rev_1`（mean_reversion）
- 命令与结果：
  - `python -m pytest -v` → **259 passed** in **48.32s** ✅
  - `export_population_candidates.py ... --no-dry-run` → ✅（`c1e96fbebbb9413bb52bad6239f0bfc2`）
  - `validate_candidate_oos.py ... --dry-run` → ✅
  - `validate_candidate_oos.py ... --no-dry-run` → ✅（artifacts + ExperimentMemory）
- **OOS 结果**（77 windows，2019-07-05 → 2025-12-08）：
  - `oos.sharpe`: **1.036**
  - `oos.total_return`: **1.363**；`max_drawdown`: **-0.169**
  - `summary.baseline_oos_sharpe`: **0.586**（EXP-20260602-008，ML walk-forward）
  - `summary.vs_baseline_sharpe`: **+0.450**
- **科研边界**：
  - 此为 **Population 导出的规则型 mean-reversion 候选** OOS，**不是** ML LightGBM 主 baseline 的复现或替代
  - 论文主指标仍为 **EXP-20260602-008** `oos.sharpe = 0.586`；候选 OOS 用于竞争学习链路闭环对照
  - M11.6 `backtest.sharpe` ≈ 12.99 仍为 synthetic smoke，**≠** 本 OOS
- 问题：无（`future_*` label 列已通过 `ffef849` 在信号前 drop）
- 下一步：~~M11.8 批量 OOS~~ → **EXP-POP-006**；M12 RL 训练；EXP-TEXT-WF-002

### EXP-20260602-032：v3 M11.7 StrategyCandidate Walk-forward OOS 本地验证 ✅

- 日期：2026-06-03
- 阶段：**M11.7** — 候选策略 walk-forward OOS hook（mock-first，synthetic features）
- 环境：本地
- 交付：
  - `research/candidate_validation.py` — `CandidateStrategyAdapter`、`run_candidate_walk_forward`、`save_candidate_validation_report`
  - `scripts/validate_candidate_oos.py`、`configs/candidate_oos.yaml`
  - `docs/strategy_candidate_oos.md`、`tests/test_candidate_oos_validation.py` — **11** 项
- 设计：复用 `build_walk_forward_windows` + `BacktestEngine`；**不修改** ML `walk_forward.py`
- 命令与结果：
  - `python -m pytest tests/test_candidate_oos_validation.py -v` → **11 passed**
  - `python -m pytest tests/test_strategy_candidate_bridge.py tests/test_candidate_oos_validation.py -v` → **22 passed**
  - `python scripts/validate_candidate_oos.py --help` → 正常
  - 全量 `python -m pytest -v` → **259 passed**（248→259，+11）
- 边界：M11.6 不写 `oos.*`；**M11.7 才允许** walk-forward 产出 `oos.*`；无 broker / LLM / 网络 / 模型训练；信号禁止 `future_*`
- metrics 含 `summary.baseline_oos_sharpe`（0.586）、`summary.vs_baseline_sharpe`
- 问题：无
- 下一步：~~服务器 pytest~~ ✅ EXP-POP-005（259）；完成 export `--no-dry-run` + 真实 OOS vs **0.586**

### EXP-POP-004：v3 M11.6 服务器 pytest + candidate export dry-run ✅

- 日期：2026-06-03
- 阶段：**M11.6** 服务器 pull @ **`7ab510f`**
- 环境：a6000-9961；conda `quant-mas`；Python **3.11.15**
- 命令与结果：
  - `python -m pytest tests/test_strategy_candidate_bridge.py -v` → **11 passed** in **2.48s**
  - `python -m pytest -v` → **248 passed** in **55.15s**
  - `python scripts/export_population_candidates.py --population-config configs/population_training.yaml --top-k 2 --run-backtest-smoke --dry-run` → ✅
    - Top-2：`cand_mean_rev_1`（scale 1.0）、`cand_mean_rev_1_g1_1`（scale 1.01）
    - `selection_metrics`：`population.*` / `simulation.*`（sharpe_mean ≈ **7.15**）
    - `validation_metrics`：`backtest.*`（如 sharpe ≈ **12.99**，synthetic smoke，**≠** OOS **0.586**）
    - `dry_run: true`；无 `oos.*`；`walk_forward: []`
- 问题：无
- 下一步：M12 RL 训练 loop；EXP-TEXT-WF-002；真实 Walk-forward OOS hook（科研）

### EXP-20260602-031：v3 M11.6 StrategyCandidate 候选验证桥本地验证 ✅

- 日期：2026-06-03
- 阶段：**M11.6** — Population Top-K → `StrategyCandidate` → Quant Engine backtest smoke
- 环境：本地
- 交付：
  - `research/strategy_candidate.py` — `StrategyCandidate`、`assert_no_oos_metrics`（严格拒绝 `oos.*`）
  - `rl/candidate_bridge.py` — `extract_top_candidates`、`write_candidates`、`run_candidate_backtest_smoke`、`walk_forward_stub`
  - `scripts/export_population_candidates.py`、`configs/candidate_validation.yaml`
  - `docs/strategy_candidate_bridge.md`、`tests/test_strategy_candidate_bridge.py` — **11** 项
- 命令与结果：
  - `python -m pytest tests/test_strategy_candidate_bridge.py -v` → **11 passed**
  - `python -m pytest tests/test_population_training_loop.py tests/test_population_training.py -v` → **25 passed**
  - `python scripts/export_population_candidates.py --help` → 正常
  - `python scripts/export_population_candidates.py --population-config configs/population_training.yaml --top-k 2 --run-backtest-smoke --dry-run` → 正常
  - 全量 `python -m pytest -v` → **248 passed**（237→248，+11）
- 边界：无 broker / LLM / 网络 / 真实 walk-forward OOS；不写 `oos.*`；`backtest.*` 仅为 synthetic smoke
- 链路：`M11 竞争评估 → M11.5 多代训练 → M11.6 Top-K 导出 + backtest smoke → 后续真实 Walk-forward OOS`
- 问题：无
- 下一步：~~M11.7 服务器 OOS~~ ✅ EXP-POP-005；M12 RL 训练；EXP-TEXT-WF-002

### EXP-POP-003：v3 M11.5 服务器 pytest + population training dry-run ✅

- 日期：2026-06-03
- 阶段：**M11.5** 服务器 pull @ **`aa841d4`**
- 环境：a6000-9961；conda `quant-mas`；Python **3.11.15**
- 命令与结果：
  - `python -m pytest -v` → **237 passed** in **41.83s**
  - `python scripts/run_population_training.py --config configs/population_training.yaml --dry-run` → ✅
    - **3 generations**；`simulation_only: true`；`dry_run: true`
    - Gen1: 2 agents → Gen2/3: Top-K + mutation（如 `mean_rev_1_g1_1` scale **1.01**、`mean_rev_1_g1_1_g2_2` scale **1.03**）
    - `best_agent`: `mean_rev_1`；Elo 平局 **1500**（mock draw）；`simulation.sharpe_mean` ≈ **7.15**（**≠** OOS **0.586**）
    - 无 `oos.*`；无 memory/artifacts
- 问题：无
- 下一步：~~M11.6 候选桥~~ ✅ EXP-031/POP-004；M12 RL 训练；EXP-TEXT-WF-002

### EXP-20260602-030：v3 M11.5 种群训练闭环本地验证 ✅

- 日期：2026-06-03
- 阶段：**M11.5** — 多代 population training loop（M11 单轮评估 → 闭环训练）
- 环境：本地
- 交付：
  - `rl/population_training.py` — `PopulationTrainingConfig`、`GenerationSummary`、`PopulationTrainingLoop`
  - `scripts/run_population_training.py` — 默认 `--dry-run`；`--generations` / `--output-dir` / `--memory-path` / `--seed`
  - `configs/population_training.yaml`、`docs/population_training.md`
  - `tests/test_population_training_loop.py` — **12** 项
- 闭环：`initial population → competitive mock eval → Elo/ranking → Top-K → mutation → next generation`
- 命令与结果：
  - `python -m pytest tests/test_population_training_loop.py -v` → **12 passed**
  - `python -m pytest tests/test_population_training.py -v` → **13 passed**
  - `python -m pytest tests/test_trading_env.py tests/test_grpo_experiment.py -v` → **19 passed**
  - `python scripts/run_population_training.py --config configs/population_training.yaml --dry-run` → 正常
  - 全量 `python -m pytest -v` → **237 passed**（225→237，+12）
- 边界：无 broker / LLM / 网络 / GPU；dry-run 不写 memory/artifacts；非 dry-run 写 generation metrics + ExperimentMemory；**无** `oos.*`
- 问题：无
- 下一步：~~服务器 pull + pytest~~ ✅ EXP-POP-003；~~M11.6~~ ✅ EXP-POP-004；M12 RL 训练

### EXP-POP-002：v3 M11 服务器 pytest + competitive mock dry-run ✅

- 日期：2026-06-03
- 阶段：**v3 M11** 服务器 pull @ **`64a5b2a`**（含 M-017 `LLM_TIMEOUT_SECONDS` 测试隔离）
- 环境：a6000-9961；conda `quant-mas`；Python **3.11.15**
- 命令与结果：
  - `python -m pytest -v` → **225 passed** in **17.32s**
  - `python scripts/run_competitive_experiment.py --config configs/competitive.yaml --mode mock --dry-run` → ✅
    - `simulation_only: true`；2 agents × 3 windows
    - `population.top_agent`: `mean_rev_1`（Elo 平局 1500，tie-break `agent_id`）
    - `simulation.sharpe` ≈ **7.15**（**simulation.*** 短窗 mock，**≠** OOS **0.586**）
    - 输出无 `oos.sharpe`；`dry_run: true`，无 memory/artifacts
- 说明：三窗均为 momentum vs mean_reversion **draw**（同 synthetic 路径下 reward 相同）；符合 mock smoke 预期
- 问题：首次 pull 曾 **224 passed**（`test_resolve_local_vllm_with_mock_http` 受 `.env` `LLM_TIMEOUT_SECONDS=60` 影响）→ **`64a5b2a`** 修复
- 下一步：M12 RL 训练 loop；EXP-TEXT-WF-002

### EXP-20260602-029：v3 M11 竞争学习 / 策略种群本地验证 ✅

- 日期：2026-06-03
- 阶段：**v3 M11** — StrategyAgent pool + PopulationManager + Elo + CompetitiveEpisodeRunner（mock-first）
- 环境：本地；Codex 按 [codex_prompt_M11.md](codex_prompt_M11.md) 实现
- 交付：
  - `agents/strategy_agent.py` — `MomentumAgent`、`MeanReversionAgent`
  - `agents/risk_agent.py` — proposal 必经风控裁剪
  - `agents/population_manager.py` — Elo、Top-K、确定性 `next_generation`
  - `rl/competitive_runner.py`、`rl/elo_rating.py` — 多 agent × 多 window shadow simulation（复用 M7 `TradingEnv`）
  - `scripts/run_competitive_experiment.py`、`configs/competitive.yaml`
  - `docs/competitive_learning.md`
- 命令与结果：
  - `python -m pytest tests/test_population_training.py -v` → **13 passed**
  - `python -m pytest tests/test_trading_env.py tests/test_grpo_experiment.py -v` → **19 passed**（M7 零回归）
  - `python scripts/run_competitive_experiment.py --config configs/competitive.yaml --mode mock --dry-run` → 成功（仅 stdout，不写 memory/artifacts）
  - 全量 `python -m pytest -v` → **225 passed**（212→225，+13）
- 指标边界：只写 `population.*` / `simulation.*`；**不写** `oos.sharpe`；Population Elo ≠ 论文 OOS **0.586**
- 问题：无
- 下一步：~~服务器 pytest + competitive dry-run~~ ✅ EXP-POP-002；M12 RL 训练 loop

### EXP-POP-001：competitive mock dry-run 本地 smoke ✅

- 日期：2026-06-03
- 命令：`run_competitive_experiment.py --mode mock --dry-run`
- 结果：stdout summary；`simulation_only: true`；无 broker / LLM / DB / 网络
- 下一步：~~服务器 **EXP-POP-002**~~ ✅；M11.5 **EXP-030** / 服务器 **EXP-POP-003**

### EXP-20260602-026：v3 M9 服务器 Postgres/pgvector 真实 DB smoke ✅

- 日期：2026-06-03
- 阶段：**v3 M9** — Docker Postgres + pgvector 真实联调（非 mock）
- 环境：a6000-9961；conda `quant-mas`；代码 @ **`02bdb8a`**（psycopg3 cursor 修复）；infra `/mnt/localDisk3/weizian/infra/quant-mas-db/`
- 前置：`weizian` 加入 **docker 组** → `setup.sh` 启动 `quant-mas-postgres`；`POSTGRES_DSN` 在 `.env`
- 命令与结果：
  - `python scripts/seed_postgres_from_json.py --json-path /mnt/localDisk3/weizian/reports/experiments.json` → **imported=6**
  - `python scripts/query_memory.py --backend postgres --best-metric oos.sharpe` → **`server_walk_forward_001`**，`oos.sharpe` **0.586**（与 EXP-20260602-008 OOS baseline 一致）
  - `python scripts/index_documents.py --vector-store pgvector --dirs docs --embedding-dimensions 64` → **documents=24, chunks=443**
- 修复：首次 seed 后 `find_best` 报 `Connection has no fetchall` → **`_psycopg_compat.py`**（psycopg3 从 cursor 取行）
- 问题：无（6 条实验已入库，无需重复 seed；重复跑用 `--skip-existing`）
- 下一步：EXP-TEXT-WF-002；~~M11 竞争学习~~ ✅ EXP-029

### EXP-LLM-002：v3 M10 服务器 local_vLLM + ResearchAgent smoke ✅

- 日期：2026-06-03
- 阶段：**v3 M10** — a6000 上真实 vLLM OpenAI 兼容端点 + `ResearchAgent --provider local_vllm`
- 环境：a6000-9961；conda **`vllm`**（vLLM **0.22.0**，Python 3.11）+ **`quant-mas`**（客户端）；GPU **0**（RTX A6000）
- 模型：`/mnt/localDisk3/weizian/models/Qwen2.5-7B-Instruct`（本地 4×safetensors，HF 镜像下载；`HF_HUB_OFFLINE=1`）
- vLLM 启动要点：
  - **独立 conda 环境** `/mnt/localDisk3/weizian/conda_envs/vllm`（勿装进 quant-mas；勿用 `~/.local/bin/vllm`）
  - `export VLLM_USE_FLASHINFER_SAMPLER=0`（系统 CUDA 11 + FlashInfer JIT 会失败；用 PyTorch-native sampler）
  - `--enforce-eager`；`--served-model-name Qwen/Qwen2.5-7B-Instruct`
  - 端点：`http://127.0.0.1:8000`
- 命令与结果：
  - `curl http://127.0.0.1:8000/v1/models` → `Qwen/Qwen2.5-7B-Instruct`
  - `python scripts/run_research_agent.py --provider local_vllm --use-llm ...` → `llm_provider=local_vllm`
  - 产物：`/mnt/localDisk3/weizian/reports/llm/EXP-LLM-002.json`、`EXP-LLM-002-constrained.json`
- 约束 task 验收：仅解释 **EXP-20260602-008** walk-forward OOS baseline（**oos.sharpe ≈ 0.586**）；未将 `workflow_ml_backtest` 单段 sharpe 或 pytest 里程碑当论文指标
- 已知限制：
  - Qwen 常把 JSON 包在 markdown fence → 顶层 `hypothesis` 可能 fallback；实质内容在 `evidence_summary`
  - LLM 叙事非权威；论文主指标仍为 **OOS 0.586**
- 问题：无（FlashInfer/CUDA12 已通过 `VLLM_USE_FLASHINFER_SAMPLER=0` 规避；GPU OOM 因重复起第二个 vLLM，kill 旧进程即可）
- 下一步：~~EXP-026 Postgres smoke~~ ✅；EXP-TEXT-WF-002

### EXP-20260602-028：v3 M9/M10 服务器 pytest 验收 ✅

- 日期：2026-06-01
- 阶段：**v3 M9 + M10** 服务器 pull 后全量 pytest（**不含**真实 Postgres/vLLM smoke）
- 环境：a6000-9961，conda `quant-mas`，Python **3.11.15**；代码 @ **`3fd32e0`**（M10）
- 命令与结果：
  - `python -m pytest -v` → **212 passed** in **11.39s**
  - 含 `test_memory_enterprise.py` **12/12**、`test_context_engineering.py` **17/17**（全 mock，不联网）
- 问题：无
- 下一步：~~EXP-026 真实 Postgres smoke~~ ✅；~~EXP-LLM-002~~ ✅

### EXP-20260602-027：v3 M10 LLM 生产化本地验证 ✅

- 日期：2026-06-01
- 阶段：**v3 M10** — `local_vllm` provider + ResearchAgent 生产路径 + 文本边界
- 环境：本地，Codex 按 [codex_prompt_M10.md](codex_prompt_M10.md) 实现
- 交付：
  - `core/llm.py` — `resolve_llm_client` 支持 `mock` | `openai_compatible` | **`local_vllm`**（`VLLM_BASE_URL` / `VLLM_MODEL` / 可选 `VLLM_API_KEY`）；无 URL 时 warning + Mock
  - `agents/research_agent.py` — provider 配置；LLM 失败 warning + 回退 Mock；**不覆盖 metrics**
  - `run_research_agent.py` / `generate_report.py` — `--provider mock|openai_compatible|local_vllm`
  - `configs/llm.server.yaml.example`
  - `docs/context_engineering.md` — M10 provider 表 + M6 文本边界
  - `text_signals.py` / `lora_finetune.py` — 边界注释（结构化特征 only）
- 命令与结果：
  - `python -m pytest tests/test_context_engineering.py -v` → **17 passed**（12→17，+5）
  - 全量 `python -m pytest -v` → **212 passed**（207→212，+5）
- 安全边界：pytest 全 mock HTTP；无真实 DeepSeek/vLLM/HF 网络
- 问题：无
- 下一步：~~服务器 pytest **212**~~ ✅ EXP-028；~~vLLM smoke EXP-LLM-002~~ ✅

### EXP-20260602-026（历史探测，已由上方 ✅ 条目取代）

- 日期：2026-06-01（探测）；**2026-06-03 验收完成**
- 曾阻塞：weizian 不在 docker 组 → 2026-06-03 解除

### EXP-20260602-025：v3 M9 企业数据与数据库本地验证 ✅

- 日期：2026-06-01
- 阶段：**v3 M9** — Postgres Memory + pgvector + Neo4j 图关系骨架
- 环境：本地，Codex 按 [`项目v3设计.md`](../项目v3设计.md) §M9 实现
- 新增模块：
  - `src/quant_mas/memory/postgres_store.py` — PostgresMemoryStore（嵌套 metric、`find_best("oos.sharpe")`）
  - `src/quant_mas/memory/neo4j_store.py` — Neo4jGraphStore（实验/策略/特征节点 CRUD 骨架）
  - `src/quant_mas/rag/vector_store_pgvector.py` — PgVectorStore（upsert/search/delete）
  - `memory/factory.py` — `backend: json | sqlite | postgres`
  - `configs/memory.enterprise.yaml.example`
- CLI：
  - `scripts/query_memory.py --backend postgres`
  - `scripts/index_documents.py --vector-store pgvector`
- 命令与结果：
  - `python -m pytest tests/test_memory_enterprise.py -v` → **12 passed**
  - `python scripts/query_memory.py --help` → 正常
  - `python scripts/index_documents.py --help` → 正常
  - 全量 `python -m pytest -v` → **207 passed**（195→207，+12）
- 安全边界：企业后端测试全 mock，不联网；`DATABASE_URL` / Neo4j 凭据仅环境变量，不入 git
- 问题：无
- 下一步：~~服务器 Postgres 真实连接 + index/query~~ ✅ EXP-026；~~M10 LLM / vLLM~~ ✅

### EXP-20260602-024：Plus M8 MCP/A2A 协议层服务器验收 ✅

- 日期：2026-06-01
- 阶段：Plus **M8**（服务器 pull @ `0794bd6` 后）
- 环境：a6000-9961，conda `/mnt/localDisk3/weizian/conda_envs/quant-mas`，Python **3.11.15**
- 命令与结果：
  - `python -m pytest -v` → **195 passed** in **12.41s**
  - `python scripts/export_agent_cards.py --config configs/protocols.yaml --output-dir /mnt/localDisk3/weizian/reports/protocols --include-mcp-specs` → 正常
  - 输出：`supervisor_agent_card.json`、`research_agent_card.json`、`report_agent_card.json`、`mcp_tools.json`
- 问题：无
- 下一步：EXP-TEXT-WF-002 / Release v0.1.0 / GitHub Topics

### EXP-20260602-023：Plus M8 MCP/A2A 协议层本地验证 ✅

- 日期：2026-06-01
- 阶段：Plus **M8** — MCP-style adapter + Policy 网关 + A2A Agent Card 导出
- 环境：本地，Codex 按 [codex_prompt_M8.md](codex_prompt_M8.md) 实现
- 新增模块：
  - `src/quant_mas/protocols/mcp/` — types、policy、adapter
  - `src/quant_mas/protocols/a2a/agent_card.py` — Supervisor / Research / Report AgentCard
  - `scripts/export_agent_cards.py`；`configs/protocols.yaml`
- 命令与结果：
  - `python -m pytest tests/test_protocols.py -v` → **15 passed**
  - `python scripts/export_agent_cards.py --help` → 正常
  - `python scripts/export_agent_cards.py --config configs/protocols.yaml --output-dir ... --include-mcp-specs` → 正常
  - 回归：`test_supervisor_agent` + `test_walk_forward` + `test_trading_env` → **33 passed**
  - 全量 `python -m pytest -v` → **195 passed**（180→195，+15）
- 安全边界：不接外部 MCP server；deny shell/broker/order/secrets；执行仍经 ToolRegistry
- 问题：无
- 下一步：~~服务器 pytest（EXP-20260602-024）~~ ✅；可选 EXP-TEXT-WF-002 / Release v0.1.0

### EXP-20260602-022：Plus M7 RL 模拟服务器验收 ✅

- 日期：2026-06-01
- 阶段：Plus **M7**（服务器 pull @ `d8ece63` 后）
- 环境：a6000-9961，conda `/mnt/localDisk3/weizian/conda_envs/quant-mas`，Python **3.11.15**
- 命令与结果：
  - `git pull origin main` → `d8ece63`（`experiment_log.md` 本地冲突已 `checkout` 丢弃）
  - `python -m pytest -v` → **180 passed** in **10.15s**
  - `python scripts/run_rl_baseline.py --config configs/rl.yaml --policy random --dry-run` → 正常
- dry-run metrics（**simulation only**，synthetic 短 episode，**不可与 OOS 0.586 混比**）：
  - `simulation.sharpe` ≈ **9.54**
  - `simulation.total_return` ≈ **0.020**
  - `simulation.max_drawdown` ≈ **-0.0017**
  - `simulation_only`: **true**
- 问题：无
- 下一步：**M8** MCP / EXP-TEXT-WF-002 / EXP-RL-003（真实 parquet MLCopy）

### EXP-20260602-021：Plus M7 RL 模拟本地验证 ✅

- 日期：2026-06-01
- 阶段：Plus **M7** — TradingEnv + baseline policies + GRPO-style ranking（simulation only）
- 环境：本地 Windows，Codex 按 [codex_prompt_M7.md](codex_prompt_M7.md) 实现
- 新增模块：
  - `src/quant_mas/rl/` — `TradingEnvConfig` / `RewardConfig` / `StepResult`、`TradingEnv`、`baseline_policy`、`reward`、`grpo_experiment`、`mock_data`
  - `scripts/run_rl_baseline.py` — `--policy random|buy_hold|ml_copy`，`--dry-run`
  - `configs/rl.yaml`；`pyproject.toml` 可选依赖 `[rl]`（gymnasium）
- 命令与结果：
  - `python -m pytest tests/test_trading_env.py -v` → **13 passed**
  - `python -m pytest tests/test_grpo_experiment.py -v` → **6 passed**
  - `python scripts/run_rl_baseline.py --help` → 正常
  - `python scripts/run_rl_baseline.py --config configs/rl.yaml --policy random --dry-run` → 正常
  - 全量 `python -m pytest -v` → **180 passed**（161→180，+19）
- 安全边界：不接 broker；metrics 命名 `simulation.*`；**不替代** walk-forward OOS **0.586**
- 问题：无
- 下一步：~~服务器 pytest + dry-run~~ ✅ EXP-20260602-022；**M8** MCP 或 EXP-TEXT-WF-002

### EXP-TEXT-WF-001：FinBERT text + Walk-forward OOS（服务器）✅

- 日期：2026-06-03
- 阶段：Plus **M6 科研** — text signal 并入 features → walk-forward
- 环境：a6000-9961，4× RTX A6000，CUDA LightGBM，git ≥ `b9de2f2`
- 数据：
  - `features_with_text.parquet`：**6033 rows**，**20 cols**（+`finbert_sentiment`）
  - 文本覆盖：200/6033 signals；fillna(0) → 134 非零、5899 中性 0
  - 插曲：`market_data.parquet` 曾误覆盖为 105 行 → 已从年度分片 **re-merge 6033 行**
- 命令：
  ```bash
  python scripts/build_features.py --config configs/features.text.yaml \
    --storage-config configs/storage.server.yaml \
    --output /mnt/localDisk3/weizian/datasets/features/features_with_text.parquet
  python scripts/run_walk_forward.py \
    --config configs/walk_forward.yaml \
    --storage-config configs/storage.server.yaml \
    --features-path /mnt/localDisk3/weizian/datasets/features/features_with_text.parquet \
    --experiment-name server_walk_forward_text_001 \
    --output-dir /mnt/localDisk3/weizian/reports/walk_forward_text_001
  python scripts/compare_experiments.py \
    --storage-config configs/storage.server.yaml \
    --memory-path /mnt/localDisk3/weizian/reports/experiments.json \
    --output-dir /mnt/localDisk3/weizian/reports/research
  ```
- **OOS 对比**（vs **EXP-20260602-008** / `server_walk_forward_001`）：

  | 指标 | baseline | + text | Δ |
  |------|----------|--------|---|
  | **oos.sharpe** | **0.586** | **0.563** | **-0.023** |
  | oos.total_return | 0.443 | 0.420 | -0.023 |
  | oos.max_drawdown | -0.255 | -0.259 | — |
  | oos.auc_mean | 0.472 | 0.473 | +0.001 |
  | feature_count | 15 | 16 | +1 |
  | window_count | 19 | 19 | — |

- 产物：`/mnt/localDisk3/weizian/reports/walk_forward_text_001/`（metrics.json、summary.md 等）
- 比较表：`reports/research/comparison.md` **6 rows**（含两行 walk_forward）
- **结论（exploratory）**：200/6033 覆盖 + fillna(0) 下 OOS sharpe **略低于** baseline；**smoke 级探索**，不能据此否定 text 特征；需扩大新闻覆盖率后再评估
- 下一步：扩大 JSONL 覆盖；forward-fill 或真实 neutral 策略；可选 EXP-TEXT-002 LoRA

### EXP-TEXT-001：FinBERT baseline smoke（服务器）✅

- 日期：2026-06-03
- 阶段：Plus **M6** — 真实 FinBERT 推理（非 pytest）
- 环境：a6000-9961，`pip install -e ".[ml,text]"`，pytest **161 passed**（22.14s）
- 模型：
  - HuggingFace Hub **不可达**（Python `Network unreachable`）
  - **ModelScope** 下载 `ProsusAI/finbert` → `/mnt/localDisk3/weizian/models/hf/finbert_prosus/`
  - 配置：`configs/text_model.server.yaml`（本地 `model_name` 路径）
- 命令与结果：
  - 200 条 text records → **`datasets/text/signals_finbert.parquet`**
  - `models/text/exp_text_001/metadata.json`
  - 日志：`logs/exp_text_001_finbert.log`
- 问题：huggingface.co 不稳定；`.env` HF_TOKEN 当时为空（本次靠 ModelScope）
- 下一步：→ EXP-TEXT-WF-001 ✅

### EXP-20260602-020：Plus M6 服务器 pytest ✅

- 日期：2026-06-03
- 阶段：Plus v2 **M6**（服务器）
- 环境：a6000-9961，conda `/mnt/localDisk3/weizian/conda_envs/quant-mas`，Python 3.11.15，git **`f1b00a9`**（pull 后）/ **`b9de2f2`**（M6 代码）
- 命令与结果：
  - `git pull origin main` → M6 代码
  - `python -m pip install -e ".[ml,text]"`（text 验收环境）
  - `python -m pytest -v` → **161 passed** in **9.20s**（核心）/ **22.14s**（含 `[text]` 全量验收）
- 问题：首次 pull TLS 失败，后 fetch 成功
- 下一步：~~EXP-TEXT-001 / walk-forward~~ ✅ EXP-TEXT-001 / EXP-TEXT-WF-001

### EXP-20260602-019：Plus M6 金融文本信号本地验证 ✅

- 日期：2026-06-03
- 阶段：Plus v2 **M6**（本地 mock / synthetic，无真实 HF 权重）
- 环境：本地 Windows，核心 `pip install -e .`（**未装** `[text]` extra）
- 新增模块：
  - `src/quant_mas/text/` — `FinancialTextRecord` / `TextSignalRecord`、时间切分、`MockSentimentClassifier`、`FinBERTSentimentClassifier` 骨架、`train_lora_text_classifier` mock 骨架
  - `src/quant_mas/features/text_signals.py` — `merge_text_signals_into_features`（left join、duplicate key、future leakage 检查）
  - `scripts/train_text_model.py` — `--mode mock|finbert_baseline|lora`，`--dry-run`
  - `configs/text_model.yaml`；`pyproject.toml` 可选依赖 `[text]`
- 命令与结果：
  - `python -m pytest tests/test_text_signals.py -v` → **11 passed**
  - `python -m pytest tests/test_features.py -v` → **3 passed**
  - `python -m pytest tests/test_train_model.py -v` → **5 passed**
  - `python scripts/train_text_model.py --help` → 正常
  - `python scripts/train_text_model.py --mode mock --config configs/text_model.yaml --dry-run ...` → 写 `signals.parquet` + `metadata.json`
  - 全量 `python -m pytest -v` → **161 passed**（150→161，+11）
- 问题：无
- 下一步：~~EXP-TEXT-001~~ ✅ → EXP-TEXT-WF-001 ✅；扩大 text 覆盖后复跑 WF

### EXP-LLM-001：DeepSeek 云端 ResearchAgent smoke ✅

- 日期：2026-06-03
- 阶段：Plus v2 **M5**（服务器真实 LLM，非 pytest）
- 环境：a6000-9961，`LLM_PROVIDER=openai_compatible`，DeepSeek API（**key 不入库**）
- 命令：
  ```bash
  python scripts/run_research_agent.py \
    --storage-config configs/storage.server.yaml \
    --json-path /mnt/localDisk3/weizian/reports/experiments.json \
    --task "Explain walk-forward OOS sharpe baseline and compare to latest ML run" \
    --use-llm
  ```
- 结果摘要：
  - `"llm_provider": "openai_compatible"`（非 mock）
  - `baseline` → `server_walk_forward_001`，**oos.sharpe = 0.585673**（≈ EXP-20260602-008 **0.586**）
  - RAG 命中 `experiment_log.md` 等；LLM 正确指出：上下文中**无**更新 ML run metrics，不得对 in-sample sharpe 2.78 下 OOS 结论
  - 建议实验含 walk-forward 对比、显著性检验、分段分析（LLM 叙事，**非**引擎 metrics）
- 问题：无
- 下一步：**M6** 文本信号；可选 `generate_report.py --latest --use-llm`

### EXP-20260602-018：Plus M5 服务器 pytest + DeepSeek 路径 ✅

- 日期：2026-06-03
- 阶段：Plus v2 **M5**（服务器）
- 环境：a6000-9961，conda `/mnt/localDisk3/weizian/conda_envs/quant-mas`，git **`43c812a`**（M-017 pytest 隔离修复）
- 命令与结果：
  - `python -m pip install -e ".[llm]"`
  - `python -m pytest -v` → **150 passed** in **7.24s**（服务器 `.env` 含 `LLM_API_KEY` 时亦全绿）
  - DeepSeek smoke → 见 **EXP-LLM-001**
- 问题：首次有 `.env` 时 `test_resolve_llm_client_defaults_to_mock` 失败（M-017，已修复）
- 下一步：**M6** 金融文本模型

### EXP-20260602-017：Plus M5 上下文/LLM 本地验证 ✅

- 日期：2026-06-03
- 阶段：Plus v2 **M5**
- 模块：
  - Context：`context_schema.py`、`context_builder.py`、`compression.py`
  - LLM：`OpenAICompatibleLLMClient`、`resolve_llm_client`
  - Agent：`ResearchAgent`；`ReportAgent` + `ReportResult`
  - CLI：`run_research_agent.py`；`generate_report.py --use-llm`
  - 配置：`configs/context.yaml`、`configs/llm.yaml`；`.env.example` LLM_* 占位符
- 指标：
  - `test_context_engineering.py` → **12 passed, 1 warning**（无 key 回退 Mock，预期）
  - `test_agent_core.py` → **6 passed**
  - `test_supervisor_agent.py` → **17 passed**
  - 全量 → **150 passed, 1 warning**（+12，138→150）
- 验收：
  - `run_research_agent.py --task "Summarize OOS baseline vs latest ML run"` Mock JSON 正常
  - `generate_report.py --help` / `--latest` 行为保持
  - Supervisor **未替换**；metrics 不被 LLM 覆盖
- 问题：无
- 下一步：~~服务器~~ ✅ EXP-018 / EXP-LLM-001 → **M6**

### EXP-20260602-016：Plus M4 服务器 LangGraph 验收 ✅

- 日期：2026-06-03
- 阶段：Plus v2 **M4**（服务器）
- 环境：a6000-9961，conda `/mnt/localDisk3/weizian/conda_envs/quant-mas`，git **`c0fa5e3`**
- 前置：`python -m pip install -e ".[orchestration]"`（langgraph 1.2.4）
- 命令与结果：
  - `git pull origin main` → Fast-forward 至 `c0fa5e3`（修复 M-016 zip strict 建边）
  - `python -m pytest tests/test_langgraph_workflow.py::test_langgraph_build_and_dry_run_when_available -v` → **1 passed** in 0.89s
  - `python scripts/run_langgraph_workflow.py --dry-run --backend langgraph` → 6 节点完成，`errors: []`，artifacts/metrics 与 sequential dry-run 一致
- 测试基线说明：
  - 核心 `pip install -e .`：**137 passed, 1 skipped**（138 项；langgraph invoke 用例 skip）
  - 含 orchestration：**138 passed**（`test_langgraph_workflow.py` **12 passed**）
- 问题：首次 pull M4 时 langgraph backend 因 M-016 失败；`c0fa5e3` 已修复
- 下一步：**M5** 上下文/LLM

### EXP-20260602-015：Plus M4 LangGraph 本地验证 ✅

- 日期：2026-06-02
- 阶段：Plus v2 **M4**
- 模块：`src/quant_mas/orchestration/`、6 节点 DAG、sequential + 可选 langgraph、`run_langgraph_workflow.py`
- 指标：
  - `test_langgraph_workflow.py` → **10 passed, 1 skipped**（无 langgraph）
  - `test_supervisor_agent.py` → **17 passed**
  - 全量 → **136 passed, 1 skipped**（+10，126→136）
- 验收：`--dry-run --backend sequential` 6 节点完成；Supervisor **未替换**
- 问题：无（langgraph backend 建边 bug 见 M-016，服务器 EXP-016 已验证修复）
- 下一步：push → 服务器 → **M5**

### EXP-20260602-014：Plus M3 服务器验收 ✅

- 日期：2026-06-02
- 阶段：Plus v2 **M3**（服务器）
- 环境：a6000-9961，conda `/mnt/localDisk3/weizian/conda_envs/quant-mas`
- 命令与结果：
  - `python -m pytest -v` → **126 passed** in **3.04s**
  - `test_memory_store_v2.py` + `test_memory_rag.py` → **22 passed**
  - `index_documents.py --dirs docs` → **132 chunks** → `outputs/rag/index.json`
  - `query_memory.py --rag-query "walk-forward OOS sharpe"` → 命中 `experiment_log.md` 等 5 条
  - `query_memory.py --best-metric oos.sharpe`（默认 json 路径）→ 无 metric（**预期**：默认路径非服务器 `reports/experiments.json`）
- 正确查 OOS baseline 实验：
  ```bash
  python scripts/query_memory.py \
    --json-path /mnt/localDisk3/weizian/reports/experiments.json \
    --best-metric oos.sharpe
  ```
- 问题：无（路径说明见上，非 M3 bug）
- 下一步：**M4** LangGraph

### EXP-20260602-013：Plus M3 Memory/RAG v2 本地验证 ✅

- 日期：2026-06-02
- 阶段：Plus v2 **M3**
- 模块：
  - Memory：`store_base`、`JsonMemoryStore`、`SqliteMemoryStore`、`factory`、`configs/memory.yaml`
  - RAG：`HashEmbeddingClient`、`InMemoryVectorStore`、`HybridRetriever`、`chunking`
  - CLI：`index_documents.py`、`query_memory.py`
  - 文档：`docs/database_setup.md`
- 指标：
  - `tests/test_memory_store_v2.py` → **11 passed**
  - `tests/test_memory_rag.py` → **11 passed**（Prompt 20 兼容）
  - 全量 → **126 passed**（+11，115→126）
- 验收：`index_documents.py --help`、`query_memory.py --help` 正常
- 问题：无
- 下一步：push → 服务器 pytest 126 → **M4**

### EXP-20260602-012：Plus M2 服务器验收 + EXP-DATA-001 ✅

- 日期：2026-06-02
- 阶段：Plus v2 **M2**（服务器）
- 环境：a6000-9961，`git` @ `7514cdc`，conda `/mnt/localDisk3/weizian/conda_envs/quant-mas`
- 命令：
  - `python -m pytest tests/test_data_sources.py -v` → **13 passed** in 0.52s
  - Alpha Vantage：`AAPL 2026-01-01..2026-06-01` → **100 rows** → `datasets/raw/market_data.parquet`
  - Stooq：`AAPL 2024-01-01..2024-06-01` → **105 rows**
- EXP-DATA-001 汇总：
  - **FRED ✅**：DGS10 → 262 rows → `datasets/raw/macro/DGS10.parquet`
  - **Stooq ✅**：105 rows（2024 H1）
  - **Alpha Vantage ✅**：100 rows（近期窗口；`outputsize=auto` + 日期提示已修复）
  - **Finnhub ❌**：403 免费 tier 无 candle 权限（非代码 bug）
  - **SEC**：未测（需真实 `SEC_EDGAR_USER_AGENT`）
- 结论：OHLCV 用 **Stooq（历史）+ Alpha Vantage（近期）**；宏观用 **FRED**
- 问题：无
- 下一步：**M3** Memory/RAG v2（见 `docs/codex_prompt_M3.md`）

### EXP-20260602-011：Plus M2 多数据源扩展本地验证 ✅

- 日期：2026-06-02
- 阶段：Plus v2 **M2**
- 模块：`src/quant_mas/data/fetchers/` 子包、DataSourceRegistry、AlphaVantage/Finnhub/FRED/SEC fetcher、`configs/data_sources.yaml`
- CLI：`download_data.py` — alpha_vantage / finnhub / fred / sec_edgar；`--series-id`；`--cik`
- 指标：
  - `tests/test_data_sources.py` → **13 passed**
  - `tests/test_stooq_fetcher.py` → **6 passed**
  - 全量 → **115 passed**（+13，102→115）
- 验收：mock HTTP，不联网；`.env.example` 占位符无真实 key
- 问题：无
- 下一步：push → 服务器 ✅ 见 EXP-20260602-012 → **M3**

### EXP-20260602-010：Plus M1 服务器验证 ✅

- 日期：2026-06-02
- 阶段：Plus v2 **M1**（服务器 pull 后验收，EXP-TODO-008 完成）
- 环境：a6000-9961，`git` @ `3a7d6df`，conda `/mnt/localDisk3/weizian/conda_envs/quant-mas`
- 命令：
  - `git pull origin main` → `python -m pip install -e .`
  - `python -m pytest -v` → **102 passed** in **1.64s**
  - `python scripts/compare_experiments.py --storage-config configs/storage.server.yaml --output-dir outputs/research`
- 指标：
  - 比较表 **5 rows**
  - `server_walk_forward_001` → `oos.sharpe` **0.585673**（≈ 0.586，与 EXP-20260602-008 一致）
  - `server_ml_backtest_001` → sharpe **2.781**（in-sample，非 OOS）
- 产物：`outputs/research/comparison.csv`、`comparison.md`
- 问题：无
- 下一步：**M2 数据扩展**

### EXP-20260602-009：Plus M1 研究基线本地验证 ✅

- 日期：2026-06-02
- 阶段：Plus v2 **M1**（研究基线与实验规范）
- 模块：
  - `src/quant_mas/research/baseline.py` — `BaselineRun`、`BaselineRegistry`（`add_baseline`、`list_baselines`、`compare_runs`、`get_best("oos.sharpe")`）
  - `src/quant_mas/research/metrics_table.py` — `collect_experiment_metrics`、`build_comparison_table`（嵌套 `oos.sharpe`）
  - `scripts/compare_experiments.py` — ExperimentMemory → `comparison.csv` / `comparison.md`
  - `docs/research_protocol.md` — 实验规范；论文主指标 = Walk-forward OOS
- 指标：
  - `python scripts/compare_experiments.py --help` → 正常
  - `python -m pytest tests/test_research_baseline.py -v` → **4 passed**
  - 全量 `python -m pytest -v` → **102 passed**（+4，基线 98→102）
- 验收：synthetic 测试覆盖嵌套 metric、best baseline、CLI 核心输出；不联网、不调 LLM
- 问题：无
- 下一步：服务器验证 ✅ → 见 EXP-20260602-010 → **M2**

### EXP-20260601-015：Prompt 13 文档收口 ✅

- 日期：2026-06-01
- 阶段：第一阶段（Prompt 13，主链路完成后统一整理）
- 内容：同步 `docs/progress.md`、`docs/architecture.md`、`docs/experiment_log.md` 与 `项目进度.md` / `项目指导.md`
- 验收：测试基线统一为 **98 passed**；阶段表与 EXP 里程碑一致；无虚构实验
- 问题：无
- 下一步：科研实验 / 论文材料；可选 EXP-TODO-006

### EXP-20260601-014：服务器 Prompt 20 pull 后全量 pytest ✅

- 日期：2026-06-01
- 阶段：第四阶段（Prompt 20 服务器验证）
- 环境：a6000-9961，`git` @ `d41ba54`，conda `/mnt/localDisk3/weizian/conda_envs/quant-mas`
- 命令：`git pull` → `python -m pip install -e .` → `python -m pytest -v`
- 指标：全量 **98 passed** in **1.93s**（含 `test_memory_rag.py` 11 项）
- 问题：无
- 下一步：文档收口（已完成 EXP-20260601-015）

### EXP-20260601-013：Prompt 20 Memory/RAG 本地验证 ✅

- 日期：2026-06-01
- 阶段：第四阶段（Prompt 20）
- 模块：ExperimentMemory 增强、TradeMemory、document_loader、SimpleRetriever
- 指标：
  - `tests/test_memory_rag.py`：**11 passed**
  - `tests/test_experiment_memory.py`：**2 passed**
  - 全量：**98 passed**（+11）
- 验收：嵌套 metric（如 `oos.sharpe`）排序；docs 关键词检索；无 LLM/向量库
- 问题：无
- 下一步：服务器 pytest（已完成 EXP-20260601-014）

### EXP-20260601-012：服务器 Prompt 19 pull 后全量 pytest ✅

- 日期：2026-06-01
- 阶段：第三阶段（Prompt 19 服务器验证）
- 环境：a6000-9961，`git` @ `edbd71a`，conda `/mnt/localDisk3/weizian/conda_envs/quant-mas`
- 命令：`git pull` → `python -m pip install -e .` → `python -m pytest -v`
- 指标：全量 **87 passed** in **1.90s**
- 问题：无
- 下一步：Codex Prompt 20（Memory + RAG）

### EXP-20260601-011：Prompt 19 Supervisor 路由本地验证 ✅

- 日期：2026-06-01
- 阶段：第三阶段（Prompt 19）
- 模块：`MLBacktestTool`、`PipelineTool`、Supervisor 扩展、`run_agent.py`（7 工具）
- 指标：
  - `tests/test_supervisor_agent.py`：**17 passed**
  - 全量 `python -m pytest -v`：**87 passed**（+11 测试）
- 验收：
  - ml_backtest / risk_check / pipeline 中英文路由
  - kwargs 别名映射（data_path、tool_config、risk_config 等）
  - `run_agent.py --help` 正常
- 问题：无
- 下一步：Prompt 20 Memory/RAG

### EXP-20260601-009：Prompt 18 基础风控层本地验证 ✅

- 日期：2026-06-01
- 阶段：第二阶段扩展（Prompt 18）
- 数据：synthetic `target_weight` parquet（pytest `tmp_path`）
- 模块：`RiskLimits`、`RiskDecision`、`check_position_limits`、`check_drawdown`、`RiskTool`
- 配置：`configs/risk.yaml`（`max_position_weight`、`max_total_exposure`、`allow_short`）
- 指标：
  - `tests/test_risk.py`：**5 passed**
  - 全量 `python -m pytest -v`：**76 passed**
- 验收：
  - 超限时 `clip=True` → status=`clipped`，`adjusted_targets` 可审计
  - `clip=False` → status=`rejected`
  - 回撤超限 → `max_drawdown_exceeded`
  - `RiskTool` 可注册 `ToolRegistry`，返回 metadata 含 `decisions` / `violations`
- 产物路径：代码 `src/quant_mas/risk/`、`src/quant_mas/tools/quant/risk_tool.py`
- 问题：无（兼容保留原 `tools/quant.py` 导出）
- 下一步：Prompt 19 Supervisor 接入 `risk_check` 路由

### EXP-20260601-010：服务器 Prompt 18 pull 后全量 pytest ✅

- 日期：2026-06-01
- 阶段：第二阶段扩展（Prompt 18 服务器验证）
- 环境：a6000-9961，`git` @ `60c2ee7`，conda `/mnt/localDisk3/weizian/conda_envs/quant-mas`
- 命令：`git pull origin main` → `python -m pip install -e .` → `python -m pytest -v`
- 指标：
  - 全量：**76 passed** in **1.76s**
  - 含 `tests/test_risk.py` 5 项全部通过
- 问题：无
- 下一步：Codex Prompt 19（Supervisor 路由增强）

### EXP-20260602-001：最小端到端 synthetic pipeline 测试

- 日期：2026-06-02
- 阶段：Phase 1 工程验证
- 数据：pytest 中生成的 synthetic OHLCV 数据
- 策略 / 模型：MovingAverageCrossStrategy
- 参数：测试内固定小窗口参数
- 指标：测试仅验证指标字段存在，不记录具体收益数值
- 产物路径：pytest `tmp_path` 临时目录
- 问题：无
- 下一步：使用 sample parquet 或真实小规模数据验证 `scripts/run_pipeline.py`

### EXP-20260602-002：本地 synthetic CLI pipeline smoke test

- 日期：2026-06-02
- 阶段：Phase 1 CLI 验证
- 数据：本地 synthetic OHLCV parquet
- 策略 / 模型：MovingAverageCrossStrategy
- 参数：`--skip-download --strategy ma_cross --experiment-name synthetic_pipeline_cli`
- 指标：已由脚本输出，但该记录不作为真实研究实验结果
- 产物路径：`outputs/reports/synthetic_pipeline_cli/`
- 问题：仅为 smoke test，不代表真实市场表现
- 下一步：用 sample parquet 或真实小规模数据验证

### EXP-20260602-008：服务器 Walk-forward 真实实验 ✅（Prompt 17）

- 日期：2026-06-02
- 阶段：Phase 2 Step 2.4（Prompt 17 服务器验证）
- 环境：a6000-9961，CUDA LightGBM，`git` @ `1f4df61`
- 数据：`/mnt/localDisk3/weizian/datasets/features/features.parquet`（6033 rows，865K）
- 配置：`walk_forward.yaml` — train 504 / val 126 / test 126 / oos 63 / step 63
- 参数：`--experiment-name server_walk_forward_001`；`device_requested=auto`，`device_resolved=cuda`，`device_fallback=false`
- 运行：约 **17s**，**19 个窗口**
- OOS 汇总（`metrics.json` → `oos` 块，**主记录指标**）：
  - sharpe：**0.586**
  - total_return：**0.443**（≈ +44%）
  - annualized_return：**0.080**
  - max_drawdown：**-0.255**
  - final_equity：**144,261**
  - bars：**1197**
  - auc_mean：**0.472**；accuracy_mean：**0.479**
  - window_count：**19**
- 与单段 ML 回测对比（EXP-20260602-005，**非 OOS，勿混用**）：

  | 指标 | Walk-forward OOS | server_ml_backtest_001 |
  |------|------------------|------------------------|
  | sharpe | **0.586** | 2.78 |
  | total_return | 0.443 | 68.27 |
  | annualized_return | 0.080 | 0.701 |
  | max_drawdown | -0.255 | -0.246 |
  | bars | 1197 | 2011 |

- 解读：单段 sharpe 2.78 **不能代表样本外**；OOS sharpe ≈ 0.59、收益 ≈ +44% 与 val/test AUC ≈ 0.47–0.49 一致，更接近真实泛化。各窗 `oos_sharpe` 有盈有亏（如 window 5/7 为负）属滚动 OOS 正常；`backtest_sharpe_mean` ≈ 0.86 为分窗均值，**报告以拼接 OOS `oos.sharpe` 为准**。
- 产物路径：
  - 报告：`/mnt/localDisk3/weizian/Quant-MAS/outputs/reports/walk_forward_latest/`
  - metrics / windows / oos_equity / oos_trades / summary
  - 日志：`/mnt/localDisk3/weizian/logs/walk_forward_server_001.log`
- 前置：`python -m pytest -v` → **71 passed**（1.65s）
- 问题：无
- 下一步：**Prompt 18** 风控层；可选 CPU 对照（EXP-TODO-006）

### EXP-20260602-007：Prompt 17 Walk-forward 本地验证 ✅

- 日期：2026-06-02
- 阶段：Phase 2 Step 2.4（Prompt 17）
- 环境：本地 Windows，Codex 改代码后
- 数据：synthetic features + mock model（测试不依赖真实金融数据）
- 模块：`walk_forward.py`、`save_walk_forward_report()`、`run_walk_forward.py`
- 参数：
  - `python -m pytest tests/test_walk_forward.py -v` → **3 passed**
  - `python -m pytest -v` → **71 passed**
  - `python scripts/run_walk_forward.py --help` → 正常
- 验证点：按时间推进 train/val/test/oos 窗口；模型仅 train 拟合；OOS 接入 MLSignalStrategy + BacktestEngine；metrics 区分 train/val/test/oos
- 产物（测试 tmp_path）：metrics.json、windows.csv、oos_equity_curve.csv、oos_trades.csv、summary.md
- 问题：无
- 下一步：服务器真实 walk-forward（EXP-TODO-007）

### EXP-20260602-005：服务器 ML 信号回测 ✅（Prompt 16）

- 日期：2026-06-02
- 阶段：Phase 2 Step 2.3（Prompt 16 服务器验证）
- 环境：a6000-9961，CUDA LightGBM 4.6.0
- 数据：真实 features + GPU 训练模型（`server_lgbm_gpu_001`）
- 策略 / 模型：`MLSignalStrategy` + `LightGBMDirectionModel` pred_proba
- 参数：`run_ml_backtest.py --experiment-name server_ml_backtest_001`
- 指标（2011 bars）：
  - total_return：**68.27**（脚本输出比例，非百分号）
  - annualized_return：**0.701**
  - sharpe：**2.78**
  - max_drawdown：**-0.246**
  - final_equity：**6,927,128.57**
- 产物路径：
  - 报告：`outputs/reports/ml_backtest_latest/summary.md`
  - 日志：`/mnt/localDisk3/weizian/logs/ml_backtest_server_001.log`
- 问题：无（链路验证通过；收益数值需后续 walk-forward 样本外复核）
- 下一步：walk-forward 服务器 ✅ → 见 EXP-20260602-008

### EXP-20260602-004：服务器 GPU LightGBM 训练 ✅（Prompt 15b）

- 日期：2026-06-02
- 阶段：Phase 2 Step 2.2b（Prompt 15b 服务器验证）
- 环境：a6000-9961，4× RTX A6000，驱动 580，CUDA 13.0
- 数据：真实 features（6033 rows，与 EXP-20260601-006 相同）
- 策略 / 模型：`LightGBMDirectionModel`，`--device cuda`，`future_direction_5`
- 参数：`configs/train.gpu.yaml`，`--experiment-name server_lgbm_gpu_001`
- device（metadata / metrics）：
  - `device_requested`: cuda
  - `device_resolved`: cuda
  - `device_fallback`: false
  - `device_reason`: null
- 指标：
  - train：accuracy **0.869**，AUC **0.961**，4170 samples
  - val：accuracy **0.445**，AUC **0.457**，894 samples
  - test：accuracy **0.456**，AUC **0.479**，894 samples
  - feature_count：15
- 产物路径：`/mnt/localDisk3/weizian/models/lightgbm_direction_latest/`
- 问题：首次训练失败 — PyPI CPU-only LightGBM（见 M-010）；源码编译 CUDA 版后成功
- 与 CPU 基线（EXP-20260601-006）：val/test AUC 仍 ~0.46–0.48，属模型过拟合问题，非 GPU 链路问题
- 下一步：可选 `server_lgbm_cpu_001` 对照；Prompt 17

### EXP-20260602-003：服务器全量 pytest 验证

- 日期：2026-06-02
- 阶段：Phase 1 服务器部署验证
- 环境：
  - 主机：a6000-9961
  - 路径：`/mnt/localDisk3/weizian/Quant-MAS`
  - Conda：`/mnt/localDisk3/weizian/conda_envs/quant-mas`
  - Python：3.11.15
- 数据：synthetic（pytest 内置，不联网）
- 策略 / 模型：全模块单元 / 集成测试
- 参数：`python -m pytest -v`
- 指标：**44 passed in 1.19s**（2026-06-02 初验；同日后 pull GPU 代码并重装 CUDA LightGBM 后为 **68 passed**）
- 产物路径：无（测试不产生持久产物）
- 问题：无
- 下一步：真实数据下载与 pipeline

### EXP-20260601-008：Prompt 15b LightGBM GPU/CUDA 本地验证 ✅

- 日期：2026-06-01
- 阶段：Phase 2 Step 2.2b（GPU 训练支持）
- 环境：本地 Windows，Codex 改代码后
- 数据：synthetic / mock（无真实 GPU）
- 模型：`LightGBMDirectionModel` + `resolve_training_device`
- 参数：
  - `python -m pytest tests/test_device.py -v` → **10 passed**
  - `python -m pytest tests/test_train_model.py -v` → **5 passed**
  - `python -m pytest -v` → **68 passed**
  - `python scripts/train_model.py --help` → 含 `--device {auto,cpu,gpu,cuda}`
- 验证点：auto/cuda/gpu/cpu 解析；无 GPU 安全 fallback；metrics/metadata 含 device 字段
- 问题：无
- 下一步：服务器验证完成 → 见 EXP-20260602-004

### EXP-20260601-007：Prompt 16 MLSignalStrategy 本地验证 ✅

- 日期：2026-06-01
- 阶段：Phase 2 Step 2.3（Prompt 16）
- 环境：本地 Windows，Codex 改代码后
- 数据：synthetic features + mock model
- 策略 / 模型：`MLSignalStrategy`（buy/sell threshold → target_weight）
- 参数：`python -m pytest tests/test_ml_signal_strategy.py -v`；`python -m pytest -v`
- 指标：**4 passed**（ML 专项）；**57 passed**（全量）
- 验证点：pred_proba → signal；下一根 bar 成交；报告产物；禁止 future label 进特征
- 问题：无
- 下一步：服务器验证完成 → 见 EXP-20260602-005

### EXP-20260601-006：服务器真实 LightGBM 训练 ✅

- 日期：2026-06-01
- 阶段：Phase 2 Step 2.2（Prompt 15 服务器验证）
- 环境：a6000-9961，`/mnt/localDisk3/weizian/conda_envs/quant-mas`
- 数据：真实 features（6033 rows，AAPL/MSFT/SPY，来自 Step 2.1 pipeline）
- 策略 / 模型：`LightGBMDirectionModel`，label `future_direction_5`，15 features
- 参数：
  - `configs/train.yaml`（n_estimators=100，70/15/15 时间切分）
  - `--experiment-name server_lgbm_001`
- 指标：
  - train：accuracy **0.876**，AUC **0.965**，4170 samples（2018-01-31 — 2023-08-09）
  - val：accuracy **0.445**，AUC **0.458**，894 samples（2023-08-10 — 2024-10-15）
  - test：accuracy **0.455**，AUC **0.466**，894 samples（2024-10-16 — 2025-12-23）
  - train_positive_rate：0.695 / val：0.403 / test：0.311
- 产物路径：
  - 模型目录：`/mnt/localDisk3/weizian/models/lightgbm_direction_latest/`
  - metrics：`.../metrics.json`
  - feature_importance：`.../feature_importance.csv`
  - model：`.../model.pkl`
  - feature_columns / metadata：同目录
  - ExperimentMemory：`/mnt/localDisk3/weizian/reports/experiments.json`（`server_lgbm_001`）
- 问题：**明显过拟合** — 训练集 AUC 高、val/test AUC 接近随机（~0.46）；标签正负比例随时间漂移。属 MVP 基线结果，非脚本故障。
- 下一步：**Prompt 16** — MLSignalStrategy + 样本外 ML 回测；后续可调参 / 特征 / 类别权重

### EXP-20260601-005：Prompt 15 ML 训练模块本地验证 ✅

- 日期：2026-06-01
- 阶段：Phase 2 Step 2.2（Prompt 15）
- 环境：本地 Windows，Codex 改代码后
- 数据：synthetic features（mock 模型，不依赖真实 LightGBM）
- 策略 / 模型：`train_direction_model()` + mock direction model
- 参数：`python -m pytest -v`
- 指标：**53 passed**
- 验证产物（测试 `tmp_path`）：
  - `metrics.json`（train/val/test accuracy、auc、时间范围、样本数）
  - `feature_importance.csv`
  - `model.pkl`
  - `feature_columns.json`、`metadata.json`
  - ExperimentMemory 记录
- 问题：无
- 下一步：git push → 服务器 `requirements-ml.txt` + 真实 `train_model.py`

### EXP-20260601-004：服务器真实数据 Stooq 下载 + ma_cross pipeline ✅

- 日期：2026-06-01
- 阶段：Phase 1 Step 1.5 / Phase 2 Step 2.1
- 环境：
  - 主机：a6000-9961
  - 路径：`/mnt/localDisk3/weizian/Quant-MAS`
  - Conda：`/mnt/localDisk3/weizian/conda_envs/quant-mas`
  - 数据源：**Stooq**（`STOOQ_API_KEY` in `.env`）
- 数据：
  - 标的：AAPL、MSFT、SPY
  - 区间：2018-01-01 — 2025-12-31（按年 parquet，合并）
  - 原始行数：**6033 rows** → `/mnt/localDisk3/weizian/datasets/raw/market_data.parquet`
- 策略 / 模型：MovingAverageCrossStrategy（`ma_cross`）
- 参数：
  - `SOURCE=stooq bash server/download_data_resilient.sh`
  - `run_pipeline.py --skip-download --experiment-name server_ma_cross_real_001`
- 指标（回测约 2011 bars）：
  - total_return：≈ 2.02
  - annualized_return：≈ 0.149
  - sharpe：≈ 1.00
  - max_drawdown：≈ -0.21
  - final_equity：≈ 302,453
- 产物路径：
  - raw：`/mnt/localDisk3/weizian/datasets/raw/market_data.parquet`
  - reports：`/mnt/localDisk3/weizian/reports/server_ma_cross_real_001/`
  - metrics：`.../metrics.json`
  - equity_curve：`.../equity_curve.csv`
  - trades：`.../trades.csv`
  - summary：`.../summary.md`
  - 日志（MSFT+SPY 下载）：`/mnt/localDisk3/weizian/logs/resilient_msft_spy.log`
- 问题：Yahoo yfinance 限流；Stooq 需 API Key（见 `mistakes.md` M-009）
- 下一步：Prompt 15 / 16 已完成

## 待验证实验

### EXP-TODO-006：CPU 对照训练（可选）

- 目的：与 EXP-20260601-006 / EXP-20260602-004 在同一 features 上对比 CPU vs GPU metrics
- 命令：`train_model.py --device cpu --experiment-name server_lgbm_cpu_001`
- 状态：可选，未跑

## 实验里程碑速查

| 编号 | 日期 | 内容 | 关键结果 |
|------|------|------|----------|
| EXP-20260601-004 | 2026-06-01 | Stooq 真实数据 + ma_cross | 6033 rows，sharpe ≈ 1.00 |
| EXP-20260601-006 | 2026-06-01 | CPU LightGBM 训练 | test AUC 0.466 |
| EXP-20260602-004 | 2026-06-02 | GPU LightGBM 训练 | device=cuda，test AUC 0.479 |
| EXP-20260602-005 | 2026-06-02 | ML 信号回测（单段） | sharpe 2.78（in-sample，勿混用） |
| EXP-20260602-008 | 2026-06-02 | Walk-forward 服务器 | **OOS sharpe 0.586**，19 窗 |
| EXP-20260602-009 | 2026-06-02 | Plus M1 研究基线本地 | **102 passed**（+4 测试） |
| EXP-20260602-010 | 2026-06-02 | Plus M1 服务器 pytest + 比较表 | **102 passed**；OOS sharpe 0.586 |
| EXP-20260602-011 | 2026-06-02 | Plus M2 数据扩展本地 | **115 passed**（+13） |
| EXP-POP-005 | 2026-06-04 | v3 M11.7 服务器 candidate OOS | `cand_mean_rev_1` **oos.sharpe 1.036** vs baseline **0.586**（77 窗）@ `ffef849` |
| EXP-20260602-032 | 2026-06-03 | v3 M11.7 候选 Walk-forward OOS | **259 passed**（+11）；OOS **11/11** |
| EXP-POP-004 | 2026-06-03 | v3 M11.6 服务器 | **248 passed**（55.15s）+ export dry-run @ `7ab510f` |
| EXP-20260602-031 | 2026-06-03 | v3 M11.6 候选验证桥 | **248 passed**（+11）；bridge **11/11** |
| EXP-POP-003 | 2026-06-03 | v3 M11.5 服务器 | **237 passed**（41.83s）+ training dry-run @ `aa841d4` |
| EXP-20260602-030 | 2026-06-03 | v3 M11.5 种群训练闭环 | **237 passed**（+12）；loop **12/12** |
| EXP-POP-002 | 2026-06-03 | v3 M11 服务器 | **225 passed**（17.32s）+ competitive dry-run @ `64a5b2a` |
| EXP-20260602-029 | 2026-06-03 | v3 M11 竞争学习本地 | **225 passed**（+13）；population **13/13** |
| EXP-POP-001 | 2026-06-03 | competitive mock dry-run | ✅ 本地；simulation_only |
| EXP-20260602-028 | 2026-06-01 | v3 M9/M10 服务器 pytest | **212 passed**（11.39s）@ `3fd32e0` |
| EXP-20260602-027 | 2026-06-01 | v3 M10 LLM 本地 | **212 passed**（+5）；context **17/17** |
| EXP-20260602-026 | 2026-06-03 | v3 M9 服务器 DB | ✅ Postgres query + pgvector **443 chunks**；OOS **0.586** @ `02bdb8a` |
| EXP-20260602-025 | 2026-06-01 | v3 M9 企业 DB 本地 | **207 passed**（+12）；enterprise **12/12** |
| EXP-20260602-024 | 2026-06-01 | Plus M8 MCP/A2A 服务器 | **195 passed**（12.41s）；export_agent_cards ✅ |
| EXP-20260602-023 | 2026-06-01 | Plus M8 MCP/A2A 本地 | **195 passed**（+15）；protocols **15/15** |
| EXP-20260602-022 | 2026-06-01 | Plus M7 服务器 pytest + RL dry-run | **180 passed**（10.15s） |
| EXP-20260602-021 | 2026-06-01 | Plus M7 RL 模拟本地 | **180 passed**（+19）；trading_env **13/13** |
| EXP-TEXT-WF-001 | 2026-06-03 | FinBERT + walk-forward OOS | oos.sharpe **0.563** vs baseline **0.586** |
| EXP-TEXT-001 | 2026-06-03 | FinBERT smoke（ModelScope） | 200 signals → signals_finbert.parquet |
| EXP-20260602-020 | 2026-06-03 | Plus M6 服务器 pytest | **161 passed**（9.20s / 22.14s 含 `[text]`） |
| EXP-20260602-019 | 2026-06-03 | Plus M6 文本信号本地 | **161 passed**（+11）；test_text_signals **11/11** |
| EXP-LLM-001 | 2026-06-03 | DeepSeek ResearchAgent smoke | openai_compatible；OOS sharpe **0.586** |
| EXP-20260602-018 | 2026-06-03 | Plus M5 服务器 pytest | **150 passed**（7.24s） |
| EXP-20260602-017 | 2026-06-03 | Plus M5 上下文/LLM 本地 | **150+1 warning**（+12） |
| EXP-20260602-016 | 2026-06-03 | Plus M4 服务器 langgraph backend | langgraph dry-run ✅；commit `c0fa5e3` |
| EXP-20260602-015 | 2026-06-02 | Plus M4 LangGraph 本地 | **137+1 skip**（138 项；+11 workflow 测试） |
| EXP-20260602-014 | 2026-06-02 | Plus M3 服务器 pytest + RAG smoke | **126 passed**（3.04s） |
| EXP-20260602-013 | 2026-06-02 | Plus M3 Memory/RAG v2 本地 | **126 passed**（+11） |
| EXP-20260602-012 | 2026-06-02 | Plus M2 服务器 + API smoke | test_data_sources 13/13；FRED/Stooq/AV ✅ |
| EXP-DATA-001 | 2026-06-02 | M2 API smoke（并入 012） | Finnhub 免费 blocked；SEC 未测 |
| EXP-20260601-009 | 2026-06-01 | Prompt 18 风控本地 | 76 passed |
| EXP-20260601-010 | 2026-06-01 | Prompt 18 服务器 pytest | 76 passed |
| EXP-20260601-011 | 2026-06-01 | Prompt 19 Supervisor 本地 | 87 passed |
| EXP-20260601-012 | 2026-06-01 | Prompt 19 服务器 pytest | 87 passed |
| EXP-20260601-013 | 2026-06-01 | Prompt 20 Memory/RAG 本地 | 98 passed |
| EXP-20260601-014 | 2026-06-01 | Prompt 20 服务器 pytest | 98 passed（1.93s） |
| EXP-20260601-015 | 2026-06-01 | Prompt 13 文档收口 | 三份 docs 与主文档对齐 |
