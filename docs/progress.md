# Quant MAS 开发进度

更新时间：2026-06-04（**v3 M12.1 ✅** 双端 **282** · EXP-POP-007 RL smoke）

**Plus v2**：M1–M8 ✅ · **v3 M9–M12.1** ✅ 双端闭环

**pytest 基线**：**282 passed** 本地 · **论文主指标**：Walk-forward ML OOS sharpe **0.586**（EXP-008）· **候选 OOS（单）**：`cand_mean_rev_1` **1.036**（EXP-POP-005）· **批量 best**：**1.039**（EXP-POP-006，`cand_mean_rev_1_g1_1_g2_2`，规则型 mean-reversion，**非** ML 主 baseline 替代）

## Plus v2 八条主线（M1–M8）

| 编号 | 名称 | 状态 | 关键交付 / 实验 | 文档 |
|------|------|------|-----------------|------|
| **M1** | 研究基线与实验规范 | ✅ | BaselineRegistry、`compare_experiments.py`；OOS **0.586** | [research_protocol.md](research_protocol.md) |
| **M2** | 数据源扩展 | ✅ | Alpha Vantage / Finnhub / FRED / SEC fetchers | [data_sources.md](data_sources.md) |
| **M3** | Memory / RAG v2 | ✅ | SQLite、HybridRetriever、index/query CLI | [database_setup.md](database_setup.md) |
| **M3.5** | 企业 RAG 扩展 | ✅ 并入 M9 | Postgres/pgvector/Neo4j（本地 EXP-025） | [database_setup.md](database_setup.md) |
| **M4** | LangGraph 工作流 | ✅ | ResearchWorkflow、sequential + langgraph | [langgraph_workflow.md](langgraph_workflow.md) |
| **M5** | 上下文 / LLM | ✅ | ContextBuilder、ResearchAgent；EXP-LLM-001 | [context_engineering.md](context_engineering.md) |
| **M5.5** | 本地 vLLM | 📋 按需 | OpenAI 兼容端点（a6000） | 项目plus设计 §M5.5 |
| **M6** | 文本信号 | ✅ | FinBERT smoke + WF OOS **0.563** vs **0.586** | [text_model_plan.md](text_model_plan.md) |
| **M7** | RL / GRPO 实验 | ✅ | TradingEnv、GRPO ranking；180 passed 本地+服务器 | [rl_plan.md](rl_plan.md) |
| **M8** | MCP / A2A 协议 | ✅ | MCP adapter、AgentCard；195 passed 本地+服务器 | [protocols.md](protocols.md) |

第五～六阶段见 [项目plus设计.md](../项目plus设计.md)（M7 RL 模拟 / M8 协议扩展，非实盘）。

## Plus v3 主线（M9–M13）

> 设计：[项目v3设计.md](../项目v3设计.md)

| 编号 | 名称 | 状态 | 关键交付 / 实验 | 文档 |
|------|------|------|-----------------|------|
| **M9** | 企业数据与数据库 | ✅ | Postgres 骨架；212 passed 本地+服务器 | [database_setup.md](database_setup.md) |
| **M10** | LLM 生产化 | ✅ | local_vllm；212 passed 本地+服务器 | [codex_prompt_M10.md](codex_prompt_M10.md) |
| **M11** | 竞争学习 / 策略种群 | ✅ | competitive CLI；225 双端（EXP-POP-002） | [competitive_learning.md](competitive_learning.md) |
| **M11.5** | 种群训练闭环 | ✅ | 237 双端（EXP-030/POP-003） | [population_training.md](population_training.md) |
| **M11.6** | 候选验证桥 | ✅ | 248 双端（EXP-031/POP-004） | [strategy_candidate_bridge.md](strategy_candidate_bridge.md) |
| **M11.7** | 候选 Walk-forward OOS | ✅ | 259 双端 + EXP-POP-005 真实 OOS | [strategy_candidate_oos.md](strategy_candidate_oos.md) |
| **M11.8** | 批量候选 OOS 比较 | ✅ | 266 双端 + EXP-POP-006（4/4 > 0.586） | [candidate_oos_batch.md](candidate_oos_batch.md) |
| **M12.1** | RL 训练实验 | ✅ 双端 | GRPOPolicyAgent、RLTrainingLoop；282 双端 + EXP-POP-007 | [rl_experiment.md](rl_experiment.md) |
| **M13** | 企业化编排 | 📋 | DAG scheduler | [protocols.md](protocols.md) |

