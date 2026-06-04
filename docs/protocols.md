# MCP / A2A 协议层计划（Plus M8）

更新时间：2026-06-01（M8 ✅ EXP-20260602-023/024，195 passed 本地+服务器）

> Codex 任务：[codex_prompt_M8.md](codex_prompt_M8.md) · 设计：[项目plus设计.md §M8](../项目plus设计.md#m8mcp--a2a-协议化扩展)

## 定位

M8 **不是**生产 MCP Server，也**不是** broker / shell / 网络监听服务。

```
现有 BaseTool + ToolRegistry（7 Quant Tools）
    → MCPToolSpec（标准化描述）
    → ToolPolicy（allow / deny / require_confirmation）
    → execute_mcp_tool_call（经 policy 调用 registry）
    → AgentCard JSON（Supervisor / Research / Report）
```

**论文主指标**不变：walk-forward **oos.sharpe 0.586**（EXP-20260602-008）。

> **v3 M13** 在 M8 `ToolPolicy` 之上新增批处理调度与 audit JSONL，语义见 [mcp_protocol.md](mcp_protocol.md)（与本文 M8 工具网关互补，不替代）。

## 已交付（第一版）

| 组件 | 路径 |
|------|------|
| MCP types | `protocols/mcp/types.py` — MCPToolSpec / MCPToolCall / MCPToolResult |
| Policy | `protocols/mcp/policy.py` — deny shell/broker/order/secrets |
| Adapter | `protocols/mcp/adapter.py` — tool_to_mcp_spec、execute_mcp_tool_call |
| A2A | `protocols/a2a/agent_card.py` — AgentCard + build_*_card |
| CLI | `scripts/export_agent_cards.py` |
| 配置 | `configs/protocols.yaml` |
| 测试 | `tests/test_protocols.py` — **15 passed** |

## 安全边界

- 不连接真实外部 MCP server；不启动 network listener
- 不新增 ShellTool / BrokerTool / PlaceOrderTool
- 默认 deny：`shell` / `exec` / `broker` / `order` / `place_order` / `live_trade`
- 默认 deny kwargs：`api_key` / `secret` / `password` / `token`
- 默认 deny `.env` 或 secret-like path
- 所有执行仍通过现有 **ToolRegistry**

## 允许的工具（白名单）

`data_summary` · `backtest` · `train_model` · `report` · `ml_backtest` · `pipeline` · `risk_check`

`pipeline` 可配置为 `require_confirmation`。

## 已验证（本地 + 服务器）

```bash
python -m pytest tests/test_protocols.py -v    # 15 passed
python -m pytest -v                              # 195 passed
python scripts/export_agent_cards.py --help
python scripts/export_agent_cards.py --config configs/protocols.yaml \
  --output-dir outputs/protocols --include-mcp-specs
```

记录：**EXP-20260602-023**（本地）；**EXP-20260602-024**（服务器 ✅ **195 passed**，12.41s）。

## 后续

| 编号 | 内容 |
|------|------|
| EXP-TEXT-WF-002 | 扩大 text JSONL 覆盖后复跑 walk-forward |

## 相关文档

- [experiment_log.md](experiment_log.md)
- [architecture.md](architecture.md)（Protocol Layer）
- [server_commands.md](server_commands.md)（§6.11）
