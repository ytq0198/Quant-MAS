# Memory / RAG Database Setup

This document describes Quant MAS memory and RAG storage backends.

Quant MAS defaults remain local and lightweight:

- experiment memory: JSON
- optional local database: SQLite
- vector store for tests: InMemoryVectorStore
- embedding client for tests: HashEmbeddingClient

Enterprise backends added in M9 are optional and are not required for pytest.

---

## Default Local Setup

```yaml
# configs/memory.yaml
memory_backend: json
json_path: outputs/reports/experiments.json
sqlite_path: null
vector_store: in_memory
embedding_provider: hash
```

Useful commands:

```bash
python scripts/index_documents.py --help
python scripts/query_memory.py --help
python scripts/query_memory.py --backend json --best-metric oos.sharpe
python scripts/query_memory.py --rag-query "walk-forward sharpe"
```

---

## SQLite

SQLite is useful for local structured experiment queries without running external services.

```yaml
memory_backend: sqlite
sqlite_path: outputs/reports/experiments.db
```

```bash
python scripts/query_memory.py --backend sqlite --query walk-forward
```

---

## M9 Enterprise Backends

M9 adds optional enterprise storage backends:

- `PostgresMemoryStore`: experiment metadata storage with JSONB metrics, artifacts, params, and notes.
- `PgVectorStore`: pgvector-backed vector store for document embeddings.
- `Neo4jGraphStore`: strategy-feature-experiment graph relationship skeleton.

These backends are optional. Tests use mock connections and do not require real Postgres, pgvector, or Neo4j services.

**Local validation**: EXP-20260602-025 — `test_memory_enterprise.py` **12 passed**; full suite **207 passed** (2026-06-01). Server Postgres smoke: EXP-20260602-026（待做）.

Copy the example config:

```bash
cp configs/memory.enterprise.yaml.example configs/memory.enterprise.yaml
```

Do not commit real credentials.

```env
POSTGRES_DSN=postgresql://user:password@localhost:5432/quant_mas
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=change-me
```

Seed Postgres from existing JSON (server smoke, EXP-026):

```bash
python scripts/seed_postgres_from_json.py \
  --json-path /mnt/localDisk3/weizian/reports/experiments.json
```

Query experiment memory from Postgres:

```bash
python scripts/query_memory.py --backend postgres --best-metric oos.sharpe
```

Index local docs into pgvector:

```bash
python scripts/index_documents.py --vector-store pgvector --dirs docs --embedding-dimensions 64
```

---

## Neo4j Graph Store

`Neo4jGraphStore` is intended for strategy-feature-experiment relationships:

- `Experiment`
- `Strategy`
- `Feature`
- `(:Experiment)-[:USES_STRATEGY]->(:Strategy)`
- `(:Experiment)-[:USES_FEATURE]->(:Feature)`

The first version is a small CRUD wrapper and is tested with a mock driver.

---

## Optional FAISS

FAISS remains optional and is not required for default tests.

```bash
python scripts/index_documents.py --vector-store faiss --dirs docs
```

If FAISS is not installed, the module raises a clear `ImportError`.

---

## Optional OpenAI-Compatible Embeddings

Real embedding APIs should only be used in manually configured environments. Pytest uses `HashEmbeddingClient`.

```env
EMBEDDING_PROVIDER=openai_compatible
EMBEDDING_BASE_URL=https://api.example.com/v1
EMBEDDING_API_KEY=
EMBEDDING_MODEL=text-embedding-3-small
```

---

## Validation

```bash
python -m pytest tests/test_memory_enterprise.py -v
python -m pytest -v
```

Current M9 tests do not connect to external services and do not read secrets.