## 阶段总览（v1 Prompt + Plus v2）

| 阶段 | 名称 | 状态 | 关键交付 |
|------|------|------|----------|
| 第零阶段 | 项目骨架 | ✅ | Prompt 1 |
| 第一阶段 | 量化核心 MVP | ✅ | Prompt 2–7、11–12、14 |
| 第二阶段 | 机器学习实验 | ✅ | Prompt 15–17、15b |
| 第二阶段扩展 | 基础风控 | ✅ | Prompt 18 |
| 第三阶段 | Agent 增强 | ✅ | Prompt 8–10、19 |
| 第四阶段 | Memory + RAG | ✅ | Prompt 20 |
| **Plus M1** | 研究基线 | ✅ | EXP-20260602-009/010，**102 passed** |
| **Plus M2** | 数据扩展 | ✅ | EXP-20260602-011/012，EXP-DATA-001 |
| **Plus M3** | Memory/RAG v2 | ✅ 本地 | EXP-20260602-013，**126 passed** |
| **Plus M4** | LangGraph 编排 | ✅ | EXP-20260602-015/016 |
| **Plus M5** | 上下文/LLM | ✅ | EXP-20260602-017/018，EXP-LLM-001，**150 passed** |
| **Plus M7** | RL 模拟 | ✅ | EXP-021/022，**180 passed** |
| 第五～六阶段 | 编排 / 协议 | ✅ | Plus **M8** MCP/A2A（EXP-023/024） |

## Quant MAS v2：M1 研究基线

