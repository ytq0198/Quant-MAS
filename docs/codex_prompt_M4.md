# Plus M4：LangGraph 工作流编排 — Codex 提示词

**状态：✅ 已完成（EXP-20260602-015，136 passed / 1 skipped，2026-06-02）**

更新时间：2026-06-02  

> 运行说明：[langgraph_workflow.md](langgraph_workflow.md) · 设计：[项目plus设计.md §M4](../项目plus设计.md#m4langgraph-工作流编排)

---

## 固定前缀（每次必贴）

```
你正在开发 Quant MAS 科研项目。
路径：D:\scientific reasearch and work\SRTP\Quant MAS

测试基线：本地 + 服务器 **126 passed**（Plus M3，EXP-20260602-013/014）。
OOS 主 baseline：EXP-20260602-008，oos.sharpe **0.586**。

硬性原则：
1. LLM 不允许直接实盘下单；workflow 不得接 broker。
2. pytest 不联网、不调真实 LLM；M4 第一版以 **--dry-run** + mock/synthetic 为主。
3. **不替换** SupervisorAgent；LangGraph 为**并存**的实验性 ResearchWorkflow。
4. 请只实现当前 **M4** 一个模块；改完后 `python -m pytest -v` 全量通过（预期 126+，新增 test_langgraph_workflow）。
5. 不要把 data/、outputs/、models/、logs/ 大文件加入 git；不要提交 .env 或真实 API key。
6. 每个 workflow 节点**只调用现有 Tool 或 pipeline 内已有函数**，不要重写 Quant Engine 逻辑。
```

---

## M4 主任务（复制给 Codex）

```
请为 Quant MAS v2 增加实验性 LangGraph 编排层（Plus M4）。

## 背景

v1 已有：
- SupervisorAgent（规则路由，单步调 Tool）— src/quant_mas/agents/supervisor_agent.py
- ToolRegistry + 7 个 Tool：data_summary / backtest / train_model / report / risk_check / ml_backtest / pipeline
- AgentEvent / ToolCallEvent / AgentFinishEvent — src/quant_mas/core/events.py
- run_quant_pipeline — src/quant_mas/pipeline.py
- scripts/run_pipeline.py、run_ml_backtest.py、train_model.py

Plus M1–M3 已完成；新 workflow 产出须可写入 ExperimentMemory，并与 M1 compare_experiments 兼容。

## 目标

实现 **ResearchWorkflow** 有状态 DAG（与 Supervisor **并存，不替换**）：

DataCheck → FeatureBuild → TrainModel → MLBacktest → RiskCheck → Report

第一版重点：
- **dry-run 可跑**（mock Tool / synthetic 小数据，不联网）
- **LangGraph 可选**：装了 langgraph 用 StateGraph；未安装则 **SequentialWorkflowRunner** 按同顺序执行（pytest 必须能在无 langgraph 时全绿）
- 每步记录 **WorkflowEvent**（复用或扩展 AgentEvent 风格），写入 state.events
- 任一步失败 → state.errors 追加消息，后续节点可 skip 或短路（配置决定，默认遇错停止）

## 需要实现的文件

### 1. 包结构

src/quant_mas/orchestration/
  __init__.py
  langgraph_state.py      # QuantWorkflowState
  workflow_events.py      # WorkflowNodeEvent / WorkflowFinishEvent（或复用 core.events）
  node_context.py         # 传给节点的 paths、configs、dry_run 标志
  nodes.py                # 6 个 node 函数
  sequential_workflow.py  # 无 langgraph 时的顺序 runner
  langgraph_workflow.py   # build_langgraph_workflow() / run_langgraph_workflow()
  registry.py             # create_default_tool_registry() 供 workflow 注入 mock

### 2. langgraph_state.py

TypedDict 或 dataclass，至少包含：

- task: str
- dry_run: bool
- storage_config: str
- features_config: str
- train_config: str
- ml_backtest_config: str
- risk_config: str
- raw_path: str | None
- features_path: str | None
- model_path: str | None
- report_output_dir: str | None
- targets_path: str | None          # RiskCheck 用
- equity_path: str | None           # RiskCheck 可选
- current_node: str | None
- completed_nodes: list[str]
- errors: list[str]
- events: list[dict]                # 可序列化 event 快照
- artifacts: dict[str, str]
- metrics: dict[str, Any]

提供 `initial_state(**kwargs) -> QuantWorkflowState` 工厂。

### 3. nodes.py（每节点只调 Tool 或已有函数）

| 节点 | 职责 | 实现要点 |
|------|------|----------|
| data_check | 检查 raw/features 路径 | dry_run：仅检查 tmp 下 synthetic 文件存在；真实模式：ParquetStorage.exists + DataSummaryTool 或 validate_ohlcv |
| feature_build | 构建特征 | 调 build_feature_table_from_config（与 pipeline 相同）；dry_run：写 tiny synthetic parquet |
| train_model | 训练 | 调 TrainModelTool；dry_run：注入 mock model_factory，不写大模型文件 |
| ml_backtest | ML 回测 | 调 MLBacktestTool；dry_run：mock model + synthetic features |
| risk_check | 风控 | 调 RiskTool；dry_run：synthetic targets CSV/parquet |
| report | 报告 | 调 ReportTool；dry_run：读已有 summary 或写 stub summary.md |

每个 node 函数签名：`def node_xxx(state: QuantWorkflowState, *, tools: ToolRegistry, context: NodeContext) -> QuantWorkflowState`

- 成功：append completed_nodes、写 events、更新 artifacts/metrics/paths
- 失败：append errors，不抛未捕获异常（让 graph 结束）

### 4. sequential_workflow.py

- `NODE_ORDER = ["data_check", "feature_build", "train_model", "ml_backtest", "risk_check", "report"]`
- `run_sequential_workflow(state, *, tools, stop_on_error=True) -> QuantWorkflowState`
- 按顺序调用 nodes.py；遇 state.errors 且 stop_on_error 则 break

### 5. langgraph_workflow.py

- `LANGGRAPH_AVAILABLE = True/False`（import langgraph 失败则为 False）
- `build_langgraph_workflow(tools) -> CompiledGraph | None`
- 用 StateGraph 连边：START → data_check → … → report → END
- `run_langgraph_workflow(state, *, tools) -> QuantWorkflowState`
- langgraph 未安装时 raise ImportError 并提示用 sequential

### 6. configs/langgraph_workflow.yaml

```yaml
workflow:
  name: research_ml_workflow
  stop_on_error: true
  default_dry_run: true
paths:
  storage_config: configs/storage.yaml
  features_config: configs/features.yaml
  train_config: configs/train.yaml
  ml_backtest_config: configs/backtest_ml.yaml
  risk_config: configs/risk.yaml
nodes:
  - data_check
  - feature_build
  - train_model
  - ml_backtest
  - risk_check
  - report
```

### 7. scripts/run_langgraph_workflow.py

CLI 参数：
- `--dry-run`（默认 true，或读 yaml default_dry_run）
- `--backend sequential|langgraph`（默认 sequential；langgraph 未安装时自动 fallback sequential 并 warn）
- `--storage-config`、`--task`（描述字符串，写入 state.task）
- `--output-json`（可选，写最终 state 快照）
- `--stop-on-error / --no-stop-on-error`

`--help` 必须可用。exit code：有 errors 则 1，否则 0。

### 8. pyproject.toml（可选依赖，不进核心 pytest 硬依赖）

```toml
[project.optional-dependencies]
orchestration = [
    "langgraph>=0.2.0",
]
```

核心 `pip install -e .` 不装 langgraph；文档说明 `pip install -e ".[orchestration]"` 可选。

### 9. tests/test_langgraph_workflow.py（新增，≥10 项）

全部使用 tmp_path + synthetic/mock，**不联网**：

1. `initial_state` 字段默认值
2. `run_sequential_workflow` dry_run 跑通 6 节点，`completed_nodes` 长度 6
3. 节点顺序严格等于 NODE_ORDER（可从 events 的 node 名断言）
4. 某 node 故意失败（mock Tool raise）→ `errors` 非空，`stop_on_error` 时后续未执行
5. `--no-stop-on-error` 或等价 flag 时继续（若实现）
6. dry_run 不写网络、不调用 YFinanceFetcher
7. events 列表含每步 tool_call 或 node 完成记录
8. `run_langgraph_workflow.py --help`（subprocess 或 import main）
9. langgraph 相关测试：`pytest.importorskip("langgraph")` 后 build graph 并 dry_run 一次
10. SupervisorAgent 仍可用（import + 简单 route 冒烟，确保未破坏）

可选：对比 sequential dry_run 与 langgraph dry_run 的 completed_nodes 一致。

## 兼容性要求

- **不得修改** SupervisorAgent 对外行为；test_supervisor_agent.py 全部保持通过
- **不得删除** 现有 Tool；可新增 orchestration 专用 mock registry
- test_quant_tools.py、test_end_to_end_pipeline.py 保持通过
- ML 训练/回测 dry_run 可用现有 test 里的 mock model 模式（参考 test_ml_signal_strategy、test_quant_tools）

## 禁止

- 用 LangGraph 替换 SupervisorAgent 或 run_agent.py 默认路径
- workflow 内直接 broker 下单、调 LLM、调真实 download API
- pytest 硬依赖 langgraph 安装（未安装时 skip langgraph 专用用例，其余全绿）
- 在测试中写死服务器绝对路径

## 验收命令

python -m pytest tests/test_langgraph_workflow.py -v
python -m pytest tests/test_supervisor_agent.py -v
python -m pytest -v                                    # 全量 126+ passed
python scripts/run_langgraph_workflow.py --help
python scripts/run_langgraph_workflow.py --dry-run --backend sequential
# 可选（已装 langgraph）：
python scripts/run_langgraph_workflow.py --dry-run --backend langgraph
```

---

## Cursor 后续（Codex 完成后）

1. 新增 `docs/langgraph_workflow.md`：Mermaid 节点图、dry-run vs 服务器真实运行、与 Supervisor 对比表。
2. 更新 `docs/architecture.md` Orchestration Layer。
3. 更新 `项目进度.md`、`docs/experiment_log.md`：
   - 本地 EXP-20260602-015（M4 pytest）
   - 服务器 EXP-20260602-016（若 pull 后 126+ 通过）
4. 服务器 smoke（不联网）：
   ```bash
   python scripts/run_langgraph_workflow.py --dry-run --backend sequential
   ```
5. **真实 workflow**（耗 GPU/数据）仅在有意做 EXP-LG-001 时跑；未跑不虚构 metrics。

---

## 参考现有代码

| 模块 | 路径 |
|------|------|
| SupervisorAgent | `src/quant_mas/agents/supervisor_agent.py` |
| Events | `src/quant_mas/core/events.py` |
| Tools | `src/quant_mas/tools/quant/`、`quant.py` |
| Pipeline | `src/quant_mas/pipeline.py` |
| PipelineTool | `src/quant_mas/tools/quant/pipeline_tool.py` |
| MLBacktestTool | `src/quant_mas/tools/quant/ml_backtest_tool.py` |
| RiskTool | `src/quant_mas/tools/quant/risk_tool.py` |
| 端到端测试模式 | `tests/test_end_to_end_pipeline.py`、`tests/test_quant_tools.py` |

---

## 与 Supervisor 的关系（写进代码 docstring）

| 维度 | SupervisorAgent | ResearchWorkflow (M4) |
|------|-----------------|-------------------------|
| 触发 | 用户一句 task → 一个 Tool | 固定 6 步 DAG |
| 状态 | 单步 events | 跨节点 QuantWorkflowState |
| LLM | 无（规则路由） | 无（M4 第一版） |
| 用途 | 交互式单任务 | 可复现研究流水线 PoC |

M5 再接 LLM 时，ResearchAgent 可读 workflow 最终 state，**仍不直接下单**。
