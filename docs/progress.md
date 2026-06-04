# Quant MAS ????

?????2026-06-04?**EXP-TEXT-WF-003 ?** � ???????? � M12.4 ???

**Plus v2**?M1?M8 ? � **v3 M9?M12.4** ? ?? � RL observation-aware policy ???

**pytest ??**?**349 passed** ?? + ??? � **?????**?**0.586**?EXP-008?� **RL feature_linear OOS**?**0.387**?EXP-POP-010 ablation?� **RL logits OOS**?**0.0**?EXP-POP-009?

## Plus v2 ?????M1?M8?

| ?? | ?? | ?? | ???? / ?? | ?? |
|------|------|------|-----------------|------|
| **M1** | ????????? | ? | BaselineRegistry?`compare_experiments.py`?OOS **0.586** | [research_protocol.md](research_protocol.md) |
| **M2** | ????? | ? | Alpha Vantage / Finnhub / FRED / SEC fetchers | [data_sources.md](data_sources.md) |
| **M3** | Memory / RAG v2 | ? | SQLite?HybridRetriever?index/query CLI | [database_setup.md](database_setup.md) |
| **M3.5** | ?? RAG ?? | ? ?? M9 | Postgres/pgvector/Neo4j??? EXP-025? | [database_setup.md](database_setup.md) |
| **M4** | LangGraph ??? | ? | ResearchWorkflow?sequential + langgraph | [langgraph_workflow.md](langgraph_workflow.md) |
| **M5** | ??? / LLM | ? | ContextBuilder?ResearchAgent?EXP-LLM-001 | [context_engineering.md](context_engineering.md) |
| **M5.5** | ?? vLLM | ?? ?? | OpenAI ?????a6000? | ??plus?? �M5.5 |
| **M6** | ???? | ? | FinBERT smoke **0.563** � ?? **0.579** � ?? **0.565** vs **0.586** | [text_model_plan.md](text_model_plan.md) |
| **M7** | RL / GRPO ?? | ? | TradingEnv?GRPO ranking?180 passed ??+??? | [rl_plan.md](rl_plan.md) |
| **M8** | MCP / A2A ?? | ? | MCP adapter?AgentCard?195 passed ??+??? | [protocols.md](protocols.md) |

??????? [??plus??.md](../??plus??.md)?M7 RL ?? / M8 ??????????

## Plus v3 ???M9?M13?

> ???[??v3??.md](../??v3??.md)

| ?? | ?? | ?? | ???? / ?? | ?? |
|------|------|------|-----------------|------|
| **M9** | ???????? | ? | Postgres ???212 passed ??+??? | [database_setup.md](database_setup.md) |
| **M10** | LLM ??? | ? | local_vllm?212 passed ??+??? | [codex_prompt_M10.md](codex_prompt_M10.md) |
| **M11** | ???? / ???? | ? | competitive CLI?225 ???EXP-POP-002? | [competitive_learning.md](competitive_learning.md) |
| **M11.5** | ?????? | ? | 237 ???EXP-030/POP-003? | [population_training.md](population_training.md) |
| **M11.6** | ????? | ? | 248 ???EXP-031/POP-004? | [strategy_candidate_bridge.md](strategy_candidate_bridge.md) |
| **M11.7** | ?? Walk-forward OOS | ? | 259 ?? + EXP-POP-005 ?? OOS | [strategy_candidate_oos.md](strategy_candidate_oos.md) |
| **M11.8** | ???? OOS ?? | ? | 266 ?? + EXP-POP-006?4/4 > 0.586? | [candidate_oos_batch.md](candidate_oos_batch.md) |
| **M12.1** | RL ???? | ? ?? | GRPOPolicyAgent?RLTrainingLoop?282 ?? + EXP-POP-007 | [rl_experiment.md](rl_experiment.md) |
| **M12.2** | RL ????? | ? ?? | policy_state ? StrategyCandidate?EXP-POP-008 | [rl_policy_export.md](rl_policy_export.md) |
| **M12.3** | RL ?? OOS ?? | ? ?? | `grpo_policy` ? walk-forward OOS?EXP-POP-009 | [rl_policy_export.md](rl_policy_export.md) �M12.3 |
| **M12.4** | Observation-aware RL | ? ?? | EXP-036 / **EXP-POP-010**?OOS **0.387** | [rl_observation_policy.md](rl_observation_policy.md) |
| **M13** | ????? | ?? | DAG scheduler | [protocols.md](protocols.md) |

