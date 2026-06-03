# Quant MAS 实验记录

更新时间：2026-06-03（Plus M5 本地 EXP-20260602-017）

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

### 当前快照：COMP-20260602-002（服务器 CLI 已验证，EXP-20260602-010）

- 生成：`python scripts/compare_experiments.py --storage-config configs/storage.server.yaml --output-dir outputs/research`
- Memory：`/mnt/localDisk3/weizian/reports/experiments.json`
- 行数：**5**
- 对照 baseline：**EXP-20260602-008**，`oos.sharpe = 0.586`

| name | family | sharpe | oos.sharpe | total_return | oos.total_return | max_drawdown | test_auc | vs OOS baseline | 备注 |
|------|--------|--------|------------|--------------|------------------|--------------|----------|-----------------|------|
| server_ma_cross_real_001 | ma_cross | 1.001 | — | 2.025 | — | -0.206 | — | 不可直接比 OOS | EXP-20260601-004 |
| server_lgbm_001 | lightgbm | — | — | — | — | — | 0.466 | 不可直接比 OOS | EXP-20260601-006 |
| server_lgbm_gpu_001 | lightgbm | — | — | — | — | — | 0.479 | 不可直接比 OOS | EXP-20260602-004 |
| server_ml_backtest_001 | ml_backtest | **2.781** | — | 68.27 | — | -0.246 | — | ⚠️ in-sample | EXP-20260602-005 |
| server_walk_forward_001 | walk_forward | — | **0.586** | — | 0.443 | — | — | **baseline** | EXP-20260602-008 |
| （RAG/LLM/RL 等） | other | 待验证 | 待验证 | 待验证 | 待验证 | 待验证 | 待验证 | 待验证 | Plus M4+ |

**说明：**

- CLI 输出 `oos.sharpe` 精确值 **0.585673** ≈ 报告 **0.586**，与 EXP-20260602-008 一致。
- 仅 **walk_forward** 行可用于论文主结论。

### 历史快照：COMP-20260602-001（手工整理，已被 COMP-20260602-002 取代）

## 实验记录模板

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
- 下一步：push → 服务器 pytest → 可选 EXP-LLM-001（真实 LLM smoke）

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
