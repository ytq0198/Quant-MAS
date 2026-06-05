# Quant MAS v5 Security Model / 安全模型

Quant MAS v5 uses lightweight API key access control for server mode and open mode for local development.

Quant MAS v5 在服务器模式下使用轻量 API Key 访问控制，在本地开发中默认使用 open mode。

## Modes / 模式

| Mode | English | 中文 |
|---|---|---|
| `open` | Local default. Requests are treated as admin for development convenience. | 本地默认模式。为方便开发，请求按 admin 处理。 |
| `api_key` | Server recommendation. Requests must send `X-Quant-MAS-Key`. | 服务器推荐模式。请求必须发送 `X-Quant-MAS-Key`。 |

Example:

示例：

```bash
export QUANT_MAS_AUTH_MODE=api_key
export QUANT_MAS_API_KEYS="viewer-secret:viewer,research-secret:researcher,reviewer-secret:reviewer,admin-secret:admin"
export QUANT_MAS_AUDIT_WRITE_PATH=/opt/quant-mas/logs/backend_audit.jsonl
```

## Roles / 角色

| Role | Level | English | 中文 |
|---|---:|---|---|
| viewer | 10 | Read status, experiments, artifacts, jobs, and optional data metadata. | 读取状态、实验、产物、任务和可选数据元数据。 |
| researcher | 20 | Run controlled research agents/tools. | 运行受控研究智能体/工具。 |
| reviewer | 30 | Read audit logs and approve/reject human review items. | 读取审计日志并批准/拒绝人工审核项。 |
| admin | 40 | Reserved for future administrative settings. | 预留给未来管理设置。 |

## Audit Rules / 审计规则

- Audit records are append-only JSONL.
- 审计记录采用 append-only JSONL。
- Raw API keys must never be written.
- 绝不写入明文 API Key。
- Key fingerprints may be written for traceability.
- 可以写入 key 指纹用于追踪。
- Review and controlled agent actions should write audit events when `QUANT_MAS_AUDIT_WRITE_PATH` is configured.
- 配置 `QUANT_MAS_AUDIT_WRITE_PATH` 后，审核动作和受控智能体动作应写入审计事件。

## Server Hardening Checklist / 服务器加固检查

- Run backend with `QUANT_MAS_AUTH_MODE=api_key`.
- 使用 `QUANT_MAS_AUTH_MODE=api_key` 运行后端。
- Keep `.env`, logs, and private outputs outside public static paths.
- 不要把 `.env`、日志和私有输出放在公网静态目录。
- Confirm `/api/config/effective` redacts secrets.
- 确认 `/api/config/effective` 会脱敏密钥。
- Confirm no route exposes broker, order, shell, or secret execution.
- 确认没有接口暴露 broker、order、shell 或 secret 执行路径。
