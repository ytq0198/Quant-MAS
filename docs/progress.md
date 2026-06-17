# Quant MAS 进度追踪

更新时间：2026-06-09 · **M13 整体收口 ✅** · **v5 Enterprise Console ✅** · **361 pytest** 双端 · EXP-M13-001→004

**Plus v2**：M1–M8 ✅ · **v3 M9–M13** ✅（本地 + 服务器 smoke 双端验证）

**v5 全栈**：Job API · Help 指南页 · 权益曲线修复 · SRTP 汇报材料（31 页 Premium PPT + 讲解稿）

**论文主 baseline**：EXP-20260602-008 · **oos.sharpe = 0.586**（19 窗 walk-forward）

**pytest 基线**：**361 passed**（本地 + 服务器 a6000-9961 @ `6913dbf`）

---

## v5 Enterprise 与 SRTP 汇报（2026-06-09）

| 交付项 | 状态 | 说明 |
|--------|------|------|
| **POST /api/jobs** | ✅ | backtest / walk_forward_oos / paper_export 可执行 Job |
| **Help 页面** | ✅ | `frontend/src/pages/Help.tsx` + `helpGuide.ts`，中英文逐步指南 |
| **Overview 增强** | ✅ | Research Workflow 九步、OOS baseline KPI |
| **回测图表修复** | ✅ | 权益曲线 bar 归一化渲染（commit `e7e82c2`） |
| **Job 导入修复** | ✅ | `job_tasks._stringify_paths` 内联，避免 quant 包导入错误 |
| **PPT 汇报包** | ✅ | `Quant_MAS_ZJU_CS_Premium_PPT.html`（31 页 · 含架构图/UI 截图） |
| **讲解稿** | ✅ | `Quant_MAS_汇报讲解稿.md`（逐页口播 + MAS 编排专章） |
| **实验数据包** | ✅ | `docs/ppt_data/`（46 文件 · 2026-06-04 服务器导出） |
| **项目说明** | ✅ | `项目说明.md` — 量化研究 vs 实盘、首次回测 walkthrough |

**SRTP 阶段**：项目初期进展汇报（非结题）；主结论仍为 **oos.sharpe = 0.586**，禁止混用 in-sample ML 2.78。

**MAS 编排文档化**（Premium PPT Part I 07–11 页）：ToolRegistry · MCP/ToolPolicy · Supervisor/Research/Report · ResearchWorkflow 6 节点 DAG · MCPScheduler · ContextBuilder/RAG。

---

## Plus v2 模块状态（M1–M8）

| 模块 | 名称 | 状态 | 关键交付 |
|------|------|------|----------|
| **M1** | 研究基线与对比 | ✅ | BaselineRegistry、`compare_experiments.py` |
| **M2** | 多源数据 | ✅ | Alpha Vantage / Finnhub / FRED / SEC |
| **M3** | Memory / RAG v2 | ✅ | SQLite、HybridRetriever、index/query CLI |
| **M4** | LangGraph 工作流 | ✅ | ResearchWorkflow 6 节点 DAG |
| **M5** | 上下文 / LLM | ✅ | ContextBuilder、ResearchAgent |
| **M6** | 文本信号 | ✅ | FinBERT smoke + walk-forward 文本消融 |
| **M7** | RL / GRPO 骨架 | ✅ | TradingEnv、GRPO ranking |
| **M8** | MCP / A2A | ✅ | ToolPolicy、AgentCard 导出 |

详见 [项目plus设计.md](../项目plus设计.md)。

---

## Plus v3 模块状态（M9–M13）

> 设计文档：[项目v3设计.md](../项目v3设计.md) · 实验记录：[experiment_log.md](experiment_log.md)

