# Quant MAS 仓库整理清单（Repo Polish Checklist）

更新时间：2026-06-03  
仓库：<https://github.com/ytq0198/Quant-MAS>  
联系：3240101782@zju.edu.cn

本文档汇总 README 第一屏审计、docs 整理、GitHub 仓库项与社交传播文案。**不虚构未完成模块**；未验证项标为「待确认 / 待补充」。

---

## 1. README 第一屏可读性审计

| 检查项 | 状态 | 说明 |
|--------|------|------|
| 双语标题与一句话定位 | ✅ 已完成 | 英 + 中首段 |
| 徽章（Python / Tests / Status / License / GitHub） | ✅ 已完成 | Tests=237 passed（本地+服务器，EXP-030/POP-003） |
| 安全声明（非实盘、LLM 不下单） | ✅ 已完成 | blockquote 双语 |
| Quick Start | ✅ 已完成 | clone → pip → pytest |
| CLI Examples | ✅ 已完成 | pipeline / train / ml backtest / ResearchAgent / text mock |
| Features 表 | ✅ 已完成 | 双语列 |
| Architecture | ⚠️ 部分 | 已引用 `assets/architecture.png` + mermaid 回退；**PNG 文件待提交** |
| Resume Usage | ✅ 已完成 | 英 + 中各一段 |
| Roadmap | ✅ 已完成 | 已完成项到 M6；后续为模拟层 / 报告 / 部署 |
| Documentation 链接 | ✅ 已完成 | index / architecture / progress / experiment_log 等 |
| Contributing + 社交引导 | ✅ 已完成 | Star/Fork/Issue/PR + 邮箱 |
| License | ✅ 已完成 | `LICENSE`（MIT） |
| Disclaimer | ✅ 已完成 | 双语 |

**第一屏建议（低优先级）**

- [ ] 提交 `assets/architecture.png`（见 [assets/README.md](../assets/README.md)）
- [ ] 增加 `docs/badge` 或 GitHub Actions CI badge（若后续加 workflow）
- [ ] Roadmap 增加 Plus **M7 / M8** 一行（与 progress.md 对齐）

---

## 2. docs 整理状态

| 文件 | 状态 | 本次更新 |
|------|------|----------|
| [progress.md](progress.md) | ✅ | Plus v2 **M1–M8** 总表（含 M3.5 / M5.5） |
| [experiment_log.md](experiment_log.md) | ✅ | 扩展实验模板（WF / LLM / TEXT / COMP） |
| [architecture.md](architecture.md) | ✅ | 引用 `assets/architecture.png` |
| [repo_polish_checklist.md](repo_polish_checklist.md) | ✅ | 本文档 |
| [index.md](index.md) | ✅ 已有 | 文档入口、双语、161 passed |
| [text_model_plan.md](text_model_plan.md) | ✅ 已有 | M6 计划 |
| [research_protocol.md](research_protocol.md) | ✅ 已有 | OOS 主指标规范 |

---

## 3. GitHub 仓库检查

> 本地未安装 `gh` CLI，Topics / Release 需在 GitHub Web UI **待确认**。

### 3.1 Repository Topics（建议设置）

在 **Settings → General → Topics** 添加（与项目真实范围一致）：

```
quantitative-finance
algorithmic-trading
multi-agent-systems
llm-agents
agentic-ai
rag
machine-learning
lightgbm
backtesting
walk-forward
financial-ai
fintech
python
risk-management
experiment-tracking
ai-agent
langgraph
reinforcement-learning
financial-machine-learning
resume-project
```

**说明**：`reinforcement-learning` Topic 可用；M7 **TradingEnv 骨架已实现**（simulation only），M8 仍为 roadmap。

### 3.2 Release v0.1.0（建议）

| 项 | 建议 |
|----|------|
| Tag | `v0.1.0` |
| Title | `v0.1.0 — Research MVP (M1–M6, 161 tests)` |
| 说明 | v1 Prompt 1–20 + Plus M1–M6；161 pytest；OOS baseline 0.586（服务器 walk-forward）；**非**实盘系统 |
| Assets | 不含 data / models / `.env` |
| 触发时机 | `LICENSE` + `assets/architecture.png` 提交后 |

Release notes 草稿见本文档 §6。

### 3.3 社区文件

