# Plus v3 M13：企业化编排与协议扩展 — Codex 提示词

**状态：✅ M13.0 + M13.1 + M13.2 已完成（354 pytest）· 服务器 M13.2 smoke 或 M13.3 待做**

更新时间：2026-06-04

> **用法**：先粘贴下方「固定前缀」，再粘贴「M13 主任务」整段交给 Codex。  
> **设计依据**：[项目v3设计.md §M13](../项目v3设计.md#m13企业化编排与协议扩展) · 前置：**M4 ✅**（6 节点 ResearchWorkflow）· **M8 ✅**（MCP adapter + ToolPolicy）· **M9–M12.4 ✅** · **M6 text 三线消融 ✅**

---

## 固定前缀（每次必贴）

```
你正在开发 Quant MAS 科研项目（v3 阶段）。
路径：D:\scientific reasearch and work\SRTP\Quant MAS
GitHub：https://github.com/ytq0198/Quant-MAS

测试基线：本地+服务器 **331 passed**（EXP-TEXT-WF-003 docs @ `e7f89b4`）。
OOS 主 baseline：EXP-20260602-008，oos.sharpe **0.586**（ML walk-forward，19 窗）。

已完成的 v3 模块（M13 不得破坏）：
- M4：orchestration/ 6 节点 ResearchWorkflow（data_check → feature_build → train_model → ml_backtest → risk_check → report）；sequential + 可选 LangGraph；`run_langgraph_workflow.py`
- M8：protocols/mcp/ — ToolPolicy deny shell/broker/order/secrets；**不接外部 MCP network listener**
- M9：Postgres/pgvector/Neo4j mock（EXP-026）
- M10：local_vllm mock + ResearchAgent（EXP-LLM-002）
- M11–M11.8：Population → StrategyCandidate → walk-forward OOS batch（266 pytest；best candidate **1.039**，ablation）
- M12.1–M12.4：RL training（simulation.*）→ export → OOS（EXP-POP-009 **0.0** / EXP-POP-010 **0.387** ablation）
- M6 text：EXP-TEXT-WF-001 **0.563** · WF-002 **0.579** · WF-003 **0.565**（exploratory；Finnhub fetch 2025-06-04~2026-06-04）

现实痛点（M13 要解决的）：
服务器上重复研究流程目前靠 `docs/server_commands.md` 手工串联 30+ CLI（fetch/align/finbert/audit/features/walk-forward/compare、population export/batch OOS、RL train/export/validate 等），易漏步、难审计、路径硬编码。M13 第一版应把这些流程 **声明式 recipe + dry-run scheduler** 化，而不是重写 Quant Engine。

硬性原则：
1. **并存，不替换** — M13 扩展 orchestration/；**不得**删除或替换 `run_agent.py` / SupervisorAgent 默认路径；**不得**删除 M4 现有 6 节点 DAG 与 `test_langgraph_workflow.py` 行为。
2. **dry-run 默认** — pytest 与 CLI 默认 `--dry-run`：只解析 recipe、模拟节点顺序、写 audit JSONL，**不**联网、**不**调 LLM、**不**跑 GPU 长训练、**不** subprocess 真实服务器路径。
3. **指标族隔离** — scheduler **禁止**在 mock/训练节点直接写 `oos.sharpe`；仅当 recipe 显式挂载既有 **walk_forward** / **validate_candidate_oos** / **batch_validate_candidates** / **compare_experiments** 节点时，才允许下游脚本按现有逻辑写 `oos.*`（M13 本身不复制 walk-forward 数学）。
4. **ToolPolicy 保持** — 调度器若经 MCP adapter 触发工具，须复用 `protocols/mcp/policy.py` deny 规则；**禁止**新增 shell/broker/order 工具。
5. **不接外部 MCP listener** — 仅内部消息 + audit log；不启动 network server。
6. pytest **331+ 全绿**；增量测试在 `tests/test_mcp_scheduler.py`（建议 ≥12 项）。
7. 路径用 `pathlib.Path` + YAML config；**禁止** commit `.env`、API key、大数据 parquet。
8. 一次只实现 **M13**；完成后 `python -m pytest -v` 全量通过。
9. 论文主指标仍为 walk-forward OOS **0.586**；编排层改善的是 **可复现性与审计**，不是新 alpha。
10. 服务器路径（如 `/mnt/localDisk3/weizian/...`）只出现在 **example yaml**，不进 pytest 硬编码。
```

---

## M13 主任务（复制给 Codex）

```
请为 Quant MAS v3 实现 **M13：企业化编排与协议扩展**（mock-first，与 Quant Engine 解耦）。

## 背景

### 已有 orchestration（M4，必须保留）

src/quant_mas/orchestration/
  langgraph_state.py      # QuantWorkflowState
  sequential_workflow.py  # NODE_ORDER 6 步
  nodes.py                # data_check / feature_build / train_model / ml_backtest / risk_check / report
  langgraph_workflow.py   # 可选 LangGraph（需 [orchestration] extra）
  registry.py             # create_default_tool_registry
  workflow_events.py

scripts/run_langgraph_workflow.py
tests/test_langgraph_workflow.py  # 12 passed（含 orchestration）

M4 是 **单条 ML 研究流水线**（6 固定节点），dry-run 友好，但 **不包含**：
- 文本增强链路（fetch → align → FinBERT → audit → text features）
- walk-forward OOS + compare_experiments 收尾
- Population Top-K export + batch candidate OOS
- RL train → export → candidate OOS

### 已有 CLI（M13 应编排，而非重写）

| 流程族 | 现有脚本（示意） |
|--------|------------------|
| ML baseline | download_data → build_features → train_model → run_walk_forward → compare_experiments |
| Text enhanced | fetch_real_news → align_real_news → train_text_model → audit_text_signals → build_features → run_walk_forward → compare_experiments |
| Population OOS | export_population_candidates → batch_validate_candidates → compare_experiments |
| RL ablation | run_rl_experiment → export_rl_policy_candidate → validate_candidate_oos → compare_experiments |
| 协议 | export_agent_cards（M8，可选收尾节点） |

这些流程在 `docs/server_commands.md` 已有完整命令；M13 应提供 **recipe 名称 → 节点 DAG** 的声明式映射。

### 科研现状（编排不得歪曲）

| 指标 | 值 | 实验 |
|------|-----|------|
| ML walk-forward OOS | **oos.sharpe 0.586** | EXP-20260602-008（主 baseline） |
| Text WF-001/002/003 | 0.563 / 0.579 / 0.565 | exploratory |
| Population candidate OOS | ~1.036–1.039 | ablation，非 ML 主 baseline 替代 |
| RL feature-linear OOS | 0.387 | ablation（EXP-POP-010） |

## M13 目标（第一版）

把「手工 server_commands 串联」升级为 **可审计的多实验 DAG Scheduler**：

1. **Pipeline Recipe** — YAML 定义节点 ID、依赖、对应 CLI 名或 callable 引用、metric_family（`walk_forward` / `simulation` / `population` / `audit`）。
2. **ExperimentScheduler** — 拓扑排序执行节点；支持 `--dry-run`（只 plan + audit）与 `--run-node NODE`（单步，可选后续）。
3. **AgentCommunication 骨架** — 内部消息类型（如 `PlanMessage` / `NodeResultMessage` / `AuditMessage`）；mock 收发，不接外部 A2A 网络。
4. **Audit Log** — append-only JSONL：`pipeline_id`, `recipe`, `node`, `status`, `started_at`, `artifacts`, `metric_family`；可查询最近 N 条。
5. **CLI** — `scripts/run_mcp_pipeline.py`：
   - `--recipe ml_baseline | text_enhanced | population_oos | rl_ablation | custom.yaml`
   - `--dry-run`（默认 true）
   - `--output-dir outputs/pipelines/<run_id>/`
6. **文档** — `docs/mcp_protocol.md`（v3 调度语义；区别于 v2 `docs/protocols.md` 的工具白名单）。
7. **测试** — `tests/test_mcp_scheduler.py`（≥12）：recipe 解析、环检测、dry-run 顺序、audit 写入、ToolPolicy 仍 deny shell、**不破坏** M4 workflow 测试。

第一版 **不做**：
- 真实 subprocess 跑 77 窗 walk-forward（pytest 内）
- LangGraph 重写全部节点（可预留 `build_langgraph_from_recipe()` stub）
- 外部 MCP server / WebSocket / Celery 分布式
- LLM 自主决定 recipe（recipe 由人/YAML 指定）
- 新 alpha 指标或绕过 RiskAgent 的下单路径

## 建议 Recipe（第一版至少 4 个 mock recipe）

### 1. `ml_baseline`（扩展 M4）

nodes（顺序）：
1. data_check
2. feature_build
3. train_model
4. walk_forward_eval      → 映射 run_walk_forward.py（dry-run：写 stub artifact）
5. compare_experiments   → 映射 compare_experiments.py（dry-run：0 rows ok）
6. report

### 2. `text_enhanced`（覆盖 EXP-TEXT-WF-003 形态）

nodes：
1. fetch_real_news       # dry-run：记录 intended window 2025-06-04~2026-06-04
2. align_real_news
3. train_text_model      # finbert_baseline
4. audit_text_signals    # 必须在前；报告 coverage_ratio
5. feature_build         # 含 text_signal_fillna: 0
6. walk_forward_eval
7. compare_experiments

文档注释：有效新闻重叠 ~2025-06-04~2025-12-31（features 截止 2025-12-31）。

### 3. `population_oos`

nodes：
1. export_population_candidates
2. batch_validate_candidates
3. compare_experiments

metric_family：`walk_forward`（OOS 仅由 batch 节点写入）。

### 4. `rl_ablation`

nodes：
1. rl_train              → run_rl_experiment.py（simulation.* only）
2. export_rl_policy
3. validate_candidate_oos
4. compare_experiments

metric_family 分轨：步骤 1 仅 `simulation.*` / `training.*`；步骤 3 才允许 `oos.*`。

## 需要实现的文件

### 1. 包结构

src/quant_mas/orchestration/
  pipeline_recipe.py       # PipelineRecipe, PipelineNode, load_recipe_yaml
  experiment_scheduler.py  # ExperimentScheduler, SchedulerResult, topological_run
  agent_communication.py   # AgentMessage, MessageBus (in-memory)
  audit_log.py             # append_audit_event, read_audit_tail
  pipeline_nodes.py        # 扩展节点 registry：walk_forward_eval, compare_experiments 等（dry-run callable）

configs/pipelines/
  ml_baseline.yaml.example
  text_enhanced.yaml.example
  population_oos.yaml.example
  rl_ablation.yaml.example

scripts/run_mcp_pipeline.py

docs/mcp_protocol.md

tests/test_mcp_scheduler.py   # ≥12 项

### 2. PipelineRecipe schema（建议）

```yaml
pipeline_id: text_enhanced
version: 1
metric_families:
  - audit
  - walk_forward
nodes:
  - id: fetch_real_news
    script: scripts/fetch_real_news.py
    metric_family: audit
    dry_run_stub: { record_count: 0 }
  - id: align_real_news
    depends_on: [fetch_real_news]
    script: scripts/align_real_news.py
  # ...
  - id: walk_forward_eval
    depends_on: [feature_build]
    script: scripts/run_walk_forward.py
    metric_family: walk_forward
    allowed_metrics_prefix: ["oos."]
```

要求：
- `depends_on` 形成 DAG；scheduler 检测环并报错
- 每节点声明 `metric_family`；scheduler 在 audit log 中记录，便于论文写作时分轨
- `dry_run_stub` 可选；dry-run 时合并进 node output

### 3. ExperimentScheduler 行为

```python
class ExperimentScheduler:
    def plan(self, recipe: PipelineRecipe) -> list[str]: ...
    def run(self, recipe, *, dry_run: bool = True, ...) -> SchedulerResult: ...
```

- `dry_run=True`：不 import 重模块副作用；节点函数返回 stub dict + 写 audit
- `dry_run=False`（CLI 可选，pytest 不默认）：允许 subprocess 调用 `sys.executable scripts/xxx.py`，但 **第一版可不实现** real run，仅在文档说明后续 EXP-ORCH-001 服务器验证

### 4. AgentCommunication（骨架）

- `MessageBus.publish(topic, AgentMessage)` / `subscribe`
- 用途：Coordinator 发布 `pipeline_started`；各 node runner 发布 `node_finished`
- **不**引入真实 multi-process；测试用内存 bus

### 5. Audit Log

- 默认路径：`outputs/pipelines/<run_id>/audit.jsonl`
- 每条：timestamp, pipeline_id, node_id, status, duration_ms, artifacts, errors, metric_family
- 提供 `summarize_audit_log(path) -> dict` 供 report 节点或 CLI 打印

### 6. CLI

```bash
python scripts/run_mcp_pipeline.py --recipe text_enhanced --dry-run
python scripts/run_mcp_pipeline.py --recipe configs/pipelines/custom.yaml --dry-run
python scripts/run_mcp_pipeline.py --list-recipes
```

- `--list-recipes` 列出内置 4 条
- 结束打印：planned nodes、audit path、metric families touched
- **不得**默认 `--dry-run false`

### 7. 与 M4 / M8 集成

- M4 `run_sequential_workflow` 保持不变；`ml_baseline` recipe 前 3 节点可 **复用** 现有 NODE_FUNCTIONS 名称，后接扩展节点
- 若经 MCP：`execute_mcp_tool_call` + `ToolPolicy`；deny shell/broker 测试保留通过
- `export_agent_cards` 可作为 recipe 可选尾节点（mock）

### 8. 文档 mcp_protocol.md 必写章节

1. M13 定位 vs M4（单流水线 vs 多实验 recipe）
2. Recipe schema 与 4 条内置 pipeline
3. metric_family 与 `oos.*` / `simulation.*` / `population.*` 边界（引用 research_protocol）
4. audit.jsonl 字段说明
5. dry-run vs 服务器 `--no-dry-run` 后续 EXP-ORCH-001 计划
6. 安全边界：无 external listener、无 broker

### 9. 测试要求（≥12）

建议覆盖：
- load 4 个 example yaml
- topological order 正确
- cycle detection
- dry-run 全 recipe 无 exception
- audit jsonl 行数 == 节点数
- text_enhanced recipe 含 audit_text_signals 且顺序在 walk_forward 前
- rl_ablation recipe 中 rl_train 节点 metric_family != walk_forward
- ToolPolicy 仍 deny `shell` tool name
- M4 `test_langgraph_workflow.py` 仍全绿
- 全量 pytest **331+**

## 验收标准（Definition of Done）

- [ ] 4 条内置 recipe yaml + `--list-recipes`
- [ ] dry-run 调度 ≥2 条 recipe（ml_baseline + text_enhanced）audit 完整
- [ ] `docs/mcp_protocol.md` 创建
- [ ] `tests/test_mcp_scheduler.py` ≥12 passed
- [ ] `python -m pytest -v` 全量 **331+** 通过
- [ ] 不破坏 M4/M8/M11/M12 现有测试
- [ ] 无 `.env` / secrets / 大文件入库

## 服务器后续（M13 代码合并后，非 Codex 第一版范围）

EXP-ORCH-001 可选 smoke（人工跑，不写进 pytest）：

```bash
cd /mnt/localDisk3/weizian/Quant-MAS
python scripts/run_mcp_pipeline.py --recipe text_enhanced --dry-run
# 未来：--no-dry-run + storage.server.yaml 真跑（需单独 EXP 记录）
```

对照：`docs/server_commands.md` § EXP-TEXT-WF-003 手工步骤应与新 recipe 节点一一对应。

## 参考文件

- 设计：项目v3设计.md §M13
- M4：docs/langgraph_workflow.md、docs/codex_prompt_M4.md
- M8：docs/protocols.md、src/quant_mas/protocols/mcp/policy.py
- 手工流程：docs/server_commands.md（§6.9 text、§6.17 candidate OOS、§六点十 RL）
- Text 实验：docs/real_news_text_experiment.md
- 指标规范：docs/research_protocol.md
```

---

## 与已完成模块的关系

| 模块 | M13 关系 |
|------|----------|
| **M4** | 保留 6 节点；`ml_baseline` recipe **扩展**而非替换 |
| **M8** | Scheduler 触发工具时走 ToolPolicy；不写新 broker 工具 |
| **M6 text** | `text_enhanced` recipe 固化 WF-003 七步；强调 coverage audit 节点 |
| **M11.7/11.8** | `population_oos` recipe 固化 export → batch OOS → compare |
| **M12** | `rl_ablation` recipe 分轨 simulation vs OOS |
| **SupervisorAgent** | 不变；M13 服务 **批处理研究**，不是对话路由 |

---

## Cursor 后续维护（Codex 完成后）

| 文档 | 动作 |
|------|------|
| `docs/progress.md` | M13 📋→✅；pytest 基线 |
| `docs/experiment_log.md` | EXP-ORCH-001（若服务器 dry-run/real run） |
| `docs/architecture.md` | Orchestration Layer 增补 M13 |
| `项目v3设计.md` | M13 验收勾选 |
| `docs/server_commands.md` | 增 §M13 pipeline CLI |
| `README.md` | v3 next 更新 |

---

## 一句话给 Codex

> 在 **不破坏 M4 六节点 ResearchWorkflow** 的前提下，新增 **YAML recipe + ExperimentScheduler + audit JSONL + run_mcp_pipeline.py**，把 server_commands 里 ML/text/population/RL 四条手工流水线声明式编排；**dry-run 默认**；指标族分轨；pytest **331+** 全绿。