| 模块 | 名称 | 状态 | pytest / EXP |
|------|------|------|--------------|
| **M9** | 企业级数据库 | ✅ | 212+ · EXP-025/026 |
| **M10** | LLM 生产化 | ✅ | local_vllm · EXP-LLM-002 |
| **M11** | 竞争学习 | ✅ | 225 · EXP-POP-002 |
| **M11.5** | 种群训练循环 | ✅ | 237 · EXP-POP-003 |
| **M11.6** | 策略候选桥接 | ✅ | 248 · EXP-POP-004 |
| **M11.7** | 候选 Walk-forward OOS | ✅ | 259 · EXP-POP-005（1.036 vs 0.586） |
| **M11.8** | 批量候选 OOS | ✅ | 266 · EXP-POP-006（best 1.039） |
| **M12.1** | RL 训练 loop | ✅ | 282 · EXP-POP-007（simulation only） |
| **M12.2** | RL policy 导出 | ✅ | 294 · EXP-POP-008 |
| **M12.3** | RL 候选 OOS | ✅ | 296 · EXP-POP-009（oos 0.0 ablation） |
| **M12.4** | Observation-aware RL | ✅ | 310 · EXP-POP-010（oos 0.387） |
| **M13.0** | MCP Scheduler | ✅ 双端 | 342 · EXP-M13-001 |
| **M13.1** | YAML Pipeline Recipe | ✅ 双端 | 349 · EXP-M13-002 |
| **M13.2** | LangGraph Recipe Backend | ✅ 双端 | 354 · EXP-M13-003 |
| **M13.3** | Paper Artifact Export | ✅ 双端 | 361 · EXP-M13-004 |

---

## M13 编排收口（2026-06-04）

| 阶段 | 交付 | 验证 |
|------|------|------|
| M13.0 | `mcp_scheduler.py`、audit JSONL、ToolPolicy | dry-run mock 通过 |
| M13.1 | 4 套 YAML recipe（ML/Text/Population/RL） | recipe 单测 7/7 |
| M13.2 | `--backend langgraph` + scheduler fallback | LangGraph 1.2.4 @ 服务器 |
| M13.3 | `export_paper_artifacts.py` → 6 类论文产物 | 真实 `experiments.json` 导出 ✅ |

**边界**：M13 只做编排、审计与论文级整理，**不产生新 OOS 结论**；与 M4 ResearchWorkflow / SupervisorAgent 并存。

详见 [mcp_protocol.md](mcp_protocol.md) · Codex：[codex_prompt_M13.md](codex_prompt_M13.md)

---

## 文本消融（M6 三线）

| 实验 | coverage | oos.sharpe | vs 0.586 |
|------|----------|------------|----------|
| EXP-TEXT-WF-001 | 3.32% | 0.563 | −0.023 |
| EXP-TEXT-WF-002 | 100% placeholder | 0.579 | −0.007 |
| EXP-TEXT-WF-003 | 2.42% 真实 Finnhub | **0.565** | −0.021 |

详见 [real_news_text_experiment.md](real_news_text_experiment.md)。

---

## 论文导出（M13.3）

```bash
python scripts/export_paper_artifacts.py \
  --memory-path outputs/reports/experiments.json \
  --audit-dir outputs/pipelines \
  --output-dir outputs/paper
```

产物：`paper_main_results.csv` · `paper_text_ablation.csv` · `paper_population_ablation.csv` · `paper_rl_ablation.csv` · `paper_experiment_index.md` · `audit_summary.json`

**规则**：主表仅 `oos.*`；simulation-only RL 不进主表；缺失值留空、不虚构。

---

## 下一步（M13 之后）

1. **论文撰写** — 基于 `outputs/paper/` 与 [论文初稿.md](../论文初稿.md)
2. **SRTP 汇报** — Premium PPT + 讲解稿；服务器 SSH 隧道演示 Web 控制台
3. **可选 EXP-TEXT-002** — LoRA 微调 FinBERT + walk-forward
4. **可选研究线** — 更长 RL 训练、多种子、Population 稳健性检验

---

## 相关文档

| 文档 | 说明 |
|------|------|
| [experiment_log.md](experiment_log.md) | 全部 EXP 验收记录 |
| [server_commands.md](server_commands.md) | 服务器 runbook |
| [research_protocol.md](research_protocol.md) | OOS 指标规范 |
| [architecture.md](architecture.md) | 架构说明 |
| [v5_enterprise_overview.md](v5_enterprise_overview.md) | v5 全栈与企业控制台 |
| [../项目说明.md](../项目说明.md) | 新手入门：量化研究 vs 实盘 |
| [../Quant_MAS_汇报讲解稿.md](../Quant_MAS_汇报讲解稿.md) | SRTP 汇报逐页讲解词 |
| [ppt_data/DATA_MANIFEST.md](ppt_data/DATA_MANIFEST.md) | PPT 实验数据清单 |
| [index.md](index.md) | 文档总入口 |
