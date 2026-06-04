# Quant MAS — Multi-Agent Quantitative Research Platform / 多智能体量化研究平台

> **Resume-ready** open-source platform for AI Agent & Quant research: deterministic pipelines, walk-forward OOS, Memory/RAG, and safe agent orchestration — **not a live-trading bot**.  
> 面向 **AI Agent / Quant / ML** 实习与科研申请者的开源项目：可运行、可回测、可训练、可记录 — **非实盘系统**。

[![GitHub](https://img.shields.io/badge/GitHub-ytq0198%2FQuant--MAS-181717?logo=github)](https://github.com/ytq0198/Quant-MAS)
[![Python](https://img.shields.io/badge/python-3.11+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Tests](https://img.shields.io/badge/tests-361%20passed-brightgreen)](docs/progress.md)
[![OOS Baseline](https://img.shields.io/badge/OOS%20Sharpe-0.586-blue)](docs/experiment_log.md)
[![M13](https://img.shields.io/badge/M13-orchestration%20%E2%9C%85-purple)](docs/mcp_protocol.md)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

---

## Table of Contents / 目录

- [Highlights / 项目亮点](#highlights--项目亮点)
- [Architecture / 系统架构](#architecture--系统架构)
- [Features / 功能概览](#features--功能概览)
- [Quick Start / 快速开始](#quick-start--快速开始)
- [CLI Examples / 命令示例](#cli-examples--命令示例)
- [Experiment Snapshot / 实验摘要](#experiment-snapshot--实验摘要)
- [Resume Usage / 简历写法](#resume-usage--简历写法)
- [Project Structure / 项目结构](#project-structure--项目结构)
- [Documentation / 文档索引](#documentation--文档索引)
- [Roadmap / 路线图](#roadmap--路线图)
- [Contributing · License · Disclaimer / 贡献 · 许可 · 免责声明](#contributing--license--disclaimer--贡献--许可--免责声明)

---

## Highlights / 项目亮点

| Highlight | Detail |
|-----------|--------|
| **361 pytest** | Dual-end verified (local + a6000 server @ `6913dbf`) |
| **OOS Sharpe 0.586** | Paper ML baseline · EXP-20260602-008 · 19 walk-forward windows |
| **M13 complete** | YAML recipes · LangGraph backend · auditable paper export |
| **Safety boundary** | LLM agents orchestrate & explain — they **never** place live orders |

| 亮点 | 说明 |
|------|------|
| **361 pytest** | 本地 + a6000 服务器双端验证（@ `6913dbf`） |
| **OOS Sharpe 0.586** | 论文 ML 主基线 · EXP-20260602-008 · 19 窗 walk-forward |
| **M13 收口** | YAML recipe · LangGraph backend · 可审计论文导出 |
| **安全边界** | LLM 智能体仅编排与解释 — **绝不**直接下单 |

> Quant Engine **computes**. Agent Layer **explains, orchestrates, and reports**.  
> Quant Engine **做计算**；Agent Layer **做编排、解释与报告**。

**Status / 当前进度**：M1–M8 ✅ · v3 M9–M13 ✅ · Next / 下一步：paper writing（`outputs/paper/`）· optional LoRA / RL lines

---

## Architecture / 系统架构

![Quant MAS Architecture — Multi-Agent Quant Research Platform / 多智能体量化研究平台](architecture.png)

The diagram above shows six layers: **Interfaces & Inputs → Quant Engine → Tool Layer → MAS Agent Layer → Memory & RAG → Orchestration & Protocols**, plus the typical research flow and safety boundary on the right.

上图展示六层架构：**接口与输入 → 量化核心引擎 → 工具层 → 多智能体层 → 记忆与 RAG → 编排与协议**，以及底部典型研究流程与右侧安全原则。

| Layer | English | 中文 |
|-------|---------|------|
| **1. Interfaces & Inputs** | User & CLI, configs, market/macro data (Stooq, yfinance, Finnhub, FRED, SEC), research docs | 用户与命令行、配置、市场/宏观数据、研究文档 |
| **2. Quant Engine** | Data · Features · Models · Strategies · Backtest · Risk — deterministic computation only | 数据 · 特征 · 模型 · 策略 · 回测 · 风控 — 仅确定性计算 |
| **3. Tool Layer** | Seven callable tools exposed to agents (data summary, backtest, train, report, risk, ml_backtest, pipeline) | 七种可调用工具供智能体使用 |
| **4. MAS Agent Layer** | SupervisorAgent, ResearchAgent, ReportAgent, RiskAgent — research, planning, explanation | 监督、研究、报告、风控智能体 — 研究规划与解释 |
| **5. Memory & RAG** | ExperimentMemory, hybrid retriever, JSON/SQLite/Postgres, vector store (FAISS / pgvector) | 实验记忆、混合检索、JSON/SQLite/Postgres、向量库 |
| **6. Orchestration & Protocols** | LangGraph workflow, Context Engineering, LLM client (mock / OpenAI-compatible / local vLLM), MCP-style adapter | LangGraph 工作流、上下文工程、LLM 客户端、MCP 协议适配 |

**Typical research flow / 典型研究流程**  
Download Data → Build Features → Train Model → Backtest → Risk Check → Generate Report → Store Memory/RAG → Compare Experiments

**Safety principle / 安全原则**  
LLM agents do **NOT** place live trades directly. All signals must pass backtesting, risk checks, audit, and human approval.  
LLM 智能体**不**直接实盘下单。所有信号须经回测、风控、审计与人工确认。

Details / 详细设计：[docs/architecture.md](docs/architecture.md) · [docs/index.md](docs/index.md)

---

## Features / 功能概览

**Quant Engine / 量化引擎** — Parquet storage, OHLCV validation, features, MA Cross / LightGBM strategies, backtest, risk, walk-forward OOS  
Parquet 存储、OHLCV 校验、特征工程、均线/LightGBM 策略、回测、风控、walk-forward 样本外验证

**Agent Layer / 智能体层** — `ToolRegistry`, `SupervisorAgent` (rule routing), `ReportAgent`, `ResearchAgent` (mock-safe · optional local vLLM)  
工具注册、规则路由监督智能体、报告/研究智能体（默认 Mock · 可选本地 vLLM）

**Memory / RAG / 记忆与检索** — JSON · SQLite · Postgres · pgvector hybrid retrieval  
JSON · SQLite · Postgres · pgvector 混合检索

**Research extensions (v3) / 研究扩展（v3）**

| Track | Highlight | Key EXP | 说明 |
|-------|-----------|---------|------|
| Text signals | FinBERT walk-forward trilogy | WF-003 **0.565** vs **0.586** | 文本信号三线消融 |
| Population | Candidate → OOS bridge | POP-006 best **1.039** | 种群候选 → 样本外验证 |
| RL | Train → export → OOS ablation | POP-010 **0.387** (vs **0.0**) | RL 训练→导出→OOS 消融 |
| M13 orchestration | Scheduler + YAML + LangGraph + paper export | EXP-M13-001→004 | 企业级编排与论文导出 |

Paper rule / 论文规则：conclusions use **walk-forward OOS** only — see [docs/research_protocol.md](docs/research_protocol.md)  
论文级结论**仅**使用 walk-forward 样本外指标 — 见 [docs/research_protocol.md](docs/research_protocol.md)

---

## Quick Start / 快速开始

```bash
git clone https://github.com/ytq0198/Quant-MAS.git
cd Quant-MAS

python -m pip install -e .
python -m pytest -v                              # expect 361 passed
python -c "import quant_mas; print('Quant MAS ready')"
```

**Optional extras / 可选依赖**

```bash
python -m pip install -r requirements-data.txt    # market data fetchers / 行情抓取
python -m pip install -r requirements-ml.txt      # LightGBM
python -m pip install -e ".[orchestration]"       # LangGraph (M13.2)
python -m pip install -e ".[llm]"                 # HTTP LLM client
python -m pip install -e ".[text]"                # FinBERT (server manual)
```

**Verified baseline / 已验证基线**：**361 passed** dual-end（local + server @ `6913dbf`）  
本地 + 服务器双端 **361 项 pytest** 通过

---

## CLI Examples / 命令示例

<details>
<summary><strong>Walk-forward OOS / 样本外 walk-forward</strong> (paper baseline / 论文基线)</summary>

```bash
python scripts/run_walk_forward.py \
  --config configs/walk_forward.yaml \
  --storage-config configs/storage.yaml \
  --experiment-name local_walk_forward_demo
```

</details>

<details>
<summary><strong>M13 pipeline / M13 编排流水线</strong> (scheduler or LangGraph)</summary>

```bash
python scripts/run_mcp_pipeline.py --list-recipes
python scripts/run_mcp_pipeline.py --recipe configs/pipelines/ml_baseline.yaml.example --dry-run
python scripts/run_mcp_pipeline.py --backend langgraph \
  --recipe configs/pipelines/text_enhanced.yaml.example --dry-run
```

</details>

<details>
<summary><strong>Paper artifact export / 论文级导出</strong> (M13.3)</summary>

```bash
python scripts/export_paper_artifacts.py \
  --memory-path outputs/reports/experiments.json \
  --audit-dir outputs/pipelines \
  --output-dir outputs/paper
```

Produces 6 files / 产出 6 个文件：`paper_main_results.csv`, text/population/RL ablation CSVs, `paper_experiment_index.md`, `audit_summary.json`

</details>

<details>
<summary><strong>ResearchAgent / 研究解释智能体</strong> (mock-safe · server vLLM)</summary>

```bash
python scripts/run_research_agent.py \
  --task "Summarize OOS baseline EXP-20260602-008 (oos.sharpe ≈ 0.586)"
```

Server vLLM / 服务器 vLLM：see [docs/server_commands.md](docs/server_commands.md)

</details>

More examples / 更多示例：end-to-end pipeline, LightGBM, candidate OOS batch — [docs/server_commands.md](docs/server_commands.md)

---

## Experiment Snapshot / 实验摘要

| Result | Value | Notes |
|--------|-------|-------|
| **ML OOS baseline** | sharpe **0.586** | EXP-20260602-008 |
| **Text (real Finnhub)** | sharpe **0.565** | EXP-TEXT-WF-003 · 2.42% coverage |
| **Population best** | sharpe **1.039** | EXP-POP-006 · rule candidates |
| **RL feature-linear** | sharpe **0.387** | EXP-POP-010 · vs all-cash 0.0 |
| **M13 paper export** | 6 artifacts | EXP-M13-004 · `outputs/paper/` |
| **pytest** | **361 passed** | M13 closeout · dual-end |

| 结果 | 数值 | 说明 |
|------|------|------|
| **ML OOS 主基线** | sharpe **0.586** | EXP-20260602-008 |
| **文本（真实 Finnhub）** | sharpe **0.565** | EXP-TEXT-WF-003 · 2.42% 覆盖 |
| **种群最佳** | sharpe **1.039** | EXP-POP-006 · 规则候选 |
| **RL feature-linear** | sharpe **0.387** | EXP-POP-010 · 对比全现金 0.0 |
| **M13 论文导出** | 6 个产物 | EXP-M13-004 · `outputs/paper/` |
| **pytest** | **361 passed** | M13 收口 · 双端 |

Full log / 完整记录：[docs/experiment_log.md](docs/experiment_log.md)

---

## Resume Usage / 简历写法

**English**

> Built **Quant MAS**, a Python 3.11 multi-agent quant research platform with walk-forward OOS (baseline sharpe 0.586), Memory/RAG, Postgres/pgvector, local vLLM ResearchAgent, competitive learning & RL ablation chains, **M13 enterprise orchestration** (YAML recipes, LangGraph, paper export), and **361 passing pytest** — with strict safeguards preventing LLM agents from direct live trading.

**中文**

> 基于 Python 3.11 构建 **Quant MAS** 多智能体量化研究平台，完成 Walk-forward OOS（主基线 sharpe 0.586）、Memory/RAG、Postgres/pgvector、本地 vLLM ResearchAgent、竞争学习与 RL 消融链路、**M13 企业级编排**（YAML recipe、LangGraph、论文导出），维护 **361 项 pytest** 通过，明确 LLM Agent 不直接参与实盘下单。

See also / 另见：[项目进度.md](项目进度.md) · [论文初稿.md](论文初稿.md)

---

## Project Structure / 项目结构

```text
Quant-MAS/
├── src/quant_mas/       # core: data, features, models, backtest, agents, memory, rl, orchestration
├── scripts/             # CLI (+ export_paper_artifacts.py, run_mcp_pipeline.py)
├── configs/             # YAML (+ pipelines/*.yaml.example)
├── tests/               # 361 pytest cases
├── docs/                # architecture, progress, server_commands, mcp_protocol
├── architecture.png     # bilingual architecture diagram / 双语架构图
└── 论文初稿.md           # paper draft with embedded export tables / 含导出表的论文初稿
```

---

## Documentation / 文档索引

| Doc | English | 中文 |
|-----|---------|------|
| [docs/index.md](docs/index.md) | Documentation hub | 文档总入口 |
| [docs/progress.md](docs/progress.md) | M1–M13 progress (361 pytest) | 进度追踪 |
| [docs/server_commands.md](docs/server_commands.md) | Server deploy & runbook | 服务器命令手册 |
| [docs/mcp_protocol.md](docs/mcp_protocol.md) | M13 orchestration protocol | M13 编排协议 |
| [docs/experiment_log.md](docs/experiment_log.md) | Verified experiments | 实验记录 |
| [项目进度.md](项目进度.md) | — | 中文进度总览 |
| [项目v3设计.md](项目v3设计.md) | v3 design M9–M13 | v3 设计文档 |
| [论文初稿.md](论文初稿.md) | Paper draft | 论文初稿 |

---

## Roadmap / 路线图

**Done / 已完成** — Quant Engine · Walk-forward OOS · Agents · Memory/RAG · M6 text · M7 RL sim · M8 protocol · M9 Postgres/pgvector · M10 vLLM · M11–M11.8 population OOS · M12 RL export/OOS · **M13 orchestration + paper export** · FinBERT WF-001/002/003

量化引擎 · 样本外验证 · 智能体 · 记忆/RAG · 文本信号 · RL 仿真 · 协议层 · 企业 DB · vLLM · 种群 OOS · RL 导出/OOS · **M13 编排与论文导出** · FinBERT 三线消融

**Optional next / 可选后续** — EXP-TEXT-002 LoRA · paper-trading sandbox (simulation only)  
可选 EXP-TEXT-002 LoRA · 模拟盘沙盒（仅仿真）

---

## Contributing · License · Disclaimer / 贡献 · 许可 · 免责声明

Contributions welcome — see [CONTRIBUTING.md](CONTRIBUTING.md). [MIT License](LICENSE).  
欢迎贡献 — 见 [CONTRIBUTING.md](CONTRIBUTING.md)。[MIT 许可](LICENSE)。

**Research & education only.** Not financial advice. Backtest results may be wrong or overfit.  
**仅供科研与教育。** 不构成投资建议。回测结果可能错误、不完整或过拟合。

**Repo / 仓库**：https://github.com/ytq0198/Quant-MAS · **Email**： [3240101782@zju.edu.cn](mailto:3240101782@zju.edu.cn)