| 文件 | 状态 |
|------|------|
| [CONTRIBUTING.md](../CONTRIBUTING.md) | ✅ 双语、测试规则、安全要求 |
| [LICENSE](../LICENSE) | ✅ MIT（2026-06-03 新增） |
| `.github/ISSUE_TEMPLATE/bug_report.md` | ✅ |
| `.github/ISSUE_TEMPLATE/feature_request.md` | ✅ |
| `.github/ISSUE_TEMPLATE/experiment_report.md` | ✅ |
| `.github/ISSUE_TEMPLATE/good_first_issue.md` | ✅ |
| `PULL_REQUEST_TEMPLATE.md` | ❌ 待补充（低优先级） |
| GitHub Actions CI | ❌ 待补充（低优先级） |

### 3.4 README 社交 / 邮箱

| 项 | 状态 |
|----|------|
| 邮箱 `3240101782@zju.edu.cn` | ✅ README Contributing + CONTRIBUTING.md |
| GitHub 链接 | ✅ 徽章 + clone URL |
| Star / Fork / Issue / PR 引导 | ✅ Contributing 节 |

---

## 4. 已完成 / 待补充 / 优先级

### 4.1 已完成（可对外展示）

- v1 量化核心：数据 → 特征 → 策略 → 回测 → 风控 → 报告
- LightGBM 方向模型 + MLSignalStrategy + walk-forward OOS（baseline **0.586**）
- Agent：SupervisorAgent（规则路由）、ReportAgent、ResearchAgent（Mock-safe）
- Memory/RAG v2：JSON/SQLite、HybridRetriever、index/query CLI
- LangGraph 编排（optional）+ sequential fallback
- M5 ContextBuilder + 可选 OpenAI-compatible LLM（DeepSeek smoke 已记录）
- M6 文本信号骨架（mock pytest **11/11**；FinBERT 骨架；**161 passed** 本地+服务器）
- 文档：architecture、progress、experiment_log、CONTRIBUTING、issue templates

### 4.2 待补充（高优先级）

| # | 项 | 行动 |
|---|-----|------|
| H1 | `assets/architecture.png` | 从 mermaid/设计图导出 PNG 并提交 |
| H2 | GitHub Topics | Web UI 批量添加 §3.1 列表 |
| H3 | Release **v0.1.0** | 打 tag + Release notes（§6） |
| H4 | `.env.example` HF 占位 | 增加 `HF_TOKEN` / `HF_HOME` 注释（不含真实 key） |
| H5 | `train_text_model.py` 加载 `.env` | 可选：`load_repo_dotenv()` 与 M5 一致 |

### 4.3 待补充（低优先级）

| # | 项 |
|---|-----|
| L1 | `PULL_REQUEST_TEMPLATE.md` |
| L2 | GitHub Actions：`python -m pytest -v` on push |
| L3 | `docs/screenshots/` CLI 输出截图 |
| L4 | 英文版 `README.zh-CN.md` 拆分（当前 README 已 inline 双语） |
| L5 | EXP-TEXT-001 / EXP-TEXT-WF-001 写入 experiment_log | ✅ |
| L6 | M7 的 `codex_prompt_M7.md` + `rl_plan.md` | ✅ |
| L7 | M8 的 `codex_prompt_M8.md` + `protocols.md` | ✅ |

### 4.4 明确未实现（文案中不得写成已完成）

- M7 RL/GRPO 训练与 TradingEnv
- M8 MCP/A2A 协议适配器
- M3.5 企业 RAG（Postgres/pgvector 生产后端）
- M5.5 本地 vLLM 服务 ✅ EXP-LLM-002（见 server_commands §6.13）
- 真实 FinBERT/LoRA 生产训练流水线（仅骨架 + 服务器手工 smoke）
- 实盘下单 / broker 对接

---

## 5. 模块真实状态速查（对外口径）

| 能力 | 对外说法 |
|------|----------|
| 回测 / 风控 | ✅ 已实现，pytest 覆盖 |
| Walk-forward OOS | ✅ 已实现；服务器 verified sharpe **0.586** |
| LLM Agent | ✅ ResearchAgent/ReportAgent；默认 Mock；可选云端 API |
| 文本情绪特征 | ✅ mock + FinBERT 服务器 smoke（EXP-TEXT-001）；WF OOS **0.563** vs **0.586**（exploratory） |
| LangGraph | ✅ 可选依赖 `[orchestration]` |
| RL simulation | ✅ M7 TradingEnv + GRPO ranking（本地 180 pytest） |
| RL / MCP | M7 ✅ 本地 skeleton · M8 📋 未实现 |

---

