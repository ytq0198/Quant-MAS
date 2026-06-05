# Quant MAS v4 Database Setup / 数据库设置

This document describes the optional database layer for Quant MAS v4 Phase 4.

本文档说明 Quant MAS v4 Phase 4 的可选数据库层。

---

## Design Principle / 设计原则

The default development path uses local files, Parquet, JSONL, and fixtures. Postgres, pgvector, and Neo4j are optional deployment backends, not required for unit tests.

默认开发路径使用本地文件、Parquet、JSONL 和夹具数据。Postgres、pgvector 和 Neo4j 是可选部署后端，不是单元测试的强制依赖。

---

## Backend Options / 后端选项

| Backend | English | 中文 | Required for tests |
|---|---|---|---|
| Local files | Stores local data, reports, audit logs, and fixtures. | 存储本地数据、报告、审计日志和夹具。 | Yes |
| SQLite | Lightweight local ExperimentMemory and development metadata. | 轻量本地 ExperimentMemory 和开发元数据。 | No |
| Postgres | Server-side experiment records, task state, and metadata tables. | 服务器端实验记录、任务状态和元数据表。 | No |
| pgvector | Vector search for RAG over documents, reports, and experiment memory. | 面向文档、报告和实验记忆的 RAG 向量检索。 | No |
| Neo4j | Optional graph relationships across agents, tools, experiments, and documents. | 可选的 Agent、Tool、Experiment、Document 关系图谱。 | No |

---

## Docker Compose / Docker Compose

Phase 4 includes a conservative `docker-compose.yml` with backend, frontend, Postgres/pgvector, and Neo4j services.

Phase 4 提供保守的 `docker-compose.yml`，包含 backend、frontend、Postgres/pgvector 和 Neo4j 服务。

```bash
docker compose up --build
```

Default development URLs:

默认开发地址：

```text
Frontend: http://127.0.0.1:5173
Backend:  http://127.0.0.1:8000
Postgres: localhost:5432
Neo4j:    http://127.0.0.1:7474
```

---

## API Status / API 状态

```bash
curl http://127.0.0.1:8000/api/database/status
curl http://127.0.0.1:8000/api/deployment/status
curl http://127.0.0.1:8000/api/database/tables
curl http://127.0.0.1:8000/api/rag/documents
curl "http://127.0.0.1:8000/api/rag/query?q=OOS"
curl http://127.0.0.1:8000/api/graph/relationships
```

These endpoints report configuration readiness. They do not prove that every optional database is connected.

这些接口报告配置准备状态，不代表每个可选数据库都已经真实连接。

---

## Phase 8 Optional Integration / Phase 8 可选集成

Phase 8 keeps local files as the default and adds fallback-safe endpoints for RAG and graph readiness.

Phase 8 保持本地文件为默认模式，并增加 RAG 和图谱准备状态的 fallback-safe 接口。

```text
QUANT_MAS_STORAGE_MODE=local_files|sqlite|postgres
VECTOR_STORE=in_memory|pgvector
POSTGRES_DSN=
PGVECTOR_DSN=
NEO4J_URI=
NEO4J_USER=
NEO4J_PASSWORD=
```

If Postgres, pgvector, or Neo4j are not configured, APIs should return status warnings or fallback documents instead of failing.

如果没有配置 Postgres、pgvector 或 Neo4j，API 应返回状态提示或回退文档，而不是直接失败。

---

## Safety / 安全边界

The database and deployment layer must not expose broker, order, shell, secrets, or direct live-trading paths.

数据库和部署层不应暴露 broker、order、shell、secrets 或直接实盘交易路径。
