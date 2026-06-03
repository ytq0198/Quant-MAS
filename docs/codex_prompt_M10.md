# Plus v3 M10：LLM 生产化与文本增强 — Codex 提示词

**状态：✅ 已完成（本地 EXP-20260602-027，212 passed，2026-06-01）**

更新时间：2026-06-01

> **用法**：先粘贴下方「固定前缀」，再粘贴「M10 主任务」整段交给 Codex。  
> **设计依据**：[项目v3设计.md §M10](../项目v3设计.md#m10llm-生产化与文本增强) · 配套：[context_engineering.md](context_engineering.md) · 前置：**M1–M8 ✅**、**M9 本地 ✅**

---

## 固定前缀（每次必贴）

```
你正在开发 Quant MAS 科研项目（v3 阶段）。
路径：D:\scientific reasearch and work\SRTP\Quant MAS

测试基线：本地 **207 passed**（v3 M9，EXP-20260602-025）。
OOS 主 baseline：EXP-20260602-008，oos.sharpe **0.586**（walk-forward，19 窗）。
M6 text OOS exploratory：EXP-TEXT-WF-001，oos.sharpe **0.563** vs baseline **0.586**（不可替代主指标）。
M7 RL：simulation only；`simulation.*` 不得与 `oos.*` 混比。

硬性原则：
1. LLM **不直接下单**；ResearchAgent / ReportAgent 只做研究叙事、解释、报告，**不得**改写 Quant Engine metrics。
2. pytest **默认 Mock**，不联网、不调真实 DeepSeek/vLLM；HTTP 测试用 mock（urllib / httpx stub）。
3. 无 `LLM_API_KEY` / 无 `VLLM_BASE_URL` 时必须安全回退 `MockLLMClient`（与 M-017 行为一致）。
4. **不替换** SupervisorAgent 规则路由；M10 扩展 `resolve_llm_client` 与配置，不改变 7 Quant Tools 行为。
5. 请只实现当前 **M10** 一个模块；改完后 `python -m pytest -v` 全量通过（预期 207+，增量测试在 test_context_engineering.py 或新 test_llm_vllm.py）。
6. 禁止 commit `.env`、API key、或含 secrets 的 server yaml 样例。
7. EXP-TEXT-WF-002（扩大 text JSONL + walk-forward）为 **Cursor 服务器科研任务**，Codex 只提供 CLI/文档边界与 mock 路径，**不虚构** OOS 数字。
8. 论文主指标仍为 walk-forward OOS；LLM 输出不参与 sharpe 计算。
```

---

## M10 主任务（复制给 Codex）

```
请为 Quant MAS v3 实现 **M10：LLM 生产化**（local_vllm + 配置增强 + mock 测试）。文本 LoRA 仅文档化边界，不在本任务跑真实训练。

## 背景

v2 / v3 已有：
- core/llm.py — MockLLMClient、OpenAICompatibleLLMClient、resolve_llm_client(provider=mock|openai_compatible)
- configs/llm.yaml — provider: mock
- configs/context.yaml、context_builder.py、compression.py
- agents/research_agent.py — ResearchAgent，use_llm=False 默认
- agents/report_agent.py — ReportAgent / ReportResult
- scripts/run_research_agent.py、generate_report.py --use-llm
- tests/test_context_engineering.py — 12 passed（含 resolve_llm_client、ResearchAgent mock）
- EXP-LLM-001 — DeepSeek 云端 smoke（服务器手工，非 pytest）

M10 目标：
1. **local_vllm provider** — 与 OpenAI-compatible chat/completions 相同 HTTP 形态，读 `VLLM_BASE_URL` / `VLLM_MODEL`（api_key 可为空或 dummy）。
2. **resolve_llm_client** — 支持 provider：`mock` | `openai_compatible` | `local_vllm`；`use_llm=False` 仍强制 Mock。
3. **配置样例** — configs/llm.server.yaml.example（vLLM endpoint，无真实 key）。
4. **ResearchAgent / ReportAgent** — 明确 provider 选择路径；LLM 失败时回退 Mock 并 warn（不 crash pytest）。
5. **文档** — 增量更新 docs/context_engineering.md（vLLM env、DeepSeek、local_vllm 对照表）。
6. **测试** — mock HTTP 验证 local_vllm 请求 URL/headers/body 形状；无 env 时仍 Mock。

第一版**不做**：真实 vLLM 集成测试、FinBERT/LoRA 权重下载、EXP-TEXT-WF-002 跑数。

## 需要实现的文件

### 1. core/llm.py 扩展

```python
# resolve_llm_client 新增 local_vllm 分支：
# - LLM_PROVIDER=local_vllm 或 provider="local_vllm"
# - VLLM_BASE_URL（必填，如 http://127.0.0.1:8000）
# - VLLM_MODEL（默认 quant-mas-local 或 env）
# - VLLM_API_KEY 可选（多数 vLLM 部署可空，传 "EMPTY" 或省略 Authorization）
# - 复用 OpenAICompatibleLLMClient 或薄 wrapper LocalVLLMClient(OpenAICompatibleLLMClient)
# - base_url 指向 VLLM_BASE_URL，chat 路径仍为 /v1/chat/completions

# 保持现有 openai_compatible + mock 行为不变
# 无 key 的 openai_compatible 仍 warn + Mock（M-017）
# local_vllm 无 VLLM_BASE_URL 时 warn + Mock
```

可选：提取 `_build_openai_compatible_client(base_url, api_key, model, timeout)` 减少重复。

### 2. configs/llm.server.yaml.example

```yaml
# Copy to llm.server.yaml locally on server — do not commit secrets.
provider: local_vllm          # mock | openai_compatible | local_vllm
model: Qwen2.5-7B-Instruct    # 示例，按服务器实际模型
base_url: http://127.0.0.1:8000
timeout_seconds: 120
# vLLM 通常无需 key；DeepSeek 云端改用 openai_compatible + LLM_API_KEY
```

### 3. .env.example 增量（若尚未有 vLLM 变量）

```env
# M10 local vLLM（OpenAI-compatible endpoint on a6000）
VLLM_BASE_URL=
VLLM_MODEL=
VLLM_API_KEY=
```

### 4. scripts/run_research_agent.py（小改）

- 增加 `--provider mock|openai_compatible|local_vllm`（可选，默认读 env/config）
- `--help` 文档说明 local_vllm 需 VLLM_BASE_URL

### 5. agents/research_agent.py / report_agent.py

- 构造函数或 factory 接受 `llm_provider: str | None = None`，传给 `resolve_llm_client`
- **禁止** LLM 输出覆盖 `AgentContextBundle.experiments` 中的数值 metrics
- structured output（ResearchAgent）仍走现有 schema；LLM 只填 narrative 字段

### 6. text/ 边界（文档 only，minimal code）

- 在 docs/context_engineering.md 增加一节「M10 与 M6 文本边界」：
  - train_text_model.py 仍负责 signals parquet
  - LLM 不做 merge_text_signals；text OOS 仍须 walk-forward + compare_experiments
  - LoRA：text/lora_finetune.py 骨架，服务器手工，pytest 不下载 HF

### 7. tests

在 tests/test_context_engineering.py 或 tests/test_llm_providers.py 新增：

| 测试 | 要求 |
|------|------|
| resolve local_vllm without URL | warn + MockLLMClient |
| resolve local_vllm with mock HTTP | patch urlopen/httpx，断言 POST .../v1/chat/completions |
| use_llm=False | 始终 Mock，忽略 VLLM_BASE_URL |
| openai_compatible 回归 | 现有测试仍 pass |
| ResearchAgent use_llm=True + local_vllm mock | 返回结构化结果，metrics 不变 |

**禁止** pytest 访问真实 127.0.0.1:8000 或外网 API。

### 8. docs/context_engineering.md

增量章节：

| Provider | 环境变量 | 用途 |
|----------|----------|------|
| mock | 默认 | pytest、离线 |
| openai_compatible | LLM_API_KEY, LLM_BASE_URL, LLM_MODEL | DeepSeek 云端（EXP-LLM-001） |
| local_vllm | VLLM_BASE_URL, VLLM_MODEL | a6000 vLLM OpenAI 兼容端点 |

说明：vLLM 启动命令不在 M10 代码内（见 server_commands / 项目v3设计 M5.5）。

## 禁止

- pytest 联网调用 DeepSeek / vLLM / HuggingFace
- LLM 生成 target_weight、下单指令、或绕过 RiskTool
- 修改 walk-forward / backtest 核心逻辑以「适应 LLM」
- 虚构 EXP-TEXT-WF-002 或新 OOS sharpe
- commit llm.server.yaml 含真实 key

## 验收命令

python -m pytest tests/test_context_engineering.py -v
python -m pytest -v                                    # 全量 207+ passed
python scripts/run_research_agent.py --help
python scripts/generate_report.py --help

## 预期 pytest 增量

+3～+8 项（local_vllm mock），全量 **207 → 215** 左右（视实现而定）。
```

---

## Cursor 后续（Codex 完成后）

1. ~~更新 `docs/context_engineering.md` 与实现对齐~~ ✅
2. ~~更新 `docs/experiment_log.md` — **EXP-20260602-027**~~ ✅
3. ~~更新 `docs/progress.md`、`项目进度.md`、`项目v3设计.md` — M10 状态~~ ✅
4. 服务器 pull + pytest **212**（EXP-20260602-028）；M9 Postgres smoke（EXP-026）
5. 服务器 vLLM smoke → **EXP-LLM-002**
6. 科研：**EXP-TEXT-WF-002** — 扩大 text JSONL → walk-forward

**M9 服务器阻塞项**（与 M10 并行）：管理员 `usermod -aG docker weizian` 或代启 Postgres → `setup.sh` → EXP-026。

---

## 参考现有代码

| 模块 | 路径 |
|------|------|
| resolve_llm_client | `src/quant_mas/core/llm.py` |
| ResearchAgent | `src/quant_mas/agents/research_agent.py` |
| ReportAgent | `src/quant_mas/agents/report_agent.py` |
| ContextBuilder | `src/quant_mas/context/context_builder.py` |
| run_research_agent | `scripts/run_research_agent.py` |
| generate_report | `scripts/generate_report.py` |
| M6 text（边界） | `src/quant_mas/text/`、`features/text_signals.py` |
| test_context_engineering | `tests/test_context_engineering.py` |
| M5 prompt（历史） | `docs/codex_prompt_M5.md` |

---

## 与 M9 / M6 / M11 的关系

| 模块 | 关系 |
|------|------|
| **M9** 企业 DB | 无硬依赖；Memory/RAG 仍可用 json/sqlite/postgres |
| **M6** 文本 | M10 不替代 FinBERT merge；EXP-TEXT-WF-002 为 Cursor 科研 |
| **M11** 竞争学习 | 后续模块；M10 不实现 StrategyAgent |
| **M5** | M10 为 M5.5（local vLLM）的代码落地 |

---

## 实验编号（验收后写入 experiment_log）

| 编号 | 内容 |
|------|------|
| **EXP-20260602-027** | M10 local_vllm 本地 pytest + resolve_llm_client ✅ |
| **EXP-20260602-028** | M10 服务器 pytest 212（待 pull） |
| **EXP-LLM-002** | 服务器 vLLM ResearchAgent smoke（待 vLLM 服务） |
| **EXP-TEXT-WF-002** | 扩大 text 覆盖 walk-forward OOS（科研，Cursor 手工） |

论文主指标仍为 **EXP-20260602-008**（oos.sharpe **0.586**）。
