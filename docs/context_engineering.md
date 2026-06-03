# 上下文工程与 LLM 接入（Plus M5）

更新时间：2026-06-03

> 配置：`configs/context.yaml`、`configs/llm.yaml` · CLI：`scripts/run_research_agent.py`  
> Codex 任务：[codex_prompt_M5.md](codex_prompt_M5.md)

## 定位

M5 在 Quant Engine（确定性）与可选 LLM（解释层）之间增加 **Context Layer**：

| 层级 | 职责 | 是否可改 metrics |
|------|------|------------------|
| Quant Engine | 数据、训练、回测、风控 | 是（实验产物） |
| ContextBuilder | Memory/RAG/workflow → 结构化 bundle | 否 |
| ResearchAgent / ReportAgent | 假设、证据摘要、叙事 | **否**（只读事实） |

**硬性原则**：LLM 不直接下单；默认 `use_llm=False`；无 `LLM_API_KEY` 时安全回退 `MockLLMClient`。

## 组件

```text
ExperimentMemory / workflow state / RAG
        ↓
ContextBuilder → AgentContextBundle（compression）
        ↓
ResearchAgent / ReportAgent
        ↓
resolve_llm_client(use_llm=...) → MockLLMClient | OpenAICompatibleLLMClient
```

| 模块 | 路径 |
|------|------|
| Schema | `src/quant_mas/context/context_schema.py` |
| Builder | `src/quant_mas/context/context_builder.py` |
| Compression | `src/quant_mas/context/compression.py` |
| LLM | `src/quant_mas/core/llm.py` — `resolve_llm_client` |
| ResearchAgent | `src/quant_mas/agents/research_agent.py` |
| ReportAgent | `src/quant_mas/agents/report_agent.py` — `ReportResult` |

## AgentContextBundle 字段

- `task` — 研究问题
- `experiments` — 实验 metrics/artifacts 摘要（无 DataFrame）
- `baseline` — OOS baseline 引用（默认 **EXP-20260602-008**，oos.sharpe **0.586**）
- `risk` — 风控 approved/status/violations
- `rag_chunks` — 文档检索片段
- `workflow` — 可选 M4 `QuantWorkflowState` 摘要

`compression.py` 保留 `oos.sharpe` 等关键 metric，截断 RAG 与文本长度（见 `configs/context.yaml`）。

## 环境变量（`.env`，勿 commit）

```env
LLM_PROVIDER=mock
LLM_BASE_URL=https://api.deepseek.com
LLM_API_KEY=
LLM_MODEL=deepseek-chat
LLM_TIMEOUT_SECONDS=60
```

可选依赖：`python -m pip install -e ".[llm]"`（httpx，仅真实 HTTP 客户端需要；pytest 仍 mock）。

## 本地 / pytest

```bash
python -m pytest tests/test_context_engineering.py -v   # 12 passed, 1 warning（无 key 回退 Mock，预期）
python -m pytest -v                                   # 150 passed, 1 warning
python scripts/run_research_agent.py --help
python scripts/run_research_agent.py --task "Summarize OOS baseline vs latest ML run"
python scripts/generate_report.py --latest              # 无 LLM
python scripts/generate_report.py --latest --use-llm    # 有 key 时用真实 LLM；无 key 回退 Mock
```

## 与 Supervisor / M4 的关系

| 入口 | 用途 |
|------|------|
| `run_agent.py` | Supervisor 规则路由 → 单 Tool |
| `run_langgraph_workflow.py` | M4 固定 6 步 DAG |
| `run_research_agent.py` | M5 研究解释（可选 LLM） |

三者并存；Supervisor **未被替换**。

## 服务器 smoke（DeepSeek 云端，不写入 pytest）

```bash
cd /mnt/localDisk3/weizian/Quant-MAS
git pull origin main
conda activate /mnt/localDisk3/weizian/conda_envs/quant-mas
python -m pip install -e ".[llm]"

# .env 示例（勿 commit）
# LLM_PROVIDER=openai_compatible
# LLM_BASE_URL=https://api.deepseek.com
# LLM_API_KEY=sk-...
# LLM_MODEL=deepseek-chat

python -m pytest -v   # 150 passed（有 .env 时也须全绿，见 mistakes.md M-017）

python scripts/run_research_agent.py \
  --storage-config configs/storage.server.yaml \
  --json-path /mnt/localDisk3/weizian/reports/experiments.json \
  --task "Explain walk-forward OOS sharpe baseline and compare to latest ML run" \
  --use-llm
```

成功时 JSON 中 `"llm_provider"` 应为 **`openai_compatible`**（不是 `mock`）。  
`baseline: null` 通常是因为默认 `experiments.json` 路径不对；务必用 `--storage-config storage.server.yaml` 或 `--json-path` 指向服务器真实 memory。

记录 **EXP-LLM-001**（输出摘要、latency；**不写 key**）。本地 vLLM 见 [项目plus设计.md §M5.5](../项目plus设计.md#m55服务器本地-vllm-进阶待定)。

## 相关文档

- [architecture.md](architecture.md)
- [research_protocol.md](research_protocol.md) — OOS 主指标
- [项目plus设计.md §M5](../项目plus设计.md#m5上下文工程与真实-llm-接入)
