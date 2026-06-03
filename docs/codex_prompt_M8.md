# Plus M8：MCP / A2A 协议化扩展 — Codex 提示词

**状态：✅ 已完成（本地 EXP-20260602-023，195 passed，2026-06-01）**

更新时间：2026-06-01（M8 第一版 skeleton 本地验收）

> **用法**：先粘贴下方「固定前缀」，再粘贴「M8 主任务」整段交给 Codex。  
> **设计依据**：[项目plus设计.md §M8](../项目plus设计.md#m8mcp--a2a-协议化扩展) · 配套：[protocols.md](protocols.md) · 前置：**M1–M7 ✅**

---

## 固定前缀（每次必贴）

```
你正在开发 Quant MAS 科研项目。
路径：D:\scientific reasearch and work\SRTP\Quant MAS

测试基线：本地 + 服务器 **180 passed**（Plus M7，EXP-20260602-021/022）。
OOS 主 baseline：EXP-20260602-008，oos.sharpe **0.586**（walk-forward，19 窗）。
M7 RL：simulation only；metrics 为 `simulation.*`，不得与 `oos.*` 混比。

硬性原则：
1. M8 是 **内部 adapter + 权限策略 + Agent Card 导出** — **不**连接真实外部 MCP server，**不**启动 network listener。
2. **不**新增 broker / live order / shell / 任意写文件工具；policy 必须 **deny** 此类 tool name 与危险 kwargs。
3. **不替换** SupervisorAgent、ResearchAgent、ToolRegistry 默认行为；M8 为**可选**标准化层，现有 `run_agent.py` 无 M8 时行为不变。
4. pytest **不联网**；不调用真实 MCP SDK 远程 endpoint；全部 mock ToolRegistry + synthetic tool calls。
5. 请只实现当前 **M8** 一个模块；改完后 `python -m pytest -v` 全量通过（预期 180+，新增 test_protocols.py）。
6. 禁止 commit `.env`、API key、或含 secrets 的 Agent Card 样例。
7. Agent Card / MCP spec 仅描述**已有** Quant Tools 能力，不得虚构 RL 实盘或 broker 接口。
8. 论文主指标仍为 walk-forward OOS；M8 不参与 metrics 计算。
```

---

## M8 主任务（复制给 Codex）

```
请为 Quant MAS v2 增加 MCP-style 工具适配与 A2A Agent Card 雏形（Plus M8，内部安全封装 only）。

## 背景

v1 / Plus 已有：
- tools/base.py — BaseTool、ToolResult
- tools/registry.py — ToolRegistry（7 个 Quant Tools）
- tools/quant.py — data_summary, backtest, train_model, report, ml_backtest, pipeline
- tools/quant/risk_tool.py — risk_check
- agents/supervisor_agent.py — 规则路由，**不**调用真实 LLM 下单
- agents/research_agent.py、report_agent.py — M5 研究/报告（Mock 默认）
- orchestration/registry.py — create_default_tool_registry（workflow 5 工具子集）
- M7 rl/ — simulation only，**不**经 MCP 暴露 broker

M8 目标：
1. **MCP 类型** — 将 BaseTool 描述为 MCPToolSpec；ToolCall → ToolResult 标准化。
2. **Policy** — allow / deny / require_confirmation；默认 deny 危险能力。
3. **Adapter** — tool_to_mcp_spec、经 policy 的 execute_mcp_tool_call。
4. **A2A AgentCard** — Supervisor / Research / Report 能力描述 JSON（静态元数据，非 live agent 网络）。
5. **CLI** — export_agent_cards.py 导出 JSON；--help 可用。

第一版重点：**mock pytest 全绿** + CLI help；**不接**外部 MCP server。

## 需要实现的文件

### 1. 包结构

src/quant_mas/protocols/
  __init__.py
  mcp/
    __init__.py
    types.py          # MCPToolSpec, MCPToolCall, MCPToolResult, MCPParameterSpec
    policy.py         # PolicyDecision, ToolPolicy, evaluate_tool_call
    adapter.py        # tool_to_mcp_spec, registry_to_mcp_specs, execute_mcp_tool_call
  a2a/
    __init__.py
    agent_card.py     # AgentCard, build_supervisor_card, build_research_card, build_report_card

configs/protocols.yaml

scripts/export_agent_cards.py

tests/test_protocols.py   # ≥12 项，全 mock

docs/protocols.md         # 若不存在则创建；M8 定位与安全边界

### 2. mcp/types.py

```python
@dataclass(frozen=True)
class MCPParameterSpec:
    name: str
    type: str              # string | number | boolean | object
    required: bool = False
    description: str = ""

@dataclass(frozen=True)
class MCPToolSpec:
    name: str
    description: str
    parameters: tuple[MCPParameterSpec, ...] = ()
    safety_tags: tuple[str, ...] = ()   # e.g. ("quant", "read_only", "no_live_order")

@dataclass(frozen=True)
class MCPToolCall:
    tool_name: str
    arguments: dict[str, Any]

@dataclass(frozen=True)
class MCPToolResult:
    status: str            # ok | denied | error
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)
```

提供 `to_dict` / `from_dict`（或等价 JSON 序列化 helper）。

### 3. mcp/policy.py

```python
class PolicyDecision(str, Enum):
    ALLOW = "allow"
    DENY = "deny"
    REQUIRE_CONFIRMATION = "require_confirmation"

