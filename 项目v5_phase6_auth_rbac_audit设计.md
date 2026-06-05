# Quant MAS v5 Phase 6 Auth / RBAC / Audit Hardening Design

> 目标：在 Phase 5 已支持服务器后端读取真实 artifacts 的基础上，设计轻量、可落地的认证、权限和审计强化方案。Phase 6 不引入复杂 OAuth，不拆微服务，不强制数据库；先让服务器部署具备基本访问控制和可审计边界。

---

## 1. Phase 6 定位

Phase 6 的目标不是做完整企业 IAM 系统，而是让 Quant MAS 在服务器上更安全地运行：

- 限制敏感 API 访问。
- 区分只读查看、研究操作、审核操作、管理员操作。
- 记录 API 访问和 Agent/Tool 调用审计事件。
- 保持本机开发和 pytest 简单可跑。
- 不暴露 broker、order、shell、secrets、live trading 相关路径。

推荐策略：

```text
Phase 6.1: API key authentication
Phase 6.2: Role-based permission checks
Phase 6.3: Append-only audit writer
Phase 6.4: Audit API filtering
Phase 6.5: Optional JWT login later
```

---

## 2. 为什么先 API Key，不先 OAuth/JWT？

当前项目主要使用场景：

| Scenario | English | 中文 |
|---|---|---|
| Local development | Single developer, fast iteration. | 单人开发，快速迭代。 |
| Server research mode | Backend runs on server, frontend accesses remote API. | 后端跑服务器，前端访问远端 API。 |
| Demo / internship showcase | Limited trusted reviewers. | 少量可信访问者查看。 |
| Research workflow | Long-running jobs and artifacts. | 长任务和实验产物。 |

因此第一阶段使用 API key 更合适：

- 实现成本低。
- 适合服务器部署。
- 适合本机前端通过环境变量访问服务器 API。
- 不需要引入用户注册、密码存储、OAuth 回调。
- 后续仍可平滑升级到 JWT / OAuth2。

---

## 3. 用户角色设计

Phase 6 建议先定义 4 个角色。

| Role | Permissions | 中文 |
|---|---|---|
| `viewer` | Read status, experiments, OOS, backtests, paper artifacts. | 查看状态、实验、OOS、回测、论文产物。 |
| `researcher` | Viewer + run mock-safe agents/tools, trigger artifact export later. | viewer 权限 + 运行受控 Agent/Tool，后续可触发产物导出。 |
| `reviewer` | Viewer + review risk/human confirmation items later. | viewer 权限 + 后续审核风险和人工确认项。 |
| `admin` | All research/admin endpoints, user/API-key management later. | 所有研究和管理接口，后续管理用户/API key。 |

初期可不做数据库用户表，使用环境变量配置 API keys：

```text
QUANT_MAS_API_KEYS=viewer_key:viewer,researcher_key:researcher,reviewer_key:reviewer,admin_key:admin
```

生产服务器建议使用更长随机 key，不要使用上述示例。

---

## 4. API 权限分级

### Public / 可公开或低风险

这些接口可以允许无 key 或 viewer key。是否完全公开由服务器环境变量控制。

```text
GET /api/status
GET /api/deployment/status
GET /api/database/status
```

建议：

- 本地开发：可公开。
- 服务器：建议至少 viewer key。

### Viewer / 查看权限

```text
GET /api/experiments
GET /api/experiments/{id}
GET /api/backtests/{id}
GET /api/oos/{id}
GET /api/risk/{id}
GET /api/artifacts/paper
GET /api/audit/logs
GET /api/memory/search
```

### Researcher / 研究操作权限

```text
POST /api/agents/run
POST /api/tools/run        # future
POST /api/artifacts/export # future
POST /api/rag/index        # future
```

### Reviewer / 审核权限

```text
GET  /api/review/queue      # future
POST /api/review/{id}/approve
POST /api/review/{id}/reject
```

### Admin / 管理权限

```text
GET /api/admin/*
POST /api/admin/*
```

---

## 5. 后端实现建议

建议新增：