## 6. Release v0.1.0 Notes 草稿

```markdown
## v0.1.0 — Research MVP

**Quant MAS** is a research-first multi-agent quantitative platform (Python 3.11+).

### Highlights
- Deterministic quant pipeline: data, features, strategies, backtest, risk, reports
- LightGBM direction model + walk-forward OOS evaluation
- 161 passing pytest cases (mock/synthetic only in CI)
- Agent layer: SupervisorAgent, ResearchAgent, optional LLM narration
- Memory/RAG v2, optional LangGraph workflow
- Text signal layer (M6) — FinBERT smoke + walk-forward OOS comparison on server

### Verified research baseline
- Walk-forward OOS sharpe **0.586** (EXP-20260602-008, server walk-forward)
- Text-augmented walk-forward OOS sharpe **0.563** (EXP-TEXT-WF-001, exploratory)

### Not included
- No live trading / broker integration
- No RL/MCP production modules yet (roadmap M7/M8)

### Install
pip install -e .
python -m pytest -v
```

---

## 7. 社交文案示例

**统一链接**：<https://github.com/ytq0198/Quant-MAS>  
**统一 CTA**：欢迎 Star / Fork / Issue / PR  
**统一定位**：科研 + 学习 + **实习 / 作品集**（AI Agent × Quant × ML × RAG）

---

### 7.1 知乎

**标题**：开源了一个多智能体量化研究平台 Quant MAS，适合写进 AI/Quant 实习简历

**正文**：

最近在 GitHub 开源了 **Quant MAS**（Multi-Agent System for Quantitative Research）：  
https://github.com/ytq0198/Quant-MAS

它不是「让 LLM 直接炒股」的噱头项目，而是把 **确定性 Quant Engine**（数据、特征、LightGBM、回测、风控、walk-forward 样本外评估）和 **Agent 层**（工具编排、Memory/RAG、ResearchAgent 解释）分开设计——LLM 只做研究和报告，**不允许直接下单**。

目前已实现并测通 **161 项 pytest**（本地+服务器），包含：
- 端到端量化 pipeline
- Walk-forward OOS 主 baseline（论文级指标 discipline）
- SupervisorAgent 规则路由 + 7 个 Quant Tools
- Memory/RAG v2、可选 LangGraph 工作流
- 文本情绪信号模块骨架（FinBERT/LoRA mock-safe）

如果你在做 **AI Agent / 量化 / 机器学习** 方向实习，需要一条能讲清楚的工程+科研闭环，可以参考 README 里的 **Resume Usage** 段落。

欢迎 **Star / Fork**，有问题开 **Issue**，改进欢迎 **PR**。  
（科研教育用途，不构成投资建议。）

---

### 7.2 掘金

**标题**：Quant MAS 开源：LightGBM + Walk-forward + Agent/RAG 的量化科研平台（161 tests）

**正文**：

项目地址：https://github.com/ytq0198/Quant-MAS

**Why**：很多 Agent 项目缺 deterministic backtest；很多 Quant 项目缺可解释的 Agent/RAG 层。Quant MAS 把两者合并，并强调 **OOS walk-forward** 才是论文主指标。

**Stack**：Python 3.11 · LightGBM · pytest · ToolRegistry · ExperimentMemory · HybridRetriever · 可选 LangGraph · 文本信号 skeleton

**Quick Start**：
```bash
git clone https://github.com/ytq0198/Quant-MAS.git
cd Quant-MAS
python -m pip install -e .
python -m pytest -v
```

适合：**Quant 入门**、**时间序列 ML**、**Agent 工具编排**、**实习作品集**。

Star / Fork / Issue / PR 都欢迎。MIT License。

---

### 7.3 CSDN

**标题**：【开源】Quant MAS：多智能体量化研究与回测平台（含 Walk-forward OOS + RAG + 161 单元测试）

**正文**：

GitHub：https://github.com/ytq0198/Quant-MAS

Quant MAS 面向 **课程项目 / SRTP / 科研训练 / 实习申请**，提供从行情数据、特征工程、策略回测、风控到实验记录、RAG 检索、ResearchAgent 解释的完整链路。

**亮点**：
1. 量化核心与 Agent 分层，LLM 不直接交易  
2. Walk-forward 样本外评估 + 实验基线对比（compare_experiments）  
3. 161 passed pytest，CI 友好（mock/synthetic）  
4. README 提供中英文 **Resume Usage** 段落  