@dataclass(frozen=True)
class PolicyEvaluation:
    decision: PolicyDecision
    reason: str = ""

class ToolPolicy:
    def evaluate(self, call: MCPToolCall) -> PolicyEvaluation: ...
```

**默认 deny 规则**（必须实现，可配置扩展）：

| 类别 | 规则 |
|------|------|
| tool_name | 含 `shell`, `exec`, `broker`, `order`, `place_order`, `live_trade` → **DENY** |
| arguments | key 匹配 `api_key`, `secret`, `password`, `token`（case-insensitive）→ **DENY** |
| arguments | `targets_path` / 写路径指向 `.env` 或明显 secrets → **DENY** |
| 白名单 | 已知 Quant 工具名：`data_summary`, `backtest`, `train_model`, `report`, `ml_backtest`, `pipeline`, `risk_check` → **ALLOW**（仍走 kwargs 检查） |
| 可选 | `pipeline` → **REQUIRE_CONFIRMATION**（第一版可 ALLOW，须在 tests 覆盖一种 confirmation 路径） |

提供 `default_tool_policy()` 与 `ToolPolicy.from_yaml(configs/protocols.yaml)`。

### 4. mcp/adapter.py

```python
def tool_to_mcp_spec(tool: BaseTool, *, parameter_specs: Sequence[MCPParameterSpec] | None = None) -> MCPToolSpec:
    """从 BaseTool 生成 MCP spec；parameters 可从静态映射表补充（第一版允许空 parameters）。"""

def registry_to_mcp_specs(registry: ToolRegistry) -> list[MCPToolSpec]:
    """导出 registry 内全部工具 spec。"""

def execute_mcp_tool_call(
    registry: ToolRegistry,
    call: MCPToolCall,
    *,
    policy: ToolPolicy | None = None,
    confirmed: bool = False,
) -> MCPToolResult:
    """
    1) policy.evaluate(call)
    2) DENY → status=denied, 不调用 tool
    3) REQUIRE_CONFIRMATION 且 confirmed=False → status=denied, reason 说明需确认
    4) ALLOW → registry.get(...).run(**arguments) → MCPToolResult(status=ok, ...)
    5) 异常 → status=error
    """
```

**不得**绕过 ToolRegistry 直接 import 脚本 subprocess。

可选：为 7 个 Quant Tool 提供 `TOOL_PARAMETER_SPECS: dict[str, list[MCPParameterSpec]]` 静态表（如 `data_path`, `targets_path`, `config_path`）。

### 5. a2a/agent_card.py

```python
@dataclass(frozen=True)
class AgentCard:
    name: str
    description: str
    version: str
    capabilities: tuple[str, ...]
    tools: tuple[str, ...]              # tool names only
    safety_constraints: tuple[str, ...]  # e.g. "no_live_orders", "metrics_not_overwritten_by_llm"
    metadata: dict[str, Any] = field(default_factory=dict)

def build_supervisor_card() -> AgentCard: ...
def build_research_card() -> AgentCard: ...
def build_report_card() -> AgentCard: ...
def agent_card_to_dict(card: AgentCard) -> dict[str, Any]: ...
```

Agent Card **描述**现有 agent，不启动 A2A 网络服务。

### 6. configs/protocols.yaml

```yaml
protocols:
  mcp:
    enabled: true
    deny_tool_patterns:
      - shell
      - broker
      - place_order
    deny_argument_patterns:
      - api_key
      - secret
      - password
    require_confirmation_tools:
      - pipeline
  a2a:
    version: "0.1.0"
    cards:
      - supervisor
      - research
      - report
paths:
  output_dir: outputs/protocols
