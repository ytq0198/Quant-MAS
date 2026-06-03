# Quant MAS — 多智能体量化研究平台 / Multi-Agent Quantitative Research Platform

> 这是一个面向 **AI Agent / Quant / ML** 实习与科研申请者的开源项目：可运行、可回测、可训练、可记录。  
> A **resume-ready** research platform for AI Agent & Quant internships — backtesting, ML training, memory/RAG, and safe agent orchestration.

[![GitHub](https://img.shields.io/badge/GitHub-ytq0198%2FQuant--MAS-181717?logo=github)](https://github.com/ytq0198/Quant-MAS)
[![Release](https://img.shields.io/badge/release-v0.1.0-blue)](https://github.com/ytq0198/Quant-MAS/releases/tag/v0.1.0)
[![Python](https://img.shields.io/badge/python-3.11+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Tests](https://img.shields.io/badge/tests-225%20passed-brightgreen)](docs/progress.md)
[![Status](https://img.shields.io/badge/status-research%20platform-orange)](docs/progress.md)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![MAS Agent](https://img.shields.io/badge/MAS-Agent%20System-purple)](docs/architecture.md)

> **Not a live-trading bot.** LLM agents never place live orders directly.  
> **非实盘系统。** LLM Agent 不允许直接下单；所有信号须经回测、风控、审计和人工确认。

---

## 目录 / Table of Contents

- [项目简介 / Project Overview](#项目简介--project-overview)
- [架构 / Architecture](#架构--architecture)
- [项目亮点 / Features](#项目亮点--features)
- [快速开始 / Quick Start](#快速开始--quick-start)
- [运行示例 / CLI Examples](#运行示例--cli-examples)
- [Agent 工作流 / Agent Workflow](#agent-工作流--agent-workflow)
- [实验结果摘要 / Experiment Results](#实验结果摘要--experiment-results)
- [简历写法参考 / Resume Usage](#简历写法参考--resume-usage)
- [项目结构 / Project Structure](#项目结构--project-structure)
- [文档 / Documentation](#文档--documentation)
- [Roadmap](#roadmap)
- [贡献指南 / Contributing](#贡献指南--contributing)
- [License](#license)
- [免责声明 / Disclaimer](#免责声明--disclaimer)
- [社交 & 联系方式 / Contact & Social](#社交--联系方式--contact--social)

---

## 项目简介 / Project Overview

**Quant MAS** integrates a **deterministic Quant Engine** (data → features → models → strategies → backtest → risk → reports) with a **lightweight Agent Layer** (tool routing, research narration, optional LLM) and **Memory/RAG** for experiment retrieval.

**Quant MAS** 将确定性量化引擎与轻量 Agent 层、Memory/RAG 结合：Quant Engine 负责计算与 metrics，Agent 负责编排、解释与报告，二者边界清晰。

**Design principle / 设计原则**

> Quant Engine computes. Agent Layer explains, orchestrates, and reports.  
> Quant Engine 做计算；Agent Layer 做编排、解释与报告。

**Plus v2**：M1–M8 ✅ · **v3 M9–M11** ✅ 双端（225 pytest · EXP-POP-002）

**v3 next / 下一步**：M12 RL 训练 · M13 编排 · EXP-TEXT-WF-002

---

## 架构 / Architecture

![Quant MAS architecture — Quant Engine, Agent Layer, Memory/RAG, and research workflow](architecture.png)

<details>
<summary>Mermaid diagram / 点击展开流程图</summary>

```mermaid
flowchart LR
    A["Data Sources"] --> B["Quant Engine"]
    B --> C["Features / Labels"]
    C --> D["Models / Strategies"]
    D --> E["Backtest / Risk"]
    E --> F["Reports / ExperimentMemory"]
    F --> G["Memory + RAG"]
    G --> H["Agent Layer"]
    H --> I["Research / Explanation"]
```

</details>

Details: [docs/architecture.md](docs/architecture.md) · [docs/index.md](docs/index.md)

---

## 项目亮点 / Features

| Layer | English | 中文 |
|-------|---------|------|
| **Quant Engine** | Parquet storage, OHLCV validation, features, MA Cross / ML strategies, backtest, risk, metrics | 数据、特征、策略、回测、风控、绩效 |
| **ML** | LightGBM direction model, MLSignalStrategy, **walk-forward OOS** evaluation | 方向模型、ML 信号策略、样本外 walk-forward |
| **MAS Agent** | `ToolRegistry`, **SupervisorAgent** (rule routing), **ReportAgent**, **ResearchAgent** | 工具注册、监督路由、报告与研究智能体 |
| **Memory / RAG** | JSON & SQLite experiment memory, hybrid retrieval, index/query CLI | 实验记忆、混合检索、文档索引 |
| **Enterprise DB (v3 M9)** | Postgres memory, **pgvector**, Neo4j graph skeleton; `json \| sqlite \| postgres` factory | 企业级持久化；服务器 **EXP-026** ✅（443 pgvector chunks） |
| **LangGraph** | Optional 6-node ResearchWorkflow DAG + sequential fallback | 可选工作流编排（`[orchestration]` extra） |
| **Context / LLM (v3 M10)** | ContextBuilder, `mock \| openai_compatible \| **local_vllm**`; server **Qwen2.5-7B** via vLLM (EXP-LLM-002) | 上下文工程；pytest 默认 Mock；a6000 本地推理见 `docs/server_commands.md` §6.13 |
| **RL Simulation (M7)** | TradingEnv, buy-and-hold / random / ML-copy baselines; GRPO-style ranking | RL 模拟骨架；`simulation.*` 不与 OOS 混比 |
| **Competitive Learning (v3 M11)** | StrategyAgent pool, PopulationManager, Elo, `run_competitive_experiment.py` | 多 agent shadow simulation；`population.*` ≠ OOS |
| **Protocol (M8)** | MCP/A2A internal adapter, AgentCard export, policy deny shell/broker/secrets | 协议层 adapter；不接外部 MCP server |
| **Text Signals (M6)** | Mock / FinBERT / LoRA **skeleton**, merge into feature tables | 文本情绪特征骨架，不替代 LightGBM |
| **Research Protocol (M1)** | Baseline registry, `compare_experiments.py`, OOS metric discipline | 实验基线对比；论文主指标用 OOS |

---

## 快速开始 / Quick Start

```bash
git clone https://github.com/ytq0198/Quant-MAS.git
cd Quant-MAS

python -m pip install -e .
python -m pytest -v
python -c "import quant_mas; print('Quant MAS ready')"
```

**Optional extras / 可选依赖**

```bash
python -m pip install -r requirements-data.txt    # market data fetchers
python -m pip install -r requirements-ml.txt      # LightGBM
python -m pip install -e ".[orchestration]"       # LangGraph workflow
python -m pip install -e ".[llm]"                 # HTTP LLM client
python -m pip install -e ".[text]"                # FinBERT / LoRA (server manual)
```

**Verified baseline / 已验证基线**：**225 passed**（本地+服务器，EXP-029 / EXP-POP-002）

---

## 运行示例 / CLI Examples

### End-to-end pipeline / 端到端 pipeline

```bash
python scripts/run_pipeline.py \
  --symbols AAPL MSFT SPY \
  --start 2018-01-01 \
  --end 2025-12-31 \
  --skip-download \
  --strategy ma_cross \
  --experiment-name local_ma_cross_demo
```

### Train LightGBM / 训练方向模型

```bash
python scripts/train_model.py \
  --config configs/train.yaml \
  --storage-config configs/storage.yaml \
  --experiment-name local_lgbm_demo
```

### ML signal backtest / ML 信号回测

```bash
python scripts/run_ml_backtest.py \
  --config configs/backtest_ml.yaml \
  --storage-config configs/storage.yaml \
  --experiment-name local_ml_backtest_demo
```

### Walk-forward OOS / 样本外 walk-forward

```bash
python scripts/run_walk_forward.py \
  --config configs/walk_forward.yaml \
  --storage-config configs/storage.yaml \
  --experiment-name local_walk_forward_demo
```

### SupervisorAgent (rule routing) / 规则路由

```bash
python scripts/run_agent.py \
  --task "summarize this dataset" \
  --data-path data/features/features.parquet
```

### ResearchAgent (mock-safe / local vLLM) / 研究解释

```bash
# Default: Mock LLM (CI-safe)
python scripts/run_research_agent.py \
  --task "Summarize OOS baseline EXP-20260602-008 (oos.sharpe ≈ 0.586)"

# Server: requires vLLM on :8000 (see docs/server_commands.md §6.13)
export VLLM_BASE_URL=http://127.0.0.1:8000
export VLLM_MODEL=Qwen/Qwen2.5-7B-Instruct
python scripts/run_research_agent.py \
  --provider local_vllm --use-llm \
  --task "Interpret walk-forward OOS baseline only; list three research risks."
```

### Mock text signals / 文本信号（mock）

```bash
python scripts/train_text_model.py \
  --mode mock \
  --config configs/text_model.yaml \
  --dry-run
```

### Compare experiments / 实验对比

```bash
python scripts/compare_experiments.py \
  --storage-config configs/storage.yaml \
  --output-dir outputs/research
```

---

## Agent 工作流 / Agent Workflow

Quant MAS uses **real, implemented** agents — not a separate broker layer.

当前已实现的两条 Agent 路径：

**1. SupervisorAgent + Quant Tools（规则路由）**

```
User task → SupervisorAgent → ToolRegistry → one of 7 tools
  (data_summary | backtest | train_model | report | risk_check | ml_backtest | pipeline)
```

**2. ResearchWorkflow DAG（Plus M4，optional LangGraph）**

```
download → features → train → ml_backtest → risk → report
  (sequential fallback always available; LangGraph optional)
```

**3. ResearchAgent（Plus M5，解释层）**

```
Memory/RAG + metrics → ContextBuilder → ResearchAgent → hypotheses & narrative
  (does NOT modify metrics or place orders)
```

Python snippet / 代码示例：

```python
from quant_mas.agents import SupervisorAgent
from quant_mas.tools import ToolRegistry, DataSummaryTool

registry = ToolRegistry([DataSummaryTool()])
agent = SupervisorAgent(registry)

result = agent.run(
    "summarize this dataset",
    data_path="data/features/features.parquet",
)
print(result.content)
```

---

## 实验结果摘要 / Experiment Results

| Item | Value | Notes |
|------|-------|-------|
| **pytest** | **225 passed** | EXP-029 本地 · EXP-POP-002 服务器（17.32s） |
| **competitive learning** | Population + Elo mock | EXP-POP-001/002 dry-run ✅ |
| **local vLLM smoke** | ResearchAgent `local_vllm` | EXP-LLM-002（Qwen2.5-7B @ a6000） |
| **Postgres/pgvector smoke** | `query_memory` + `index_documents` | EXP-026（6 experiments, **443 chunks**） |
| **OOS baseline** | **sharpe 0.586** | EXP-20260602-008, 19 walk-forward windows |
| **OOS + FinBERT text** | **sharpe 0.563** | EXP-TEXT-WF-001 · exploratory (200/6033 text coverage) |
| Single-segment ML backtest | sharpe 2.78 | ⚠️ in-sample — **not** paper metric |
| GPU LightGBM | verified on server | CUDA path documented in `docs/server_commands.md` |

**Research rule / 科研规则**：paper-level conclusions must use **walk-forward OOS** metrics and compare via `compare_experiments.py`. See [docs/research_protocol.md](docs/research_protocol.md).

---

## 简历写法参考 / Resume Usage

**English**

> Built **Quant MAS**, a Python 3.11 multi-agent quantitative research platform with deterministic quant pipelines, walk-forward OOS evaluation (baseline sharpe 0.586), Memory/RAG, optional LangGraph, enterprise DB backends (Postgres/pgvector), **local vLLM ResearchAgent** (EXP-LLM-002), **competitive strategy population** (M11 Elo simulation), text signals, RL simulation, MCP-style protocol adapter, and mock-safe LLM defaults. Maintained **225 passing pytest** cases with strict safeguards preventing LLM agents from direct live trading.

**中文**

> 基于 Python 3.11 构建 **Quant MAS** 多智能体量化研究平台，完成 Walk-forward OOS、风控、Agent 编排、Memory/RAG、**v3 企业 DB**、**本地 vLLM（M10）**、**竞争学习策略种群（M11）**、文本信号、RL 模拟与 **MCP/A2A 协议层（M8）**；维护 **225 项 pytest** 通过，明确 LLM Agent 不直接参与实盘下单。

---

## 项目结构 / Project Structure

```text
Quant-MAS/
├── src/quant_mas/          # core package
│   ├── data/               # storage, fetchers, validation
│   ├── features/           # technical, labels, text_signals
│   ├── models/               # LightGBM direction model
│   ├── strategies/           # ma_cross, ml_signal
│   ├── backtest/             # engine, walk_forward, metrics
│   ├── risk/                 # limits, drawdown guard
│   ├── agents/               # supervisor, report, research, strategy (M11)
│   ├── tools/                # 7 quant tools
│   ├── memory/               # experiment memory: json | sqlite | postgres (M9)
│   ├── rag/                  # retriever, in-memory + pgvector (M9)
│   ├── context/              # ContextBuilder (M5)
│   ├── core/                 # llm.py — mock | openai_compatible | local_vllm (M10)
│   ├── text/                 # text signals (M6)
│   ├── rl/                   # TradingEnv (M7), competitive runner (M11)
│   ├── protocols/            # MCP/A2A adapter (M8)
│   ├── orchestration/        # LangGraph workflow (M4)
│   └── research/             # baseline registry (M1)
├── scripts/                  # CLI entrypoints
├── configs/                  # YAML configs (+ llm.server.yaml.example)
├── tests/                    # 225 pytest cases
├── docs/                     # architecture, progress, experiment log, server_commands
├── architecture.png          # architecture diagram
├── CONTRIBUTING.md
├── LICENSE
└── README.md
```

---

## 文档 / Documentation

| Doc | Description |
|-----|-------------|
| [docs/index.md](docs/index.md) | Documentation hub (bilingual) |
| [docs/progress.md](docs/progress.md) | Plus v2 M1–M8 + v3 M9/M10 progress |
| [项目进度.md](项目进度.md) | 中文进度总览（Plus v2 收官 + v3） |
| [项目v3设计.md](项目v3设计.md) | v3 roadmap M9–M13 |
| [docs/experiment_log.md](docs/experiment_log.md) | Verified experiments (EXP-LLM-002, OOS 0.586, …) |
| [docs/research_protocol.md](docs/research_protocol.md) | OOS metric rules |
| [docs/server_commands.md](docs/server_commands.md) | Server deploy, vLLM §6.13, Postgres §6.12 |
| [docs/database_setup.md](docs/database_setup.md) | M9 Postgres / pgvector / Neo4j |
| [docs/competitive_learning.md](docs/competitive_learning.md) | M11 population / Elo |
| [docs/context_engineering.md](docs/context_engineering.md) | LLM providers & ResearchAgent |
| [CONTRIBUTING.md](CONTRIBUTING.md) | How to contribute |

---

## Roadmap

- [x] Quant Engine MVP — data, features, backtest, risk, reports
- [x] LightGBM training & ML signal backtest
- [x] Walk-forward OOS evaluation
- [x] SupervisorAgent + 7 Quant Tools
- [x] Memory / RAG v2 (JSON, SQLite, hybrid retrieval)
- [x] LangGraph ResearchWorkflow (optional)
- [x] Context engineering + optional LLM (M5)
- [x] Text signal layer — mock / FinBERT / LoRA skeleton (M6)
- [x] **M7** RL simulation / GRPO-style ranking skeleton ✅
- [x] **M8** MCP / A2A protocol adapter ✅
- [x] **M9** Enterprise DB — Postgres memory, pgvector, Neo4j skeleton; **EXP-026** server smoke ✅
- [x] **M10** LLM production — `local_vllm`, ResearchAgent smoke **EXP-LLM-002** (Qwen2.5-7B @ a6000) ✅
- [x] **M11** Competitive learning — StrategyAgent, PopulationManager, Elo **EXP-029** ✅
- [ ] **M12** RL training experiments (GRPO/PPO/MARL GPU smoke)
- [ ] **M13** Enterprise orchestration — multi-experiment DAG scheduler, audit log
- [ ] FinBERT server smoke + text-enhanced walk-forward ablation (EXP-TEXT-WF-002)
- [ ] Optional paper-trading sandbox (simulation only)

See [项目v3设计.md](项目v3设计.md) for full v3 scope.

---

## 贡献指南 / Contributing

1. **Fork** and clone the repository  
2. `python -m pip install -e .` and run `python -m pytest -v`  
3. Add Tool / Agent / Fetcher / Strategy with tests (mock/synthetic only)  
4. Open an **Issue** or **Pull Request**

**Do not commit** real API keys, datasets, or model weights. See [CONTRIBUTING.md](CONTRIBUTING.md).

---

## License

[MIT License](LICENSE)

---

## 免责声明 / Disclaimer

This project is for **research and education only**. It is not financial advice and must not be used for live trading without independent validation, risk review, and human approval.

本项目仅用于科研和教育，不构成投资建议或收益承诺。回测与模型结果可能错误、不完整或过拟合。

---

## 社交 & 联系方式 / Contact & Social

**Repository**: https://github.com/ytq0198/Quant-MAS

欢迎 **Star / Fork / Issue / PR** — feedback from students and researchers is welcome!

**Email**: [3240101782@zju.edu.cn](mailto:3240101782@zju.edu.cn)

If this project helps your portfolio or coursework, a ⭐ on GitHub is appreciated.
