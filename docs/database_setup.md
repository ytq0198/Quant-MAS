# Memory / RAG v2 数据库与向量存储（Plus M3）

更新时间：2026-06-02

> 配置：`configs/memory.yaml` · CLI：`index_documents.py` / `query_memory.py`

## 默认（pytest 与本地开发）

无需 Docker 或外部服务：

| 组件 | 默认 | 说明 |
|------|------|------|
| 实验元数据 | `json` | 兼容现有 `outputs/reports/experiments.json` |
| 可选 SQLite | `sqlite` | `{reports_dir}/experiments.db` |
| 向量存储 | `in_memory` | `InMemoryVectorStore` + 余弦相似度 |
| Embedding | `hash` | `HashEmbeddingClient`（确定性，不联网） |

```yaml
# configs/memory.yaml
memory_backend: json
json_path: outputs/reports/experiments.json
sqlite_path: null
vector_store: in_memory
embedding_provider: hash
```

```bash
python scripts/index_documents.py --help
python scripts/query_memory.py --help
python scripts/query_memory.py --backend json --best-metric oos.sharpe
python scripts/query_memory.py --rag-query "walk-forward sharpe"
```

## 切换到 SQLite

```yaml
memory_backend: sqlite
sqlite_path: outputs/reports/experiments.db
```

或通过 CLI：

```bash
python scripts/query_memory.py --backend sqlite --query walk-forward
```

## 可选扩展（不进 pytest）

以下需自行安装服务；**勿**把真实密码 commit 到 git。

### PostgreSQL + pgvector（占位）

```env
POSTGRES_DSN=postgresql://user:password@localhost:5432/quant_mas
```

用途：生产级实验元数据与 pgvector 向量检索。M3 第一版未强制实现 Postgres 后端，接口可在后续 M 扩展。

### FAISS（可选）

```env
VECTOR_STORE=faiss
```

需 `pip install faiss-cpu`（或 GPU 版）。未安装时 `faiss_store` 模块可 import，工厂会给出清晰 `ImportError`。

### Neo4j（占位）

```env
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=change-me
```

用途：策略–特征–实验关系图；M3 仅预留 env，pytest 不依赖。

### OpenAI-compatible Embedding（骨架）

```env
EMBEDDING_PROVIDER=openai_compatible
EMBEDDING_BASE_URL=https://api.example.com/v1
EMBEDDING_API_KEY=
EMBEDDING_MODEL=text-embedding-3-small
```

pytest 使用 `hash`；真实 API 仅服务器手工验证时使用。

## 服务器建议

a6000-9961 当前**无 Docker 要求**：

1. `git pull` → `python -m pip install -e .`
2. `python -m pytest -v`（预期 **126 passed**）
3. 可选 smoke（不联网）：
   ```bash
   python scripts/index_documents.py --dirs docs --vector-store in_memory
   python scripts/query_memory.py --rag-query "OOS sharpe baseline"
   ```

## 相关文档

- [architecture.md](architecture.md) — Memory/RAG v2 分层
- [codex_prompt_M3.md](codex_prompt_M3.md) — M3 设计与验收
- [mistakes.md](../mistakes.md) — M-014 API key 勿写入 `.env.example`