```text
src/backend/security/
|-- __init__.py
|-- roles.py
|-- api_keys.py
|-- dependencies.py
`-- audit.py
```

### roles.py

负责：

- 定义角色枚举。
- 定义权限等级。
- 判断 `role >= required_role`。

建议角色等级：

```text
viewer = 10
researcher = 20
reviewer = 30
admin = 40
```

注意：`reviewer` 不一定包含 researcher 的执行权限。为了简单，Phase 6 可以先使用等级制；后续可改为权限集合制。

### api_keys.py

负责：

- 从 `QUANT_MAS_API_KEYS` 读取 key-role 映射。
- 支持无配置时进入 local open mode。
- 不记录明文 key 到日志。
- 可返回 key fingerprint。

API key header：

```text
X-Quant-MAS-Key: <api-key>
```

### dependencies.py

负责 FastAPI dependency：

```python
require_role("viewer")
require_role("researcher")
require_role("reviewer")
require_role("admin")
```

### audit.py

负责 append-only audit writer：

```text
logs/backend_audit.jsonl
```

事件字段：

```json
{
  "timestamp": "...",
  "event_type": "api.request",
  "path": "/api/agents/run",
  "method": "POST",
  "role": "researcher",
  "key_fingerprint": "sha256:abcd...",
  "status": "accepted",
  "request_id": "...",
  "safety": {
    "live_trading_enabled": false
  }
}
```

---

## 6. 安全默认值

Phase 6 默认值建议：

| Setting | Local default | Server recommendation |
|---|---|---|
| `QUANT_MAS_AUTH_MODE` | `open` | `api_key` |
| `QUANT_MAS_API_KEYS` | empty | required |
| `QUANT_MAS_AUDIT_WRITE_PATH` | `logs/backend_audit.jsonl` | server logs path |
| `QUANT_MAS_PUBLIC_STATUS` | `true` | `false` |

本机开发保持简单，服务器部署必须显式设置 key。

---

## 7. 审计强化设计

Phase 6 应记录三类事件：

### API access event

记录：

- method
- path
- role
- status code
- request id
- key fingerprint

### Agent / Tool event

记录：

- agent name
- task summary
- allowed tools
- denied operations
- safety notes

### Artifact / Experiment access event

记录：

- artifact path
- experiment id
- source mode: `server_artifact`, `fallback_baseline`, `fallback_empty`

---

## 8. 前端设计

Phase 6 前端不需要复杂登录页，先做轻量 API key 设置。

建议新增：

```text
Settings / API Access panel
```

功能：

- 输入 API key。
- 存入 browser localStorage。
- 所有 fetch 请求自动带 `X-Quant-MAS-Key`。
- 显示当前 role。
- 显示 auth mode：open / api_key。

安全说明：

- 这是研究项目和服务器 demo 的轻量认证，不是完整生产 IAM。
- 如果要公开给多人长期使用，再升级 JWT / OAuth2。

---

## 9. 测试策略

本机目标测试只验证：

1. 无 API key 配置时，本地 open mode 可用。
2. 配置 API key 后，缺 key 访问受限接口返回 401。
3. viewer key 不能调用 researcher 接口。
4. researcher key 可以调用 `/api/agents/run`。
5. audit writer 会追加 JSONL 事件。
6. 不记录明文 API key。

服务器 / Cursor 测试验证：

1. 设置真实 `QUANT_MAS_API_KEYS` 后后端可启动。
2. 前端 localStorage key 能访问服务器 API。
3. audit JSONL 正常写入服务器日志目录。
4. Nginx/Caddy 不暴露 `.env`、logs、outputs 私有目录。

---

## 10. 实施顺序

### Step 1: security modules

新增 `src/backend/security/`。

验收：

- API key 解析测试通过。
- role check 测试通过。

### Step 2: protect selected routes

优先保护：

```text
POST /api/agents/run
GET /api/audit/logs
```

验收：

- open mode 不影响本机开发。
- api_key mode 下权限生效。

### Step 3: audit middleware

新增轻量 middleware 或 dependency，记录 API access。

验收：

- JSONL audit event 写入。
- 不写入明文 key。

### Step 4: frontend API key panel

新增本地 API key 设置。

验收：

- 前端请求带 header。
- 无 key 时显示权限提示。

### Step 5: docs and server env

更新：

- `.env.example`
- `docs/fullstack_quickstart.md`
- `src/backend/README.md`
- `项目v5企业级设计.md`

---

## 11. 不做事项

Phase 6 暂不做：

- OAuth provider integration.
- Password registration system.
- Multi-tenant project billing.
- Kubernetes secrets.
- Complex permission matrix.
- Real broker/order permissions.

这些属于未来成熟平台阶段，不适合现在立刻加入。

---

## 12. 最小验收标准

Phase 6 完成时应满足：

- 本地 open mode 可继续运行。
- 服务器 api_key mode 可限制访问。
- `viewer` / `researcher` / `reviewer` / `admin` 角色定义清楚。
- `POST /api/agents/run` 至少需要 researcher。
- `GET /api/audit/logs` 至少需要 reviewer 或 admin。
- API access audit JSONL 可写入。
- 不记录明文 API key。
- 文档说明本机与服务器模式差异。
- 不引入投资建议、实盘交易或收益承诺。

---

## 13. Implementation Status / 实施状态

已落地：

- `src/backend/security/roles.py`
- `src/backend/security/api_keys.py`
- `src/backend/security/dependencies.py`
- `src/backend/security/audit.py`
- `GET /api/auth/me`
- `POST /api/auth/validate-key`
- `POST /api/agents/run` 需要 `researcher+`
- `GET /api/audit/logs` 需要 `reviewer+`
- 前端 API Access 面板
- 前端 `X-Quant-MAS-Key` 请求头

本地目标测试已覆盖：

- open mode 默认可用。
- api_key mode 缺 key 返回 401。
- viewer 不能调用 researcher 接口。
- researcher 可以调用 `/api/agents/run`。
- reviewer 可以调用 `/api/audit/logs`。
- API key 指纹不包含明文 key。