> 设计细节见 [项目plus设计.md §M1](../项目plus设计.md#m1研究基线与实验规范)；实验规范见 [docs/research_protocol.md](research_protocol.md)。

### 目标

建立统一实验基线管理，**后续所有新实验必须与 EXP-20260602-008 Walk-forward OOS baseline 对比**后再写结论。

### 已交付（代码）

| 组件 | 路径 | 说明 |
|------|------|------|
| BaselineRegistry | `src/quant_mas/research/baseline.py` | `BaselineRun`、`add_baseline`、`compare_runs`、`get_best("oos.sharpe")` |
| MetricsTable | `src/quant_mas/research/metrics_table.py` | `collect_experiment_metrics`、`build_comparison_table` |
| CLI | `scripts/compare_experiments.py` | 从 ExperimentMemory 输出 `comparison.csv` / `comparison.md` |
| 实验规范 | `docs/research_protocol.md` | 必填字段、OOS 主指标、比较族 |
| 测试 | `tests/test_research_baseline.py` | 4 项（嵌套 metric、空 memory） |

### 状态

| 项目 | 状态 | 备注 |
|------|------|------|
| M1 模块代码 | ✅ | baseline / metrics_table / compare_experiments / research_protocol |
| `python scripts/compare_experiments.py --help` | ✅ | EXP-20260602-009 |
| `tests/test_research_baseline.py` | ✅ **4 passed** | 嵌套 metric、best baseline、CLI 输出 |
| 全量 pytest（本地） | ✅ **102 passed** | EXP-20260602-009 |
| 全量 pytest（服务器） | ✅ **102 passed**（1.64s） | EXP-20260602-010 |
| 服务器 `compare_experiments` | ✅ **5 rows** | `oos.sharpe` **0.586**（与 EXP-20260602-008 一致） |

### 下一步

M1/M2 已完成；**M3 本地 ✅**（见下两节）；下一步 **M4**。

### OOS 主 baseline（不可遗忘）

| 实验 | 主指标 | 用途 |
|------|--------|------|
| **EXP-20260602-008** | **OOS sharpe 0.586** | 论文 / 报告 **唯一主指标** |
| EXP-20260602-005 | sharpe 2.78（单段 ML） | ⚠️ in-sample，**禁止**与 OOS 混比 |
| EXP-20260601-004 | ma_cross sharpe ≈ 1.00 | 传统策略参考 |
| EXP-20260601-006 | test AUC 0.466 | ML 训练参考 |

## Quant MAS v2：M2 数据扩展

> 设计见 [项目plus设计.md §M2](../项目plus设计.md#m2数据源扩展)；用法见 [docs/data_sources.md](data_sources.md)。

| 组件 | 路径 |
|------|------|
| Fetcher 子包 | `src/quant_mas/data/fetchers/` |
| Registry | `DataSourceRegistry` |
| 新源 | Alpha Vantage、Finnhub、FRED、SEC EDGAR |
| 配置 | `configs/data_sources.yaml` |
| 测试 | `tests/test_data_sources.py`（**13 passed**） |

| 项目 | 状态 |
|------|------|
| 全量 pytest（本地） | ✅ **115 passed**（EXP-20260602-011） |
| test_data_sources（服务器） | ✅ **13 passed**（EXP-20260602-012） |
| API smoke（EXP-DATA-001） | ✅ FRED + Stooq + Alpha Vantage；Finnhub 免费 blocked |

`download_data.py` 新增：`--source alpha_vantage|finnhub|fred|sec_edgar`、`--series-id`、`--cik`。

## Quant MAS v2：M3 Memory/RAG v2

> 设计见 [项目plus设计.md §M3](../项目plus设计.md#m3数据库与-memory--rag-升级)；部署见 [database_setup.md](database_setup.md)。

| 组件 | 路径 |
|------|------|
| MemoryStore | `memory/store_base.py`、`json_store.py`、`sqlite_store.py`、`factory.py` |
| RAG | `rag/embedding_client.py`、`in_memory_vector_store.py`、`hybrid_retriever.py` |
| 配置 | `configs/memory.yaml` |
| CLI | `index_documents.py`、`query_memory.py` |
| 测试 | `tests/test_memory_store_v2.py`（**11 passed**） |

| 项目 | 状态 |
|------|------|
| 全量 pytest（本地） | ✅ **126 passed**（EXP-20260602-013） |
| test_memory_rag（Prompt 20） | ✅ **11 passed**（未破坏） |
| 全量 pytest（服务器） | ✅ **126 passed**（EXP-20260602-014） |
| index/query CLI `--help` | ✅ |

## Prompt 任务状态

- [x] Prompt 1–10：骨架 → Agent Core
- [x] Prompt 11–12：端到端 pipeline + 测试
- [x] Prompt 13：文档收口（2026-06-01，EXP-20260601-015）
- [x] Prompt 14：服务器部署脚本
- [x] Prompt 15–17、15b：ML 训练 / 回测 / walk-forward
- [x] Prompt 18：基础风控
- [x] Prompt 19：Supervisor 7 类路由
- [x] Prompt 20：Memory + RAG
- [x] **Plus M1**：研究基线与实验规范（EXP-20260602-009/010）
- [x] **Plus M2**：多数据源扩展（EXP-20260602-011/012，EXP-DATA-001）
- [x] **Plus M3**：Memory/RAG v2（EXP-20260602-013/014）
- [x] **Plus M4**：LangGraph ResearchWorkflow（EXP-20260602-015/016；**137+1 skip**，含 orchestration **138 passed**）

## Quant MAS v2：M4 LangGraph

> [langgraph_workflow.md](langgraph_workflow.md)

| 项目 | 状态 |
|------|------|
| sequential dry-run 6 节点 | ✅ |
| langgraph dry-run 6 节点 | ✅ 服务器 EXP-016 |
| test_langgraph_workflow | ✅ 11+1 skip（核心）/ **12 passed**（含 orchestration） |
| 全量 pytest（本地） | ✅ **137+1 skip** / **138 passed**（含 orchestration） |
| 全量 pytest（服务器） | ✅ langgraph invoke + dry-run（EXP-016 @ `c0fa5e3`） |

- [x] **Plus M5**：Context + ResearchAgent + 可选 LLM（EXP-20260602-017，**150+1 warning**）

## Quant MAS v2：M5 上下文/LLM

> [context_engineering.md](context_engineering.md)

| 项目 | 状态 |
|------|------|
| ContextBuilder + compression | ✅ |
| ResearchAgent / ReportResult | ✅ |
| resolve_llm_client（默认 Mock） | ✅ |
| test_context_engineering | ✅ 12 passed, 1 warning |
| 全量 pytest（本地） | ✅ **150 passed, 1 warning** |
| 全量 pytest（服务器） | ✅ **150 passed**（7.24s，EXP-018 @ `43c812a`） |
| DeepSeek ResearchAgent smoke | ✅ EXP-LLM-001（openai_compatible） |

## 当前 pytest 状态

| 环境 | Python | 结果 | 日期 | 实验 |
|------|--------|------|------|------|
| 本地 Windows | 3.11+ | **282 passed** | 2026-06-04 | EXP-20260602-034 |
| 服务器 a6000-9961 | 3.11.15 | **282 passed** | 2026-06-04 | EXP-POP-007 @ `e291cf9` |

命令：`python -m pytest -v`（勿裸敲 `pytest` / `pip`）。

## 当前可用 CLI

```powershell
python scripts/download_data.py --help
python scripts/build_features.py --help
python scripts/run_backtest.py --help
python scripts/train_model.py --help
python scripts/generate_report.py --help
python scripts/run_agent.py --help
python scripts/run_pipeline.py --help
python scripts/run_ml_backtest.py --help
python scripts/run_walk_forward.py --help
python scripts/compare_experiments.py --help
python scripts/index_documents.py --help
python scripts/query_memory.py --help
python scripts/run_rl_baseline.py --help
python scripts/run_competitive_experiment.py --help
python scripts/run_population_training.py --help
python scripts/export_population_candidates.py --help
python scripts/validate_candidate_oos.py --help
python scripts/batch_validate_candidates.py --help
python scripts/export_agent_cards.py --help
```

## 当前已实现能力

### Quant Engine

- 数据：Parquet、Stooq/yfinance/auto、**Alpha Vantage / Finnhub / FRED / SEC**（Plus M2）、OHLCV 校验
- 特征：技术指标、future label、按 symbol 分组
- 策略 / 回测：MA Cross、MLSignalStrategy、walk-forward OOS
- 模型：LightGBM（CPU + GPU/CUDA）
- 风控：RiskLimits、持仓裁剪/拒绝、回撤守卫

### Agent Layer

- 7 个 Quant Tools + Supervisor 规则路由（中英文关键词）
- 路由：ml_backtest / risk_check / pipeline / backtest / train_model / report / data_summary

### Memory / RAG

- ExperimentMemory：get / search / sort_by_metric / find_best（含嵌套 metric）
- TradeMemory：JSONL 空壳
- SimpleRetriever：关键词检索 docs（无向量库、无 LLM）

### Research Layer（Plus M1）

- BaselineRegistry / BaselineRun：命名 baseline 与实验 run 的统一比较
- MetricsTable：`collect_experiment_metrics` → `build_comparison_table`
- `compare_experiments.py`：从 ExperimentMemory 导出 CSV / Markdown 比较表
- **规则**：新实验结论须与 **EXP-20260602-008 OOS sharpe 0.586** 对比（见 `research_protocol.md`）

## 服务器真实实验（研究用）

| 实验 | 关键结果 | 备注 |
|------|----------|------|
| EXP-20260601-004 | Stooq 6033 rows；ma_cross sharpe ≈ 1.00 | 真实 pipeline |
| EXP-20260601-006 | CPU LightGBM test AUC 0.466 | 过拟合基线 |
| EXP-20260602-004 | GPU LightGBM device=cuda | 见 M-010 |
| EXP-20260602-005 | ML 单段回测 sharpe **2.78** | **非 OOS，勿混用** |
| EXP-20260602-008 | Walk-forward **OOS sharpe 0.586** | **报告主指标** |
| EXP-TEXT-001 | FinBERT smoke（ModelScope） | 200 signals；6033 行 features 中 134 非零 |
| EXP-TEXT-WF-001 | Walk-forward + text | OOS sharpe **0.563** vs baseline **0.586**（exploratory） |
| EXP-POP-005 | 单候选 OOS（M11.7） | `cand_mean_rev_1` **oos.sharpe 1.036** vs **0.586**（77 窗） |
| EXP-POP-007 | RL training smoke（M12.1） | **simulation.sharpe_mean 6.31**（**≠ OOS 0.586**） |
| EXP-POP-006 | 批量候选 OOS（M11.8） | 4/4 超 baseline；best **1.039** |

## 研究解读

1. 单段 ML 回测 sharpe 2.78 ≫ walk-forward OOS sharpe 0.586 → **论文/报告以 OOS 为准**。
2. OOS auc_mean 0.472 与 val/test AUC ≈ 0.46–0.48 一致；模型调参留作后续研究。
3. Agent 可编排 ML 回测、风控、pipeline；Memory/RAG 可检索历史实验与文档。
4. **Plus M1**：任何新实验写入 ExperimentMemory 后，须用 `compare_experiments.py` 生成比较表，并与 **EXP-20260602-008** 对照后再下结论。
5. **Plus M6 text**：EXP-TEXT-WF-001 在 200/6033 覆盖 + fillna(0) 下 OOS sharpe **略低于** baseline；属 smoke 探索，需扩大新闻覆盖后再评估。

## Quant MAS v2：M6 文本信号

> [text_model_plan.md](text_model_plan.md) · [codex_prompt_M6.md](codex_prompt_M6.md)

| 项目 | 状态 |
|------|------|
| text/ schema + mock classifier | ✅ |
| text_signals merge + leakage 检查 | ✅ |
| train_text_model.py（mock dry-run） | ✅ |
| test_text_signals | ✅ **11 passed** |
| 全量 pytest（本地） | ✅ **161 passed** |
| 全量 pytest（服务器） | ✅ **161 passed**（9.20s，EXP-020 @ `b9de2f2`） |
| EXP-TEXT-001 FinBERT smoke | ✅ ModelScope 本地 FinBERT，200 signals |
| EXP-TEXT-WF-001 walk-forward | ✅ oos.sharpe **0.563** vs baseline **0.586**（exploratory） |

## Quant MAS v2：M7 RL 模拟

> [rl_plan.md](rl_plan.md) · [codex_prompt_M7.md](codex_prompt_M7.md)

| 项目 | 状态 |
|------|------|
| TradingEnv + next-bar open 执行 | ✅ |
| Random / BuyHold / MLCopy policies | ✅ |
| GRPO-style group-relative ranking | ✅ |
| run_rl_baseline.py --dry-run | ✅ |
| run_competitive_experiment.py --dry-run | ✅ EXP-POP-001/002 |
| run_population_training.py --dry-run | ✅ EXP-030/POP-003 双端 |
| test_trading_env | ✅ **13 passed** |
| test_grpo_experiment | ✅ **6 passed** |
| 全量 pytest（本地） | ✅ **180 passed** |
| 全量 pytest（服务器） | ✅ **180 passed**（10.15s，EXP-022 @ `d8ece63`） |

## Quant MAS v2：M8 MCP / A2A

> [protocols.md](protocols.md) · [codex_prompt_M8.md](codex_prompt_M8.md)

| 项目 | 状态 |
|------|------|
| MCPToolSpec / policy / adapter | ✅ |
| deny shell/broker/order/secrets | ✅ |
| AgentCard（Supervisor/Research/Report） | ✅ |
| export_agent_cards.py | ✅ |
| test_protocols | ✅ **15 passed** |
| 全量 pytest（本地） | ✅ **195 passed** |
| 全量 pytest（服务器） | ✅ **212 passed**（11.39s，EXP-028 @ `3fd32e0`） |
| 服务器 Postgres 真实连接 | ✅ EXP-026（6 exp, 443 chunks, OOS 0.586） |

## Quant MAS v3：M9 企业 DB

> [database_setup.md](database_setup.md) · [项目v3设计.md](../项目v3设计.md) §M9

| 项目 | 状态 |
|------|------|
| PostgresMemoryStore + oos.sharpe 嵌套查询 | ✅ |
| PgVectorStore upsert/search/delete | ✅ |
| Neo4jGraphStore 骨架 | ✅ |
| factory json \| sqlite \| postgres | ✅ |
| query_memory / index_documents CLI | ✅ |
| test_memory_enterprise | ✅ **12 passed** |
| 全量 pytest（本地+服务器） | ✅ **212 passed**（EXP-028，11.39s） |
| 服务器 Postgres 真实连接 | ✅ EXP-026 |

## Quant MAS v3：M10 LLM

> [context_engineering.md](context_engineering.md) · [codex_prompt_M10.md](codex_prompt_M10.md)

| 项目 | 状态 |
|------|------|
| local_vllm provider | ✅ |
| ResearchAgent LLM 失败回退 Mock | ✅ |
| --provider CLI | ✅ |
| test_context_engineering | ✅ **17 passed** |
| 全量 pytest（本地） | ✅ **212 passed** |
| 全量 pytest（服务器） | ✅ **212 passed**（11.39s，EXP-028） |
| 服务器 / vLLM smoke | ✅ EXP-LLM-002（Qwen2.5-7B @ a6000） |

## Plus v2 收官（V2 结尾）

> 系统结构定稿见根目录 [`项目进度.md`](../项目进度.md) §Plus v2 收官；架构详图 [`architecture.md`](architecture.md)。

**设计原则**：Quant Engine 做计算；Agent Layer 做编排、解释与报告；LLM 不直接实盘下单。

**十层架构（定稿）**：Quant Engine → Tool Layer（7 tools）→ Agent Layer → Text（M6）→ RL Simulation（M7）→ Protocol（M8）→ Context（M5）→ Orchestration（M4）→ Memory/RAG（M3）→ Research（M1）。

**主数据流**：`download_data → features → train → walk_forward（OOS 0.586）→ ExperimentMemory → compare_experiments`。

**Agent 路径**：`SupervisorAgent → ToolRegistry → Quant Engine → metrics`。

**v2 关键指标**：pytest **195** · OOS sharpe **0.586** · text OOS **0.563**（exploratory）· RL `simulation.*` 不与 OOS 混比。

**v2 不做**：实盘 broker、外部 MCP server、ShellTool。

## 后续工作（v2 之后）

- ~~**M10 本地/服务器 pytest**~~ ✅ EXP-027/028（212）
- **M9 服务器 DB smoke**：✅ EXP-026（2026-06-03）
- ~~**EXP-LLM-002**~~ ✅（2026-06-03，local_vllm + ResearchAgent）
- ~~**M11.8 服务器批量 OOS**~~ ✅ EXP-POP-006（266 pytest；best **1.039**）
- ~~**M12.1 本地 RL training loop**~~ ✅ EXP-034（**282 pytest**）
- ~~**M12.1 服务器 RL smoke**~~ ✅ EXP-POP-007 / EXP-RL-003
- **M12.2** policy export bridge
- **EXP-TEXT-WF-002**