**未实现**：RL(M7)、MCP(M8) 仍在 roadmap，不夸大宣传。

欢迎 Star、Fork、提 Issue、贡献 PR。联系：3240101782@zju.edu.cn

---

### 7.4 V2EX

**标题**：[分享] 开源 Quant MAS：Agent + Quant 科研平台，161 tests，适合 portfolio

**正文**：

https://github.com/ytq0198/Quant-MAS

Python 写的多智能体量化**研究**平台（不是实盘 bot）。  
Quant Engine 做计算，Agent 做编排/解释，Memory+RAG 查实验，walk-forward 做 OOS。

个人用来整理 SRTP/实习材料，README 有 resume 描述可直接改。  
M1–M7 代码已落地（M7 simulation only），M8 MCP 还在规划。

求 Star，欢迎 Issue/PR。仅科研教育，非投资建议。

---

### 7.5 少数派

**标题**：把量化研究、Agent 和实验记录做成一个可复现的开源项目：Quant MAS

**正文**：

对于想系统学习「数据 → 模型 → 回测 → 报告」的同学，纯 notebook 往往缺少工程边界；对于做 Agent 的同学，又容易忽略风控与样本外验证。

**Quant MAS** 尝试用一层清晰的架构把这些问题分开：  
https://github.com/ytq0198/Quant-MAS

- 确定性引擎负责 metrics  
- Agent 负责解释与工具调用  
- 实验 memory + RAG 负责可追溯  
- Walk-forward 负责 OOS 结论  

文档齐全（architecture / progress / experiment_log），**161** 项测试，适合作为长期迭代的个人研究仓库。

欢迎 Star / Fork / Issue / PR。

---

### 7.6 LinkedIn（English）

**Post**：

I open-sourced **Quant MAS** — a research-first multi-agent quantitative platform in Python.

🔗 https://github.com/ytq0198/Quant-MAS

It combines a deterministic quant engine (features, LightGBM, backtesting, risk, walk-forward OOS) with a lightweight agent layer (tool routing, memory/RAG, research narration). LLM agents **never** place live orders.

✅ 161 passing pytest cases  
✅ Experiment tracking + baseline comparison  
✅ Good fit for AI Agent / Quant / ML internship portfolios  

Star / Fork / Issues / PRs welcome. Research & education only — not financial advice.

#QuantitativeFinance #MachineLearning #AIAgents #LangGraph #Python #OpenSource #FinTech

---

### 7.7 Twitter / X（English）

**Thread opener**：

Open-sourced Quant MAS 🧪📈

Research-first multi-agent quant platform:
• LightGBM + walk-forward OOS
• Tool-routing agents + Memory/RAG
• 161 pytest (mock-safe)
• LLM explains — does NOT trade

Great for AI Agent / Quant intern portfolios.

⭐ https://github.com/ytq0198/Quant-MAS

Star / Fork / Issue / PR welcome.

---

### 7.8 Reddit（r/algotrading or r/MachineLearning）

**Title**：`[Project] Quant MAS – research multi-agent quant platform with walk-forward OOS + RAG (161 tests, MIT)`

**Body**：

Repo: https://github.com/ytq0198/Quant-MAS

I'm sharing a project I've been building for research/education (not live trading). It separates:

1. **Quant engine** – deterministic pipeline, LightGBM direction model, backtest, risk, walk-forward OOS evaluation  
2. **Agent layer** – SupervisorAgent tool routing, ResearchAgent with structured context (no direct order placement)  
3. **Memory/RAG** – experiment retrieval over reports/docs  

Current status: **161 passing tests**; server walk-forward OOS baseline documented at sharpe ~0.586. Text-signal and optional LangGraph layers are in repo; RL/MCP are roadmap only.

If you're building a portfolio for quant/ML/agent internships, README includes resume bullets.

Feedback welcome via Issues/PRs. MIT license. Not financial advice.

---

## 8. 维护者下一步（建议顺序）

1. 导出并提交 `assets/architecture.png`  
2. GitHub Topics + Release **v0.1.0**  
3. `.env.example` 补 HF 占位；可选 `load_repo_dotenv` in `train_text_model.py`  
4. 服务器 EXP-TEXT-001 完成后写入 [experiment_log.md](experiment_log.md)  
5. 择一平台发布 §7 文案，链接回 GitHub  

---

*本清单随仓库演进更新；以 [progress.md](progress.md) 与 [experiment_log.md](experiment_log.md) 为实验真相来源。*