```

### 7. scripts/export_agent_cards.py

CLI：
- `--config configs/protocols.yaml`
- `--output-dir outputs/protocols`
- `--include-mcp-specs`（可选：同时写 `mcp_tools.json`）
- `--registry default|supervisor`（default = 7 tools via run_agent 同款 registry 工厂；可 import helper）
- `--help`

行为：
- 写 `supervisor_agent_card.json`、`research_agent_card.json`、`report_agent_card.json`
- 可选写 `mcp_tools.json`（MCPToolSpec 列表）
- 输出 summary 到 stdout（paths only，不含 secrets）
- **不**连接外部 MCP server

第一版可在脚本内 `from quant_mas.tools import ToolRegistry, ...` 构建与 `run_agent.py` 一致的 7 工具 registry（提取 shared helper 到 `protocols/` 或 `tools/` 若需避免 duplication，但**最小 diff**优先：允许 export 脚本内联构建）。

### 8. tests/test_protocols.py（≥12 项）

全部 mock / 无网络：

1. MCPToolSpec / MCPToolCall / MCPToolResult 序列化 round-trip
2. tool_to_mcp_spec 保留 name + description
3. registry_to_mcp_specs 数量 = registry 工具数
4. policy denies `shell` / `broker` tool_name
5. policy denies arguments 含 `api_key`
6. policy allows `data_summary` with benign kwargs
7. REQUIRE_CONFIRMATION 未 confirmed → denied
8. REQUIRE_CONFIRMATION + confirmed=True → executes（mock tool）
9. execute_mcp_tool_call ALLOW 调用 Mock BaseTool 返回 ok
10. execute_mcp_tool_call DENY 不调用 tool.run（用 spy/mock 断言）
11. build_supervisor_card tools 含 7 个 quant 工具名（或文档说明的子集）
12. agent_card_to_dict JSON-serializable
13. export_agent_cards.py --help（subprocess）
14. export_agent_cards 写文件到 tmp_path（subprocess 或 import main）
15. test_supervisor_agent / test_walk_forward / test_trading_env **保持通过**

Mock 工具示例：

```python
class EchoTool(BaseTool):
    def __init__(self):
        super().__init__(name="echo", description="echo for tests")
    def run(self, **kwargs):
        return ToolResult(content="ok", metadata=kwargs)
```

### 9. docs/protocols.md

简要说明：
- M8 **不是**生产 MCP server
- MCP = 工具描述 + policy 网关
- A2A = Agent 能力卡片 JSON
- 安全 deny 列表
- 验收命令

## 兼容性要求

- **不得修改** SupervisorAgent.route 默认逻辑
- **不得修改** ResearchAgent 默认 `use_llm=False` 行为
- **不得**让 M8 adapter 成为唯一 tool 入口（第一版仅新 CLI + 库函数）
- RiskTool / walk-forward / M7 RL **不受影响**
- 可选：在 `protocols/__init__.py` export 主要类型，**不**强制全项目 import

## 禁止

- 连接真实外部 MCP server / SSE / stdio MCP transport（第一版）
- 新增 `ShellTool`, `BrokerTool`, `PlaceOrderTool`
- pytest 中 HTTP 调用 MCP endpoint
- Agent Card 写入真实 API key 或 `.env` 内容
- 用 MCP 层绕过 RiskTool 直接下单
- commit secrets 或 `outputs/protocols/*.json` 含 key 的样例到 git（`.gitignore` 已有 outputs/）

## 验收命令

python -m pytest tests/test_protocols.py -v
python -m pytest -v                                    # 全量 180+ passed
python scripts/export_agent_cards.py --help
python scripts/export_agent_cards.py --config configs/protocols.yaml --output-dir outputs/protocols
```

---

## Cursor 后续（Codex 完成后）

1. ~~确认 `docs/protocols.md` 与实现对齐~~ ✅
2. ~~更新 `docs/architecture.md` — Protocol Layer~~ ✅
3. ~~更新 `docs/experiment_log.md` — EXP-20260602-023~~ ✅
4. ~~更新 `docs/progress.md` / `项目进度.md` — M8 状态~~ ✅
5. 服务器 pull + pytest **195 passed** + export_agent_cards（EXP-20260602-024 待做）
6. ~~`docs/server_commands.md` §6.11 M8~~ ✅

**Plus v2 主线 M1–M8 代码骨架已全部落地**；后续为科研复跑（EXP-TEXT-WF-002）或仓库对外（Release/Topics）。

---

## 参考现有代码

| 模块 | 路径 |
|------|------|
| BaseTool / ToolResult | `src/quant_mas/tools/base.py` |
| ToolRegistry | `src/quant_mas/tools/registry.py` |
| 7 Quant Tools | `src/quant_mas/tools/quant.py`, `quant/risk_tool.py` |
| run_agent registry | `scripts/run_agent.py` |
| SupervisorAgent | `src/quant_mas/agents/supervisor_agent.py` |
| ResearchAgent | `src/quant_mas/agents/research_agent.py` |
| ReportAgent | `src/quant_mas/agents/report_agent.py` |
| RiskTool | `src/quant_mas/tools/quant/risk_tool.py` |
| M7（不暴露 broker） | `src/quant_mas/rl/trading_env.py` |

---

## 与 M7 / 外部 MCP 的关系

| 模块 | 用途 |
|------|------|
| **M7** RL | simulation only；**不**经 MCP 对外暴露 |
| **M8** MCP adapter | 内部 Tool spec + policy gateway |
| **M8** A2A AgentCard | 静态能力描述，非 live A2A 网络 |
| **未来** | 真实 MCP server 需单独 security review，不在 M8 第一版 |

---

## 实验编号（验收后写入 experiment_log）

| 编号 | 内容 |
|------|------|
| **EXP-20260602-023** | M8 protocols 本地 pytest + export_agent_cards |
| **EXP-20260602-024** | M8 服务器 pytest（待做） |

论文主指标仍为 **EXP-20260602-008**（oos.sharpe **0.586**）。
