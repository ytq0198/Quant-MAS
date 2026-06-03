# MCP / A2A 协议层计划（Plus M8）

更新时间：2026-06-01（Codex 任务待实现）

> Codex 任务：[codex_prompt_M8.md](codex_prompt_M8.md) · 设计：[项目plus设计.md §M8](../项目plus设计.md#m8mcp--a2a-协议化扩展)

## 定位

M8 **不是**接入真实 MCP Server，也**不是**实盘 broker 或 shell 网关。

```
现有 BaseTool + ToolRegistry（7 Quant Tools）
    → MCPToolSpec（标准化描述）
    → ToolPolicy（allow / deny / require_confirmation）
    → execute_mcp_tool_call（经 policy 调用 registry）
    → AgentCard JSON（Supervisor / Research / Report 能力描述）
```

**论文主指标**不变：walk-forward **oos.sharpe 0.586**（EXP-20260602-008）。  
M8 不参与回测 metrics，不替代 RiskTool。

## 第一版交付（Codex）

| 组件 | 路径 | 说明 |
|------|------|------|
| MCP types | `protocols/mcp/types.py` | MCPToolSpec / MCPToolCall / MCPToolResult |
| Policy | `protocols/mcp/policy.py` | deny shell/broker/order/secrets |
| Adapter | `protocols/mcp/adapter.py` | tool_to_mcp_spec、execute_mcp_tool_call |
| A2A | `protocols/a2a/agent_card.py` | AgentCard + build_*_card |
| CLI | `scripts/export_agent_cards.py` | 导出 JSON |
| 配置 | `configs/protocols.yaml` | deny 规则、output 路径 |
| 测试 | `tests/test_protocols.py` | ≥12 项，全 mock |

## 安全边界（必须）

| 规则 | 行为 |
|------|------|
| 不接外部 MCP server | 无 network listener / 无远程 MCP SDK 调用 |
| deny 危险 tool 名 | shell、broker、place_order 等 |
| deny 危险 kwargs | api_key、secret、password、token |
| 不新增 live order API | 现有 Quant Tools 行为不变 |
| 输出不含 secrets | Agent Card / mcp_tools.json 无 `.env` 内容 |

## 与现有 Agent 的关系

| Agent | M8 产出 |
|-------|---------|
| SupervisorAgent | AgentCard：7 工具路由能力 |
| ResearchAgent | AgentCard：研究/解释，不修改 metrics |
| ReportAgent | AgentCard：报告叙事，默认 Mock LLM |

Supervisor **不被替换**；M8 为可选标准化层。

## 验收流程（Codex 完成后）

### 本地

```bash
python -m pytest tests/test_protocols.py -v
python -m pytest -v
python scripts/export_agent_cards.py --help
python scripts/export_agent_cards.py --config configs/protocols.yaml --output-dir outputs/protocols
```

### 服务器（可选）

```bash
cd /mnt/localDisk3/weizian/Quant-MAS
git pull origin main
python -m pytest -v
python scripts/export_agent_cards.py --config configs/protocols.yaml \
  --output-dir /mnt/localDisk3/weizian/reports/protocols
```

## 待验证实验

| 编号 | 内容 |
|------|------|
| EXP-20260602-023 | M8 本地 pytest + export_agent_cards |
| EXP-20260602-024 | M8 服务器 pytest |

## 相关文档

- [experiment_log.md](experiment_log.md)
- [architecture.md](architecture.md)（M8 完成后更新）
- [server_commands.md](server_commands.md)（§6.11 待补充）
