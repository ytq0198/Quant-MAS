# Plus M3：Memory / RAG v2 — Codex 提示词

更新时间：2026-06-02

> **用法**：先粘贴 [§10.1 总背景](../项目指导.md#101-总背景提示词)（或下方「固定前缀」），再粘贴「M3 主任务」整段交给 Codex。  
> **设计依据**：[项目plus设计.md §M3](../项目plus设计.md#m3数据库与-memory--rag-升级)

---

## 固定前缀（每次必贴）

```
你正在开发 Quant MAS 科研项目。
路径：D:\scientific reasearch and work\SRTP\Quant MAS

测试基线：本地 **115 passed**（Plus M2 + AV 日期提示测试，EXP-20260602-011/012）；
服务器 a6000-9961 已验证 test_data_sources **13 passed** + EXP-DATA-001（FRED/Stooq/AV）。
OOS 主 baseline：EXP-20260602-008，oos.sharpe **0.586**。

硬性原则：
1. LLM 不允许直接实盘下单。
2. pytest 不联网、不调真实 LLM API；外部 DB/Embedding 用 mock 或 HashEmbeddingClient。
3. 请只实现当前 **M3** 一个模块；改完后 `python -m pytest -v` 全量通过（预期 115+，新增 test_memory_store_v2）。
4. 不要破坏现有 ExperimentMemory / SimpleRetriever 对外 API；新后端可插拔并存。
5. 不要把 data/、outputs/、models/、logs/ 大文件加入 git；不要提交 .env 或真实 API key。
```

---

## M3 主任务（复制给 Codex）

```
请为 Quant MAS v2 实现可插拔 Memory / RAG 存储后端（Plus M3）。

## 背景

Prompt 20 已交付：
- src/quant_mas/memory/experiment_memory.py — ExperimentMemory（JSON append-only）
- src/quant_mas/memory/trade_memory.py — TradeMemory 空壳
- src/quant_mas/rag/document_loader.py — Document、load_documents
- src/quant_mas/rag/simple_retriever.py — SimpleRetriever 关键词检索
- tests/test_memory_rag.py — 11 项

Plus M1 已交付 compare_experiments / BaselineRegistry；新 Memory 后端须能继续被 metrics 收集使用。

## 目标

三库结构（渐进式，第一版只做 SQLite + InMemory 向量）：

| 层级 | v2 第一版 | 扩展（接口预留，pytest 不依赖） |
|------|-----------|----------------------------------|
| 元数据 | JSON 兼容 + SQLite experiments 表 | PostgreSQL |
| 向量 | InMemoryVectorStore + HashEmbeddingClient | FAISS / pgvector |
| 图 | 抽象接口占位 | Neo4j |

保留 SimpleRetriever；新增 VectorRetriever 或 HybridRetriever 可选，但 SimpleRetriever 必须仍可用。

## 需要实现的文件

### Memory 层

1. src/quant_mas/memory/store_base.py
   - 抽象 MemoryStore：add / get / list / search_by_name / sort_by_metric / find_best
   - 与 ExperimentRecord 字段对齐（experiment_id, name, status, metrics, artifacts, params, notes）

2. src/quant_mas/memory/json_store.py
   - JsonMemoryStore：包装现有 ExperimentMemory 逻辑，实现 MemoryStore 接口（向后兼容）

3. src/quant_mas/memory/sqlite_store.py
   - SqliteMemoryStore：experiments 表（id, name, status, created_at, metrics_json, artifacts_json, params_json, notes）
   - 支持按嵌套 metric 排序，如 metrics->oos->sharpe（与 ExperimentMemory.find_best 行为一致）
   - 使用 stdlib sqlite3；路径可配置，默认 {reports_dir}/experiments.db（从 storage yaml 或构造函数传入）

4. src/quant_mas/memory/factory.py（或 registry.py）
   - create_memory_store(backend: "json" | "sqlite", **kwargs) -> MemoryStore
   - 读 configs/memory.yaml（新建）：backend、sqlite_path、json_path

### RAG 层

5. src/quant_mas/rag/embedding_client.py
   - EmbeddingClient 抽象：embed(texts: list[str]) -> list[list[float]]
   - HashEmbeddingClient：确定性 hash 向量（维度可配置，如 64），供 pytest
   - OpenAICompatibleEmbeddingClient：骨架实现（读 EMBEDDING_* env），pytest 不调用真实 API

6. src/quant_mas/rag/vector_store_base.py
   - VectorStore 抽象：upsert(ids, embeddings, metadata) / search(query_embedding, top_k) / delete

7. src/quant_mas/rag/in_memory_vector_store.py
   - 余弦相似度检索；纯 Python + numpy（numpy 已在项目依赖中）

8. src/quant_mas/rag/faiss_store.py（可选）
   - 若 import faiss 失败则模块仍可 import，工厂里 faiss 后端 raise 清晰 ImportError
   - pytest 不依赖 faiss 安装

9. src/quant_mas/rag/chunking.py
   - chunk_text(text, chunk_size=512, overlap=64) -> list[str]
   - 供 index_documents 使用

10. src/quant_mas/rag/hybrid_retriever.py（推荐）
    - 组合 SimpleRetriever（关键词）+ 向量检索；merge 去重按 score 排序
    - 若未索引向量则仅关键词，不报错

### CLI

11. scripts/index_documents.py
    - 参数：--dirs docs outputs/reports（默认）、--chunk-size、--vector-store in_memory|faiss、--output（索引持久化路径，in_memory 可写 json）
    - 读取 document_loader，切块，HashEmbeddingClient 或 env 指定的 client，写入 VectorStore
    - --help 必须可用

12. scripts/query_memory.py
    - 子命令或参数：
      - --backend json|sqlite 查实验（--query 名称关键词 / --best-metric oos.sharpe）
      - --rag-query "walk-forward sharpe" 查文档（HybridRetriever 或 SimpleRetriever fallback）
    - --help 必须可用

### 配置

13. configs/memory.yaml
    - memory_backend: json | sqlite
    - sqlite_path: null  # 默认 reports/experiments.db
    - vector_store: in_memory
    - embedding_provider: hash  # hash | openai_compatible

14. .env.example 追加占位符（无真实值）：
    EMBEDDING_PROVIDER=hash
    EMBEDDING_BASE_URL=
    EMBEDDING_API_KEY=
    EMBEDDING_MODEL=
    VECTOR_STORE=in_memory
    POSTGRES_DSN=
    NEO4J_URI=

### 测试

15. tests/test_memory_store_v2.py（新增，至少 10 项，全部 mock/临时目录，不联网）
    - JsonMemoryStore 与 ExperimentMemory 行为一致（add/list/get/find_best 嵌套 metric）
    - SqliteMemoryStore CRUD + sort_by_metric + find_best("oos.sharpe")
    - json vs sqlite 同一批 record 指标一致
    - HashEmbeddingClient 确定性：同文本同向量
    - InMemoryVectorStore upsert + search top_k
    - chunk_text 长度与 overlap
    - HybridRetriever：有关键词命中；有向量时 merge
    - create_memory_store 读 yaml
    - index_documents CLI --help（subprocess 或 import main）
    - query_memory CLI --help

## 兼容性要求

- quant_mas.memory 继续 export ExperimentMemory、TradeMemory（不删不改签名）
- quant_mas.rag 继续 export SimpleRetriever、load_documents
- scripts/compare_experiments.py 仍读 JSON ExperimentMemory 或扩展为可选 --memory-backend sqlite（若改动须加测试）
- 现有 tests/test_memory_rag.py 全部保持通过

## 禁止

- pytest 依赖 Postgres / Neo4j / 真实 Embedding API / 网络
- 删除 SimpleRetriever 或破坏 Prompt 20 测试
- 在测试中写死服务器绝对路径

## 验收命令

python -m pytest tests/test_memory_store_v2.py -v
python -m pytest tests/test_memory_rag.py -v
python -m pytest -v   # 全量 115+ passed
python scripts/index_documents.py --help
python scripts/query_memory.py --help
```

---

## Cursor 后续（Codex 完成后）

1. 检查服务器是否有 Docker；新增 `docs/database_setup.md`（可选 Postgres+pgvector、Neo4j 占位说明；默认 SQLite + InMemoryVectorStore）。
2. 更新 `docs/architecture.md` Memory/RAG v2 分层图。
3. 更新 `项目进度.md`、`docs/progress.md`、`docs/experiment_log.md`（EXP-M3-001 本地 pytest）。
4. 服务器：`git pull` → `python -m pytest -v` → 可选 `index_documents.py` smoke（不联网可用 hash backend）。

---

## 参考现有代码

| 模块 | 路径 |
|------|------|
| ExperimentMemory | `src/quant_mas/memory/experiment_memory.py` |
| SimpleRetriever | `src/quant_mas/rag/simple_retriever.py` |
| document_loader | `src/quant_mas/rag/document_loader.py` |
| M1 compare | `scripts/compare_experiments.py` |
| Prompt 20 测试 | `tests/test_memory_rag.py` |
