# Plus M5：上下文工程与真实 LLM 接入 — Codex 提示词

**状态：✅ 已完成（EXP-20260602-017，150 passed / 1 warning，2026-06-03）**

更新时间：2026-06-03

> **用法**：先粘贴下方「固定前缀」，再粘贴「M5 主任务」整段交给 Codex。  
> **设计依据**：[项目plus设计.md §M5](../项目plus设计.md#m5上下文工程与真实-llm-接入) · 前置：**M1–M4 ✅**（EXP-20260602-015/016）

---

## 固定前缀（每次必贴）

```
你正在开发 Quant MAS 科研项目。
路径：D:\scientific reasearch and work\SRTP\Quant MAS

测试基线：本地 **137 passed, 1 skipped**（138 项；Plus M4，EXP-20260602-015）；
含 orchestration **138 passed**；服务器 langgraph backend ✅（EXP-20260602-016 @ c0fa5e3）。
OOS 主 baseline：EXP-20260602-008，oos.sharpe **0.586**。

硬性原则：
1. LLM **不允许**直接实盘下单；不得输出 target_weight / 订单 / broker 指令。
2. pytest **不联网、不调真实 LLM**；OpenAICompatibleLLMClient 在测试中必须 mock HTTP 或使用 MockLLMClient。
3. **事实指标与 LLM 解释分离**：metrics、artifacts、ExperimentMemory 记录由 Quant Engine 产生，LLM 只生成 narrative / hypothesis / suggestions。
4. 默认 **use_llm=False**；无 LLM_API_KEY 时 CLI 与 Agent 须完整跑通（Mock 路径）。
5. 请只实现当前 **M5** 一个模块；改完后 `python -m pytest -v` 全量通过（预期 137+，新增 test_context_engineering）。
6. **不替换** SupervisorAgent 规则路由；ResearchAgent 为**新增**研究解释 Agent，与 run_agent.py 并存。
7. 不要把 data/、outputs/、models/、logs/ 大文件加入 git；不要提交 .env 或真实 API key；日志不得打印 key。
```

---

## M5 主任务（复制给 Codex）

```
请为 Quant MAS v2 实现上下文工程与可选真实 LLM 接入（Plus M5）。

## 背景

v1 / Plus 已有：
- core/llm.py — LLMClient、MockLLMClient（tests/test_agent_core.py 已用）
- agents/report_agent.py — ReportAgent.generate_report(title, metrics, notes)
- agents/supervisor_agent.py — 规则路由，**无 LLM**
- memory/ — ExperimentMemory、JsonMemoryStore、SqliteMemoryStore、create_memory_store
- rag/ — SimpleRetriever、HybridRetriever、HashEmbeddingClient、index_documents / query_memory CLI
- orchestration/ — QuantWorkflowState、ResearchWorkflow dry-run（M4）
- scripts/generate_report.py — 仅定位 latest summary.md，**未**调 LLM
- utils/env.py — load_repo_dotenv()

Plus M1 compare_experiments 与 OOS baseline 0.586 为论文主指标；M5 输出须**引用**这些事实，不得篡改。

## 目标

1. **Context Layer**：从 Memory / RAG / metrics / 可选 workflow state 构建结构化上下文包。
2. **LLM Layer**：OpenAI 兼容客户端（DeepSeek / vLLM / OpenAI），env 配置，pytest 全 mock。
3. **ResearchAgent**：基于上下文输出研究假设、证据摘要、建议实验（JSON 结构），**不下单**。
4. **ReportAgent 增强**：可选 LLM 叙事层；metrics 原样保留。
5. **CLI**：run_research_agent.py；generate_report.py 增加 --use-llm（默认 false）。

第一版重点：**无 key 可跑** + mock pytest 全绿；真实 LLM 仅服务器手工验证（EXP-LLM-001，不虚构）。

## 需要实现的文件

### 1. 包结构

src/quant_mas/context/
  __init__.py              # 导出主要类型
  context_schema.py        # 结构化上下文 schema
  context_builder.py       # 从 Memory/RAG/metrics 构建
  compression.py           # 截断/压缩，保留关键 metric

configs/context.yaml       # 默认 top_k、max_chars、metric_keys
configs/llm.yaml           # provider、model、timeout（可被 env 覆盖）

### 2. context_schema.py

使用 dataclass 或 TypedDict，至少包含：

- MarketContextSnapshot — symbols、date_range、row_counts（**不要**塞完整 DataFrame）
- ExperimentContextSnapshot — experiment_id、name、family、metrics（扁平 + 嵌套 oos.*）、artifacts 路径摘要
- RiskContextSnapshot — approved、status、violations 列表（来自 workflow 或 RiskTool 结果）
- RagContextChunk — doc_id、path、title、snippet、score
- AgentContextBundle — 聚合上述 + task: str、baseline_ref: str（默认 "EXP-20260602-008"）、built_at: str

提供 `to_dict()` / `from_dict()` 或 `model_dump` 风格序列化，便于 JSON CLI 输出。

### 3. context_builder.py

```python
class ContextBuilder:
    def __init__(
        self,
        *,
        memory_store: MemoryStore | None = None,
        retriever: SimpleRetriever | HybridRetriever | None = None,
        storage_config: str = "configs/storage.yaml",
        context_config: str = "configs/context.yaml",
    ): ...

    def build(
        self,
        *,
        task: str,
        experiment_name: str | None = None,
        rag_query: str | None = None,
        workflow_state: dict | None = None,  # 可选 QuantWorkflowState 快照
        metric_keys: list[str] | None = None,
    ) -> AgentContextBundle: ...
```

实现要点：
- 默认从 ExperimentMemory / create_memory_store 读 latest 或按 name 搜索
- `find_best("oos.sharpe")` 或等价，把 baseline 实验写入 bundle
- RAG：优先 SimpleRetriever（不硬依赖向量库）；若 index 存在可尝试 HybridRetriever
- workflow_state：提取 metrics、artifacts、completed_nodes、errors（若有）
- **不**在 builder 内调用 LLM

### 4. compression.py

- `compress_metrics(metrics: dict, *, keep_keys: list[str]) -> dict`
  - 默认 keep：`oos.sharpe`、`oos.total_return`、`oos.max_drawdown`、`total_return`、`sharpe`、`max_drawdown`、`test_auc`
  - 嵌套 metric 用点路径或保留 `oos` 子 dict
- `truncate_text(text: str, max_chars: int) -> str`
- `compress_rag_chunks(chunks: list[RagContextChunk], *, max_chunks: int, max_chars: int) -> list[RagContextChunk]`
- ContextBuilder 在返回前调用 compression，避免 prompt 过长

### 5. core/llm.py 增强

保留 LLMClient、MockLLMClient 现有行为。

新增：

```python
class OpenAICompatibleLLMClient(LLMClient):
    """Chat completions via OpenAI-compatible HTTP API (DeepSeek, vLLM, etc.)."""

def resolve_llm_client(
    *,
    provider: str | None = None,  # mock | openai_compatible
    use_llm: bool = False,
) -> LLMClient:
    """Read LLM_* from os.environ (after load_repo_dotenv). No key → MockLLMClient."""
```

.env / .env.example 增量（占位符，不提交真实 key）：

```env
LLM_PROVIDER=mock
LLM_BASE_URL=https://api.deepseek.com
LLM_API_KEY=
LLM_MODEL=deepseek-chat
LLM_TIMEOUT_SECONDS=60
```

实现要点：
- HTTP 用 **stdlib urllib** 或 optional httpx（若加 optional-dependencies llm，核心 pytest 仍 mock，不硬依赖）
- 请求体 OpenAI chat/completions 格式；解析 choices[0].message.content
- 错误时 raise 清晰异常；**禁止**在异常/message 中包含 API key
- `resolve_llm_client(use_llm=False)` 始终 MockLLMClient
- `use_llm=True` 且无 key → MockLLMClient 并 warn，或 raise 明确错误（CLI 文档说明）

可选 pyproject.toml：

```toml
[project.optional-dependencies]
llm = [
    "httpx>=0.25",
]
```

### 6. agents/research_agent.py

```python
@dataclass
class ResearchAgentOutput:
    hypothesis: str
    evidence_summary: str
    suggested_experiments: list[str]
    risks_and_caveats: str
    llm_provider: str  # "mock" | "openai_compatible"
    context_snapshot: dict  # AgentContextBundle.to_dict() 摘要

class ResearchAgent(BaseAgent):
    def run_research(self, bundle: AgentContextBundle) -> ResearchAgentOutput: ...
```

System prompt 必须包含：
- 你是量化**研究**助手，不是交易员
- 不得建议实盘、不得输出具体仓位
- 必须区分「事实 metrics（只读）」与「LLM 推断」
- 建议实验须可执行（如 walk-forward、特征 ablation），且应提及与 OOS baseline 0.586 对比

输出：优先让 LLM 返回 **JSON**；解析失败时 fallback 为纯文本包在 ResearchAgentOutput.evidence_summary。

### 7. ReportAgent 增强

- `generate_report(..., *, use_llm: bool = False) -> str | ReportResult`
- 若 `use_llm=False`：行为与现有一致（MockLLMClient 仍走 LLM 边界，但 CLI 默认 mock）
- 新增 `ReportResult`（可选 dataclass）：`metrics: dict`（原样）、`narrative: str | None`、`facts_markdown: str`
- LLM **不得**修改传入的 metrics dict（测试：传入 metrics 与返回 metrics 深度相等）
- system prompt 强调：summary 不能捏造未提供的 metric

### 8. scripts/run_research_agent.py

CLI 参数：
- `--task`（必填，研究问题，如 "Compare latest ML backtest to walk-forward OOS baseline"）
- `--use-llm` / `--no-use-llm`（默认 **false** → MockLLMClient）
- `--storage-config`、`--memory-backend json|sqlite`、`--json-path`、`--sqlite-path`
- `--rag-query`（可选，拉 RAG 上下文）
- `--experiment-name`（可选，指定实验而非 latest）
- `--workflow-json`（可选，读 M4 输出 state JSON 路径）
- `--context-config`、`--output-json`（写 ResearchAgentOutput + bundle 摘要）

`--help` 必须可用。exit code：成功 0，异常 1。

无 API key 时默认 mock 跑通并打印 JSON。

### 9. scripts/generate_report.py 增强

- 新增 `--use-llm`（默认 **false**）
- false：保持现有「定位 latest summary.md」行为
- true：读 latest ExperimentMemory → ContextBuilder 或直接用 metrics → ReportAgent(use_llm=True) → 打印/写入 narrative（**不覆盖**原 summary.md 除非 `--output` 指定）

### 10. configs/context.yaml

```yaml
context:
  max_rag_chunks: 5
  max_snippet_chars: 400
  max_bundle_chars: 8000
  metric_keys:
    - oos.sharpe
    - oos.total_return
    - oos.max_drawdown
    - sharpe
    - total_return
    - max_drawdown
    - test_auc
  baseline_experiment_hint: EXP-20260602-008
```

### 11. tests/test_context_engineering.py（新增，≥12 项）

全部 **不联网**：

1. context_schema 序列化/反序列化
2. compress_metrics 保留 oos.sharpe 等，丢弃大字段
3. truncate_text / compress_rag_chunks 边界
4. ContextBuilder + tmp_path synthetic ExperimentMemory → bundle 含 experiment snapshot
5. ContextBuilder + SimpleRetriever fixture → rag chunks 非空
6. ContextBuilder + workflow_state dict → risk/metrics 字段
7. resolve_llm_client(use_llm=False) → MockLLMClient
8. resolve_llm_client(use_llm=True, 无 key) → Mock 或明确错误（与实现一致，文档化）
9. OpenAICompatibleLLMClient：mock HTTP（unittest.mock patch urllib/httpx）返回固定 JSON
10. ResearchAgent.run_research mock → ResearchAgentOutput 字段齐全；输出无 "buy"/"sell order" 等（简单 substring 或 regex）
11. ReportAgent：use_llm=False 时 metrics 不被 LLM 改写（deepcopy 断言）
12. run_research_agent.py --help（subprocess）
13. generate_report.py --help 仍可用；--use-llm false 不改变原行为（subprocess 或 import）
14. test_supervisor_agent.py、test_agent_core.py **保持通过**（不得破坏）

可选：ContextBuilder.find_best 与 EXP-20260602-008 风格嵌套 metric 一致（用 fixture json）。

## 兼容性要求

- **不得修改** SupervisorAgent 路由逻辑；test_supervisor_agent.py 全绿
- **不得修改** Quant Engine 训练/回测/风控核心算法
- ExperimentMemory / MemoryStore API 保持向后兼容
- M4 orchestration dry-run 不受影响
- test_memory_store_v2.py、test_memory_rag.py、test_langgraph_workflow.py 保持通过

## 禁止

- LLM 输出订单、target_weight、broker 指令
- pytest 调用真实 DeepSeek/OpenAI/vLLM
- 在日志/异常中打印 LLM_API_KEY
- 用 LLM 生成的数字**覆盖** ExperimentMemory metrics
- 删除 MockLLMClient 或破坏 test_agent_core 现有用例

## 验收命令

python -m pytest tests/test_context_engineering.py -v
python -m pytest tests/test_agent_core.py -v
python -m pytest tests/test_supervisor_agent.py -v
python -m pytest -v                                    # 全量 137+ passed
python scripts/run_research_agent.py --help
python scripts/run_research_agent.py --task "Summarize OOS baseline vs latest ML run"
python scripts/generate_report.py --help
python scripts/generate_report.py --latest             # 无 LLM，行为不变

# 服务器可选（有 key 时，不写入 pytest）：
# LLM_PROVIDER=openai_compatible LLM_API_KEY=... python scripts/run_research_agent.py --task "..." --use-llm
```

---

## Cursor 后续（Codex 完成后）

1. 新增 `docs/context_engineering.md`：ContextBundle 字段、压缩策略、mock vs 真实 LLM、与 OOS baseline 关系。
2. 更新 `docs/architecture.md` — Context Layer + LLM 边界图。
3. 更新 `.env.example` — LLM_* 占位符。
4. 更新 `项目进度.md`、`docs/experiment_log.md`：
   - 本地 EXP-20260602-017（M5 pytest）
   - 服务器 EXP-20260602-018（若 pull 后 137+ 通过）
5. 服务器可选 smoke（**不写入 pytest**）：
   ```bash
   python scripts/run_research_agent.py --task "Explain walk-forward OOS sharpe baseline" --use-llm
   ```
   记录 **EXP-LLM-001**（token 用量、输出样例）；无 key 则只记 mock smoke。
6. **不要**虚构 LLM 输出质量指标；未跑真实 LLM 则标「待验证」。

---

## 参考现有代码

| 模块 | 路径 |
|------|------|
| LLM 边界 | `src/quant_mas/core/llm.py` |
| BaseAgent | `src/quant_mas/core/agent.py` |
| ReportAgent | `src/quant_mas/agents/report_agent.py` |
| SupervisorAgent | `src/quant_mas/agents/supervisor_agent.py` |
| MemoryStore | `src/quant_mas/memory/factory.py`、`store_base.py` |
| RAG | `src/quant_mas/rag/simple_retriever.py`、`hybrid_retriever.py` |
| Workflow state | `src/quant_mas/orchestration/langgraph_state.py` |
| env 加载 | `src/quant_mas/utils/env.py` |
| 研究基线 | `src/quant_mas/research/baseline.py`、`docs/research_protocol.md` |
| Agent 测试模式 | `tests/test_agent_core.py` |

---

## 与 M4 / Supervisor 的关系

| 维度 | SupervisorAgent | ResearchWorkflow (M4) | ResearchAgent (M5) |
|------|-----------------|-------------------------|---------------------|
| 触发 | 用户 task → 一个 Tool | 固定 6 步 DAG | 研究问题 → 上下文 + 可选 LLM |
| LLM | 无 | 无 | **可选**（解释/假设/建议） |
| 输出 | ToolResult | state.metrics / artifacts | ResearchAgentOutput JSON |
| 下单 | 禁止 | 禁止 | **禁止** |

M6 文本模型与 M3.5 企业 RAG 为后续扩展；M5 第一版 **不依赖** 真 Embedding API。
