# M13 MCP Scheduler Protocol

更新时间：2026-06-04

本文记录 Quant MAS v3 **M13：企业化编排与协议扩展** 的第一版设计。M13 的目标不是发现新的 alpha，而是把已经完成的研究链路变成可复现、可审计、可扩展的调度协议。

## 定位

M13 位于 Orchestration Layer，扩展已有 M4 ResearchWorkflow 与 M8 MCP/A2A 协议层。

M13 不替换：

- `run_agent.py` / `SupervisorAgent`
- `scripts/run_langgraph_workflow.py`
- Quant Engine 的训练、回测、风控、walk-forward 计算
- 已有 ExperimentMemory / compare_experiments 逻辑

M13 第一版只做内部调度骨架：

- 不接外部 MCP server listener
- 不开 WebSocket / HTTP 调度服务
- 不调用真实 LLM
- 不直接接 broker / order / shell 工具
- 默认 dry-run

## 分阶段设计

### M13.0：MCP Scheduler Minimal

这是当前应优先实现的最小闭环。

目标：

1. 定义多 Agent / 多节点调度消息。
2. 实现内部 dry-run scheduler。
3. 复用 `ToolPolicy`，继续拒绝 shell / broker / order / secrets。
4. 写入 append-only audit JSONL。
5. 提供 `scripts/run_mcp_pipeline.py` CLI。

建议交付：

| 组件 | 路径 | 说明 |
|------|------|------|
| 通信 | `src/quant_mas/orchestration/agent_communication.py` | `AgentMessage`、`PlanMessage`、`NodeResultMessage`、`AuditMessage`、`InMemoryMessageBus` |
| 调度 | `src/quant_mas/orchestration/mcp_scheduler.py` | mock DAG / sequential dry-run scheduler |
| 审计 | `src/quant_mas/orchestration/audit_log.py` | append/read/summarize JSONL |
| CLI | `scripts/run_mcp_pipeline.py` | `--dry-run` 默认、`--list-recipes`、`--output-dir` |
| 测试 | `tests/test_mcp_scheduler.py` | mock-only，不联网 |

M13.0 最小验收：

- dry-run 调度至少 2 个 mock 实验节点
- audit JSONL 可写、可读、可汇总
- `ToolPolicy` 仍拒绝 `shell` / `broker` / `order` / `secrets`
- `python scripts/run_mcp_pipeline.py --help` 正常
- `python -m pytest tests/test_mcp_scheduler.py -v` 通过
- 全量 `python -m pytest -v` 通过

### M13.1：Pipeline Recipe Scheduler

在 M13.0 稳定后扩展 YAML recipe。

目标：

- 将 ML baseline、Text enhanced、Population OOS、RL ablation 四条研究链路声明为 recipe。
- 支持拓扑排序、循环依赖检测、节点 metric family 声明。
- 将 `docs/server_commands.md` 中的手工流程固化为可审计配置。

候选配置：

- `configs/pipelines/ml_baseline.yaml.example`
- `configs/pipelines/text_enhanced.yaml.example`
- `configs/pipelines/population_oos.yaml.example`
- `configs/pipelines/rl_ablation.yaml.example`

关键约束：

- `rl_train` 只能写 `training.*` / `simulation.*`
- `walk_forward_eval`、`validate_candidate_oos`、`batch_validate_candidates` 才允许进入 walk-forward 指标族
- `text_enhanced` 必须包含 text coverage audit 节点，且在 walk-forward 前执行

### M13.2：LangGraph Extended DAG

将 M13.1 的 recipe 映射到可选 LangGraph backend。

范围：

- 保留 M4 的 6 节点 workflow。
- 新增 Population、RL、batch walk-forward 的实验节点。
- LangGraph 作为可选 backend，核心 pytest 不依赖 LangGraph 安装。

### M13.3：Paper Artifact Export

将已完成实验导出为论文级审计包。

输出：

- 主结果表
- 文本消融表
- Population 消融表
- RL 消融表
- 实验索引
- audit trail summary

规则：

- 论文主指标仍为 EXP-20260602-008 的 walk-forward OOS `oos.sharpe = 0.586`
- `simulation.*` 不得进入主结果表
- 文本实验必须同时报告 coverage、aligned count、dropped count、fillna 规则与 OOS metrics

## Metric Family 边界

| family | 可包含指标 | 可写入论文主结论 |
|--------|------------|------------------|
| `walk_forward` | `oos.*` | 是 |
| `audit` | coverage、dropped、aligned、artifact count | 否，但必须作为解释上下文 |
| `training` | loss、step count、policy update count | 否 |
| `simulation` | simulation reward / sharpe | 否 |
| `population` | Elo、population rank、candidate count | 否 |

M13 调度层只记录和检查 metric family，不重写 walk-forward 或 backtest 数学。

## Audit JSONL

建议字段：

```json
{
  "timestamp": "2026-06-04T12:00:00",
  "pipeline_id": "text_enhanced",
  "run_id": "text_enhanced_20260604_120000",
  "node_id": "audit_text_signals",
  "status": "success",
  "metric_family": "audit",
  "duration_ms": 12,
  "artifacts": {"summary": "outputs/pipelines/.../summary.md"},
  "error": null
}
```

审计日志默认写入：

```text
outputs/pipelines/<run_id>/audit.jsonl
```

pytest 必须使用 `tmp_path`，不能写真实服务器路径。

## 与 M4 / M8 的区别

| 层 | 作用 | 状态 |
|----|------|------|
| M4 ResearchWorkflow | 固定 6 节点 ML 研究 DAG | 保留 |
| M8 MCP/A2A | 工具描述、权限策略、AgentCard | 保留 |
| M13 Scheduler | 多实验任务调度、消息、审计 | 新增 |