## ?????v1 Prompt + Plus v2?

| ?? | ?? | ?? | ???? |
|------|------|------|----------|
| ???? | ???? | ? | Prompt 1 |
| ???? | ???? MVP | ? | Prompt 2?7?11?12?14 |
| ???? | ?????? | ? | Prompt 15?17?15b |
| ?????? | ???? | ? | Prompt 18 |
| ???? | Agent ?? | ? | Prompt 8?10?19 |
| ???? | Memory + RAG | ? | Prompt 20 |
| **Plus M1** | ???? | ? | EXP-20260602-009/010?**102 passed** |
| **Plus M2** | ???? | ? | EXP-20260602-011/012?EXP-DATA-001 |
| **Plus M3** | Memory/RAG v2 | ? ?? | EXP-20260602-013?**126 passed** |
| **Plus M4** | LangGraph ?? | ? | EXP-20260602-015/016 |
| **Plus M5** | ???/LLM | ? | EXP-20260602-017/018?EXP-LLM-001?**150 passed** |
| **Plus M7** | RL ?? | ? | EXP-021/022?**180 passed** |
| ?????? | ?? / ?? | ? | Plus **M8** MCP/A2A?EXP-023/024? |

## Quant MAS v2?M1 ????

> ????? [??plus??.md �M1](../??plus??.md#m1?????????)?????? [docs/research_protocol.md](research_protocol.md)?

### ??

???????????**?????????? EXP-20260602-008 Walk-forward OOS baseline ??**??????

### ???????

| ?? | ?? | ?? |
|------|------|------|
| BaselineRegistry | `src/quant_mas/research/baseline.py` | `BaselineRun`?`add_baseline`?`compare_runs`?`get_best("oos.sharpe")` |
| MetricsTable | `src/quant_mas/research/metrics_table.py` | `collect_experiment_metrics`?`build_comparison_table` |
| CLI | `scripts/compare_experiments.py` | ? ExperimentMemory ?? `comparison.csv` / `comparison.md` |
| ???? | `docs/research_protocol.md` | ?????OOS ??????? |
| ?? | `tests/test_research_baseline.py` | 4 ???? metric?? memory? |

### ??

| ?? | ?? | ?? |
|------|------|------|
| M1 ???? | ? | baseline / metrics_table / compare_experiments / research_protocol |
| `python scripts/compare_experiments.py --help` | ? | EXP-20260602-009 |
| `tests/test_research_baseline.py` | ? **4 passed** | ?? metric?best baseline?CLI ?? |
| ?? pytest???? | ? **102 passed** | EXP-20260602-009 |
| ?? pytest????? | ? **102 passed**?1.64s? | EXP-20260602-010 |
| ??? `compare_experiments` | ? **5 rows** | `oos.sharpe` **0.586**?? EXP-20260602-008 ??? |

### ???

M1/M2 ????**M3 ?? ?**?????????? **M4**?

### OOS ? baseline??????

| ?? | ??? | ?? |
|------|--------|------|
| **EXP-20260602-008** | **OOS sharpe 0.586** | ?? / ?? **?????** |
| EXP-20260602-005 | sharpe 2.78??? ML? | ?? in-sample?**??**? OOS ?? |
| EXP-20260601-004 | ma_cross sharpe ? 1.00 | ?????? |
| EXP-20260601-006 | test AUC 0.466 | ML ???? |

## Quant MAS v2?M2 ????

> ??? [??plus??.md �M2](../??plus??.md#m2?????)???? [docs/data_sources.md](data_sources.md)?

| ?? | ?? |
|------|------|
| Fetcher ?? | `src/quant_mas/data/fetchers/` |
| Registry | `DataSourceRegistry` |
| ?? | Alpha Vantage?Finnhub?FRED?SEC EDGAR |
| ?? | `configs/data_sources.yaml` |
| ?? | `tests/test_data_sources.py`?**13 passed**? |

| ?? | ?? |
|------|------|
| ?? pytest???? | ? **115 passed**?EXP-20260602-011? |
| test_data_sources????? | ? **13 passed**?EXP-20260602-012? |
| API smoke?EXP-DATA-001? | ? FRED + Stooq + Alpha Vantage?Finnhub ?? blocked |

`download_data.py` ???`--source alpha_vantage|finnhub|fred|sec_edgar`?`--series-id`?`--cik`?

## Quant MAS v2?M3 Memory/RAG v2

> ??? [??plus??.md �M3](../??plus??.md#m3????-memory--rag-??)???? [database_setup.md](database_setup.md)?

| ?? | ?? |
|------|------|
| MemoryStore | `memory/store_base.py`?`json_store.py`?`sqlite_store.py`?`factory.py` |
| RAG | `rag/embedding_client.py`?`in_memory_vector_store.py`?`hybrid_retriever.py` |
| ?? | `configs/memory.yaml` |
| CLI | `index_documents.py`?`query_memory.py` |
| ?? | `tests/test_memory_store_v2.py`?**11 passed**? |

| ?? | ?? |
|------|------|
| ?? pytest???? | ? **126 passed**?EXP-20260602-013? |
| test_memory_rag?Prompt 20? | ? **11 passed**????? |
| ?? pytest????? | ? **126 passed**?EXP-20260602-014? |
| index/query CLI `--help` | ? |

## Prompt ????

- [x] Prompt 1?10??? ? Agent Core
- [x] Prompt 11?12???? pipeline + ??
- [x] Prompt 13??????2026-06-01?EXP-20260601-015?
- [x] Prompt 14????????
- [x] Prompt 15?17?15b?ML ?? / ?? / walk-forward
- [x] Prompt 18?????
- [x] Prompt 19?Supervisor 7 ???
- [x] Prompt 20?Memory + RAG
- [x] **Plus M1**???????????EXP-20260602-009/010?
- [x] **Plus M2**????????EXP-20260602-011/012?EXP-DATA-001?
- [x] **Plus M3**?Memory/RAG v2?EXP-20260602-013/014?
- [x] **Plus M4**?LangGraph ResearchWorkflow?EXP-20260602-015/016?**137+1 skip**?? orchestration **138 passed**?

## Quant MAS v2?M4 LangGraph

> [langgraph_workflow.md](langgraph_workflow.md)

| ?? | ?? |
|------|------|
| sequential dry-run 6 ?? | ? |
| langgraph dry-run 6 ?? | ? ??? EXP-016 |
| test_langgraph_workflow | ? 11+1 skip????/ **12 passed**?? orchestration? |
| ?? pytest???? | ? **137+1 skip** / **138 passed**?? orchestration? |
| ?? pytest????? | ? langgraph invoke + dry-run?EXP-016 @ `c0fa5e3`? |

- [x] **Plus M5**?Context + ResearchAgent + ?? LLM?EXP-20260602-017?**150+1 warning**?

## Quant MAS v2?M5 ???/LLM

> [context_engineering.md](context_engineering.md)

| ?? | ?? |
|------|------|
| ContextBuilder + compression | ? |
| ResearchAgent / ReportResult | ? |
| resolve_llm_client??? Mock? | ? |
| test_context_engineering | ? 12 passed, 1 warning |
| ?? pytest???? | ? **150 passed, 1 warning** |
| ?? pytest????? | ? **150 passed**?7.24s?EXP-018 @ `43c812a`? |
| DeepSeek ResearchAgent smoke | ? EXP-LLM-001?openai_compatible? |

## ?? pytest ??

| ?? | Python | ?? | ?? | ?? |
|------|--------|------|------|------|
| ?? Windows | 3.11+ | **331 passed** | 2026-06-04 | EXP-TEXT-WF-003 docs |
| ??? a6000-9961 | 3.11.15 | **331 passed** | 2026-06-04 | EXP-TEXT-WF-003 OOS **0.565** @ `561e104` |

???`python -m pytest -v`???? `pytest` / `pip`??

## ???? CLI

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

## ???????

### Quant Engine

- ???Parquet?Stooq/yfinance/auto?**Alpha Vantage / Finnhub / FRED / SEC**?Plus M2??OHLCV ??
- ????????future label?? symbol ??
- ?? / ???MA Cross?MLSignalStrategy?walk-forward OOS
- ???LightGBM?CPU + GPU/CUDA?
- ???RiskLimits?????/???????

### Agent Layer

- 7 ? Quant Tools + Supervisor ????????????
- ???ml_backtest / risk_check / pipeline / backtest / train_model / report / data_summary

### Memory / RAG

- ExperimentMemory?get / search / sort_by_metric / find_best???? metric?
- TradeMemory?JSONL ??
- SimpleRetriever?????? docs??????? LLM?

### Research Layer?Plus M1?

- BaselineRegistry / BaselineRun??? baseline ??? run ?????
- MetricsTable?`collect_experiment_metrics` ? `build_comparison_table`
- `compare_experiments.py`?? ExperimentMemory ?? CSV / Markdown ???
- **??**???????? **EXP-20260602-008 OOS sharpe 0.586** ???? `research_protocol.md`?

## ????????????

| ?? | ???? | ?? |
|------|----------|------|
| EXP-20260601-004 | Stooq 6033 rows?ma_cross sharpe ? 1.00 | ?? pipeline |
| EXP-20260601-006 | CPU LightGBM test AUC 0.466 | ????? |
| EXP-20260602-004 | GPU LightGBM device=cuda | ? M-010 |
| EXP-20260602-005 | ML ???? sharpe **2.78** | **? OOS????** |
| EXP-20260602-008 | Walk-forward **OOS sharpe 0.586** | **?????** |
| EXP-TEXT-001 | FinBERT smoke?ModelScope? | 200 signals?6033 ? features ? 134 ?? |
| EXP-TEXT-WF-001 | Walk-forward + text | OOS sharpe **0.563** vs baseline **0.586**?exploratory?3.32% ??? |
| EXP-TEXT-WF-002 | Walk-forward + 100% text | OOS sharpe **0.579** vs baseline **0.586**?? **-0.007**?????? |
| EXP-TEXT-WF-003 | Walk-forward + ???? | OOS sharpe **0.565** vs baseline **0.586**?? **-0.021**?Finnhub 2.42% ??? |
| EXP-POP-005 | ??? OOS?M11.7? | `cand_mean_rev_1` **oos.sharpe 1.036** vs **0.586**?77 ?? |
| EXP-POP-007 | RL training smoke?M12.1? | **simulation.sharpe_mean 6.31**?**? OOS 0.586**? |
| EXP-POP-006 | ???? OOS?M11.8? | 4/4 ? baseline?best **1.039** |

## ????

1. ?? ML ?? sharpe 2.78 ? walk-forward OOS sharpe 0.586 ? **??/??? OOS ??**?
2. OOS auc_mean 0.472 ? val/test AUC ? 0.46?0.48 ??????????????
3. Agent ??? ML ??????pipeline?Memory/RAG ???????????
4. **Plus M1**???????? ExperimentMemory ???? `compare_experiments.py` ???????? **EXP-20260602-008** ????????
5. **Plus M6 text**?EXP-TEXT-WF-001?3.32%?**0.563**?EXP-TEXT-WF-002?100% ???**0.579**?EXP-TEXT-WF-003?Finnhub ?? 2.42%?**0.565**?????????? **0.586**??????????? ? WF-001???? WF-002 ?????

## Quant MAS v2?M6 ????

> [text_model_plan.md](text_model_plan.md) � [codex_prompt_M6.md](codex_prompt_M6.md)

| ?? | ?? |
|------|------|
| text/ schema + mock classifier | ? |
| text_signals merge + leakage ?? | ? |
| train_text_model.py?mock dry-run? | ? |
| test_text_signals | ? **11 passed** |
| ?? pytest???? | ? **161 passed** |
| ?? pytest????? | ? **161 passed**?9.20s?EXP-020 @ `b9de2f2`? |
| EXP-TEXT-001 FinBERT smoke | ? ModelScope ?? FinBERT?200 signals |
| EXP-TEXT-WF-001 walk-forward | ? oos.sharpe **0.563** vs baseline **0.586**?exploratory? |

## Quant MAS v2?M7 RL ??

> [rl_plan.md](rl_plan.md) � [codex_prompt_M7.md](codex_prompt_M7.md)

| ?? | ?? |
|------|------|
| TradingEnv + next-bar open ?? | ? |
| Random / BuyHold / MLCopy policies | ? |
| GRPO-style group-relative ranking | ? |
| run_rl_baseline.py --dry-run | ? |
| run_competitive_experiment.py --dry-run | ? EXP-POP-001/002 |
| run_population_training.py --dry-run | ? EXP-030/POP-003 ?? |
| test_trading_env | ? **13 passed** |
| test_grpo_experiment | ? **6 passed** |
| ?? pytest???? | ? **180 passed** |
| ?? pytest????? | ? **180 passed**?10.15s?EXP-022 @ `d8ece63`? |

## Quant MAS v2?M8 MCP / A2A

> [protocols.md](protocols.md) � [codex_prompt_M8.md](codex_prompt_M8.md)

| ?? | ?? |
|------|------|
| MCPToolSpec / policy / adapter | ? |
| deny shell/broker/order/secrets | ? |
| AgentCard?Supervisor/Research/Report? | ? |
| export_agent_cards.py | ? |
| test_protocols | ? **15 passed** |
| ?? pytest???? | ? **195 passed** |
| ?? pytest????? | ? **212 passed**?11.39s?EXP-028 @ `3fd32e0`? |
| ??? Postgres ???? | ? EXP-026?6 exp, 443 chunks, OOS 0.586? |

## Quant MAS v3?M9 ?? DB

> [database_setup.md](database_setup.md) � [??v3??.md](../??v3??.md) �M9

| ?? | ?? |
|------|------|
| PostgresMemoryStore + oos.sharpe ???? | ? |
| PgVectorStore upsert/search/delete | ? |
| Neo4jGraphStore ?? | ? |
| factory json \| sqlite \| postgres | ? |
| query_memory / index_documents CLI | ? |
| test_memory_enterprise | ? **12 passed** |
| ?? pytest???+???? | ? **212 passed**?EXP-028?11.39s? |
| ??? Postgres ???? | ? EXP-026 |

## Quant MAS v3?M10 LLM

> [context_engineering.md](context_engineering.md) � [codex_prompt_M10.md](codex_prompt_M10.md)

| ?? | ?? |
|------|------|
| local_vllm provider | ? |
| ResearchAgent LLM ???? Mock | ? |
| --provider CLI | ? |
| test_context_engineering | ? **17 passed** |
| ?? pytest???? | ? **212 passed** |
| ?? pytest????? | ? **212 passed**?11.39s?EXP-028? |
| ??? / vLLM smoke | ? EXP-LLM-002?Qwen2.5-7B @ a6000? |

## Plus v2 ???V2 ???

> ?????????? [`????.md`](../????.md) �Plus v2 ??????? [`architecture.md`](architecture.md)?

**????**?Quant Engine ????Agent Layer ??????????LLM ????????

**????????**?Quant Engine ? Tool Layer?7 tools?? Agent Layer ? Text?M6?? RL Simulation?M7?? Protocol?M8?? Context?M5?? Orchestration?M4?? Memory/RAG?M3?? Research?M1??

**????**?`download_data ? features ? train ? walk_forward?OOS 0.586?? ExperimentMemory ? compare_experiments`?

**Agent ??**?`SupervisorAgent ? ToolRegistry ? Quant Engine ? metrics`?

**v2 ????**?pytest **195** � OOS sharpe **0.586** � text OOS **0.563**?exploratory?� RL `simulation.*` ?? OOS ???

**v2 ??**??? broker??? MCP server?ShellTool?

## ?????v2 ???

- ~~**M10 ??/??? pytest**~~ ? EXP-027/028?212?
- **M9 ??? DB smoke**?? EXP-026?2026-06-03?
- ~~**EXP-LLM-002**~~ ??2026-06-03?local_vllm + ResearchAgent?
- ~~**M11.8 ????? OOS**~~ ? EXP-POP-006?266 pytest?best **1.039**?
- ~~**M12.1 ?? RL training loop**~~ ? EXP-034?**282 pytest**?
- ~~**M12.1 ??? RL smoke**~~ ? EXP-POP-007 / EXP-RL-003
- ~~**M12.2 ?? export bridge**~~ ? EXP-035?**294?296 pytest**?
- ~~**M12.2 ??? export**~~ ? EXP-POP-008
- ~~**M12.3 RL ?? OOS**~~ ? EXP-POP-009?**296 pytest**?`oos.sharpe=0.0` ??? ablation?
- ~~**M12.4 Observation-aware RL policy**~~ ? ?? EXP-036 / **EXP-POP-010**?OOS **0.387**?
- ~~**EXP-TEXT-WF-002** coverage audit tool~~ ? EXP-TEXT-WF-002-PREP?**314 pytest**?
- ~~**EXP-TEXT-WF-002** ??? walk-forward OOS~~ ? oos.sharpe **0.579** vs **0.586**
- ~~**EXP-TEXT-WF-003** ??? walk-forward OOS~~ ? oos.sharpe **0.565** vs **0.586**
- M13 ??

## Quant MAS v3?M12.4 Observation-aware RL

M12.4 adds a feature-linear policy path for RL candidates. It reads deterministic market observations (`position_weight`, `last_return`, `rolling_vol_5`, `volume`, `close`) and exports `agent_type="feature_linear_policy"` candidates for the existing M11.7/M11.8 OOS validation hooks.

Validation status:

| Item | Status |
|------|--------|
| Feature policy tests | ? **14 passed** |
| RL training/export regression | ? **28 passed** |
| Candidate OOS regression | ? **20 passed** |
| Full pytest | ? **308 passed** |
| Server OOS smoke | ? **EXP-POP-010**?`oos.sharpe=0.387`? |

Boundary: M12.4 training still writes only `training.*` / `simulation.*`; `oos.*` remains owned by M11.7/M11.8.

Research interpretation: M12.4 improves the RL ablation from all-cash (`oos.sharpe=0.0`) to state-dependent exposure (`oos.sharpe=0.387`), but it remains below the ML walk-forward baseline (`0.586`). Keep it as an RL mechanism ablation, not the paper main result.

Recommended next steps:

1. **EXP-TEXT-002** (optional): LoRA fine-tune FinBERT on domain news; rerun walk-forward.
2. **M13 orchestration**: consolidate repeated research flows into a controlled DAG/scheduler.
3. **Optional RL ablation**: longer feature-linear RL training with multi-seed export + M11.8 batch OOS.

EXP-TEXT-WF-003 completed real Finnhub news alignment and walk-forward OOS (`oos.sharpe = 0.565`, 2.42% coverage). See [real_news_text_experiment.md](real_news_text_experiment.md).

## M13 planning update: enterprise orchestration roadmap

M13 is split into four incremental stages so implementation can stay small and testable.

| Stage | Status | Purpose | Document |
|------|--------|---------|----------|
| **M13.0 MCP Scheduler Minimal** | ✅ | Internal dry-run scheduler, audit JSONL, ToolPolicy | [mcp_protocol.md](mcp_protocol.md) |
| **M13.1 Pipeline Recipe Scheduler** | ✅ | YAML recipes for ML/Text/Population/RL | [mcp_protocol.md](mcp_protocol.md) |
| **M13.2 LangGraph Extended DAG** | Later | Optional LangGraph backend for population, RL, and batch walk-forward nodes | [mcp_protocol.md](mcp_protocol.md) |
| **M13.3 Paper Artifact Export** | Later | Paper-grade result tables, ablation tables, and audit package | [mcp_protocol.md](mcp_protocol.md) |

Current next target: **M13.2** LangGraph extended DAG (EXP-M13-002 dual-end ? @ `2610612`).

### M13.0 completion note（EXP-M13-001 ✅ 双端）

| 环境 | 结果 |
|------|------|
| 本地 | **342 passed** |
| 服务器 a6000-9961 | **342 passed**（53.99s）；pipeline dry-run ✅ @ 605fa66 |

Delivered: agent_communication / audit_log / mcp_scheduler / run_mcp_pipeline / test_mcp_scheduler（11/11）

M13.0 remains dry-run only and does not create new OOS research metrics.

### M13.1 completion note（EXP-M13-002 ✅ 双端）

| 环境 | 结果 |
|------|------|
| 本地 | **349 passed**；4 yaml.example dry-run ✅ |
| 服务器 a6000-9961 | **349 passed**（54.00s）；4 yaml.example dry-run ✅ @ 2610612 |

Delivered: pipeline_recipe + 4 yaml.example + test_mcp_pipeline_recipes（7/7）