M13 是批处理研究调度，不是对话路由器，也不是外部 MCP 服务。

## 当前下一步

**M13 已收口**（EXP-M13-001→004 · 361 pytest 双端 @ `6913dbf`）。后续：论文撰写（`outputs/paper/`）· 可选 EXP-TEXT-002 LoRA · 可选 RL/Population 研究线。

## M13.0 Implementation Note

M13.0 implemented @ `605fa66`. **Server verified 2026-06-04**（53.99s，342 passed）.

Local + server verification:

```bash
python -m pytest tests/test_mcp_scheduler.py -v  # 11 passed
python scripts/run_mcp_pipeline.py --list-recipes
python scripts/run_mcp_pipeline.py --recipe mock_research --dry-run
python scripts/run_mcp_pipeline.py --recipe text_smoke --dry-run
python -m pytest -v  # 342 passed
```

This implementation remains mock-first and dry-run only. It does not create new OOS metrics or replace existing research workflows.

## M13.1 Implementation Note

M13.1 adds YAML pipeline recipes on top of the M13.0 scheduler.

Delivered:

- `src/quant_mas/orchestration/pipeline_recipe.py`
- `configs/pipelines/ml_baseline.yaml.example`
- `configs/pipelines/text_enhanced.yaml.example`
- `configs/pipelines/population_oos.yaml.example`
- `configs/pipelines/rl_ablation.yaml.example`
- `tests/test_mcp_pipeline_recipes.py`

Recipe behavior:

- Built-in recipe names from M13.0 still work.
- `scripts/run_mcp_pipeline.py --recipe <path-to-yaml> --dry-run` loads a YAML recipe.
- YAML recipes keep `script` metadata for auditability but still execute only dry-run stubs in this stage.
- Text recipes require `audit_text_signals` before `walk_forward_eval`.
- RL recipes keep `rl_train` under `simulation` / `training`; OOS is only allowed at candidate validation.

M13.1 implemented @ `2610612`. **Server verified 2026-06-04**（54.00s，349 passed；4 yaml.example dry-run ✅）.

Verification:

```bash
python -m pytest tests/test_mcp_pipeline_recipes.py -v  # 7 passed
python -m pytest tests/test_mcp_scheduler.py -v         # 11 passed
python -m pytest -v                                     # 349 passed
python scripts/run_mcp_pipeline.py --recipe configs/pipelines/ml_baseline.yaml.example --dry-run
python scripts/run_mcp_pipeline.py --recipe configs/pipelines/text_enhanced.yaml.example --dry-run
python scripts/run_mcp_pipeline.py --recipe configs/pipelines/population_oos.yaml.example --dry-run
python scripts/run_mcp_pipeline.py --recipe configs/pipelines/rl_ablation.yaml.example --dry-run
```

M13.1 still does not run real server commands. Real execution remains a later explicit server experiment.

## M13.2 Implementation Note

M13.2 adds an optional LangGraph backend for YAML recipes.

Delivered:

- `src/quant_mas/orchestration/langgraph_recipe_workflow.py`
- `scripts/run_mcp_pipeline.py --backend scheduler|langgraph`
- `tests/test_langgraph_recipe_workflow.py`

Behavior:

- `--backend scheduler` remains the default.
- `--backend langgraph` builds a LangGraph DAG when `langgraph` is installed.
- If `langgraph` is unavailable, the backend falls back to the deterministic scheduler dry-run.
- M4 `ResearchWorkflow` remains unchanged.
- M13.2 still writes audit JSONL via the M13 scheduler and does not execute real server jobs.

M13.2 implemented @ `7f48486`. **Server verified 2026-06-04**（61.37s，354 passed；langgraph + scheduler dry-run ✅）.

Verification:

```bash
python -m pytest tests/test_langgraph_recipe_workflow.py -v  # 5 passed
python -m pytest -v                                          # 354 passed
python scripts/run_mcp_pipeline.py \
  --backend langgraph \
  --recipe configs/pipelines/text_enhanced.yaml.example \
  --dry-run
python scripts/run_mcp_pipeline.py \
  --backend langgraph \
  --recipe configs/pipelines/rl_ablation.yaml.example \
  --dry-run
```

## M13.3 Implementation Note

M13.3 exports paper-grade tables and an audit summary from existing experiment records.

Delivered:

- `src/quant_mas/research/paper_artifacts.py`
- `scripts/export_paper_artifacts.py`
- `tests/test_paper_artifacts.py`

Outputs:

- `paper_main_results.csv`
- `paper_text_ablation.csv`
- `paper_population_ablation.csv`
- `paper_rl_ablation.csv`
- `paper_experiment_index.md`
- `audit_summary.json`

Boundaries:

- Main-result exports include only experiments with `oos.*`.
- Simulation-only RL runs are excluded from the main result table.
- Text ablation rows keep coverage, aligned count, and dropped count columns.
- RL ablation rows keep OOS and simulation metrics in separate columns.
- Missing values are left blank; the exporter does not infer or invent results.

M13.3 implemented @ `931356f`. **Server verified 2026-06-04**（61.08s，361 passed；真实 `experiments.json` 导出 6 产物 ✅）。

Verification:

```bash
python -m pytest tests/test_paper_artifacts.py -v  # 7 passed
python -m pytest -v                                 # 361 passed
python scripts/export_paper_artifacts.py \
  --memory-path outputs/reports/experiments.json \
  --audit-dir outputs/pipelines \
  --output-dir outputs/paper
```

M13.3 does not create new OOS metrics. It only organizes existing ExperimentMemory records and optional M13 audit JSONL into paper-grade tables.
