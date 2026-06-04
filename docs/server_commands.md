# Quant MAS Server Runbook

GitHub: [https://github.com/ytq0198/Quant-MAS](https://github.com/ytq0198/Quant-MAS)

**Server project path**: `/mnt/localDisk3/weizian/Quant-MAS`

> **Environment**: always `conda activate /mnt/localDisk3/weizian/conda_envs/quant-mas` before `python -m pytest` / `python -m pip`. Do not use bare `pytest` / `pip`.

---

## Verification snapshot

| Date | Task | Result | EXP |
|------|------|--------|-----|
| 2026-06-04 | v3 M13.3 paper export | **361 passed** + 6 artifacts | EXP-M13-004 @ `6913dbf` |
| 2026-06-04 | v3 M13.2 LangGraph backend | **354 passed** + langgraph dry-run | EXP-M13-003 |
| 2026-06-04 | v3 M13.1 YAML recipe | **349 passed** + 4 yaml.example | EXP-M13-002 @ `2610612` |
| 2026-06-04 | v3 M13.0 MCP scheduler | **342 passed** + dry-run | EXP-M13-001 @ `605fa66` |
| 2026-06-04 | v3 M12.4 feature_linear OOS | **310 passed**; oos **0.387** | EXP-POP-010 |
| 2026-06-04 | EXP-TEXT-WF-003 real news OOS | oos.sharpe **0.565** vs **0.586** | EXP-TEXT-WF-003 |
| 2026-06-04 | v3 M11.8 batch candidate OOS | best **1.039** | EXP-POP-006 |
| 2026-06-02 | Walk-forward ML baseline | OOS sharpe **0.586** | EXP-20260602-008 |

Paper baseline: **EXP-20260602-008** (`oos.sharpe = 0.586`, 19 walk-forward windows)

---

## Daily smoke

```bash
cd /mnt/localDisk3/weizian/Quant-MAS
git pull origin main
conda activate /mnt/localDisk3/weizian/conda_envs/quant-mas

python -m pytest -v                    # expect 361 passed
python -c "import quant_mas; print('ok')"
```

---

## First-time setup

```bash
mkdir -p /mnt/localDisk3/weizian/conda_envs
cd /mnt/localDisk3/weizian
git clone https://github.com/ytq0198/Quant-MAS.git
cd Quant-MAS

mkdir -p /mnt/localDisk3/weizian/datasets/{raw,processed,features,text}
mkdir -p /mnt/localDisk3/weizian/{models,reports,logs}

cp configs/storage.server.yaml.example configs/storage.server.yaml

conda create -p /mnt/localDisk3/weizian/conda_envs/quant-mas python=3.11 -y
conda activate /mnt/localDisk3/weizian/conda_envs/quant-mas

python -m pip install --upgrade pip setuptools wheel
python -m pip install -e .
python -m pip install -r requirements-data.txt
python -m pip install -r requirements-ml.txt
python -m pip install -e ".[orchestration]"   # LangGraph (M13.2 optional)

python -m pytest -v
```

**Path conventions**

| Purpose | Path |
|---------|------|
| Feature table | `/mnt/localDisk3/weizian/datasets/features/features.parquet` |
| Experiment memory | `/mnt/localDisk3/weizian/reports/experiments.json` or `outputs/reports/experiments.json` |
| Models | `/mnt/localDisk3/weizian/models/` |
| Reports | `/mnt/localDisk3/weizian/reports/` |
| M13 audit logs | `outputs/pipelines/<run_id>/audit.jsonl` |
| Paper export | `outputs/paper/` |

---

## Core pipelines

### End-to-end (Stooq real-data smoke)

```bash
conda activate /mnt/localDisk3/weizian/conda_envs/quant-mas
cd /mnt/localDisk3/weizian/Quant-MAS

python scripts/run_pipeline.py \
  --symbols AAPL MSFT SPY \
  --start 2018-01-01 \
  --end 2025-12-31 \
  --storage-config configs/storage.server.yaml \
  --skip-download \
  --experiment-name server_ma_cross_real_001
```

### LightGBM training (GPU)

```bash
# If CUDA Tree Learner fails, see mistakes.md M-010 (build LightGBM from source)
nvidia-smi

python scripts/train_model.py \
  --config configs/train.gpu.yaml \
  --storage-config configs/storage.server.yaml \
  --device cuda \
  --experiment-name server_lgbm_gpu_001
```

### Walk-forward OOS (paper baseline)

```bash
python scripts/run_walk_forward.py \
  --config configs/walk_forward.yaml \
  --storage-config configs/storage.server.yaml \
  --features-path /mnt/localDisk3/weizian/datasets/features/features.parquet \
  --experiment-name server_walk_forward_001

python scripts/compare_experiments.py \
  --storage-config configs/storage.server.yaml \
  --output-dir /mnt/localDisk3/weizian/reports/research
```

Verified: **oos.sharpe = 0.586** (EXP-20260602-008)

---

## Text ablation (M6)

### EXP-TEXT-WF-003 (real Finnhub)

Fetch window: **2025-06-04 ~ 2026-06-04** (not 2018-2025). Result: **oos.sharpe = 0.565**, coverage **2.42%**.

```bash
python -m pip install -e ".[ml,text]"

python scripts/fetch_real_news.py \
  --source finnhub --symbols AAPL MSFT SPY \
  --start 2025-06-04 --end 2026-06-04 \
  --output-path /mnt/localDisk3/weizian/datasets/text/real_news_wf003.jsonl

python scripts/align_real_news.py \
  --news-path /mnt/localDisk3/weizian/datasets/text/real_news_wf003.jsonl \
  --features-path /mnt/localDisk3/weizian/datasets/features/features.parquet \
  --output-dir /mnt/localDisk3/weizian/reports/real_news_alignment_wf003

python scripts/train_text_model.py --mode finbert_baseline \
  --config configs/text_model.server.yaml \
  --text-path /mnt/localDisk3/weizian/reports/real_news_alignment_wf003/aligned_news.jsonl \
  --signals-output /mnt/localDisk3/weizian/datasets/text/signals_finbert_wf003.parquet

python scripts/audit_text_signals.py \
  --features-path /mnt/localDisk3/weizian/datasets/features/features.parquet \
  --signals-path /mnt/localDisk3/weizian/datasets/text/signals_finbert_wf003.parquet \
  --output-dir /mnt/localDisk3/weizian/reports/text_signal_audit_wf003

python scripts/run_walk_forward.py \
  --config configs/walk_forward.yaml \
  --storage-config configs/storage.server.yaml \
  --features-path /mnt/localDisk3/weizian/datasets/features/features_with_text_wf003.parquet \
  --experiment-name server_walk_forward_text_003
```

See [real_news_text_experiment.md](real_news_text_experiment.md).

---

## Population / candidate OOS (M11-M11.8)

```bash
python scripts/run_population_training.py \
  --config configs/population_training.yaml --dry-run

python scripts/export_population_candidates.py \
  --population-config configs/population_training.yaml \
  --top-k 2 --run-backtest-smoke --no-dry-run

python scripts/validate_candidate_oos.py \
  --candidate-json outputs/candidates/candidates.json \
  --features-path /mnt/localDisk3/weizian/datasets/features/features.parquet \
  --config configs/candidate_oos.yaml

python scripts/batch_validate_candidates.py \
  --candidate-json outputs/candidates/candidates.json \
  --features-path /mnt/localDisk3/weizian/datasets/features/features.parquet \
  --config configs/candidate_oos.yaml --top-k 5 --no-dry-run
```

Verified: EXP-POP-005 **1.036**; EXP-POP-006 best **1.039** vs baseline **0.586**

---

## RL chain (M12: simulation -> export -> OOS)

```bash
python scripts/run_rl_experiment.py \
  --config configs/rl.yaml --dry-run

python scripts/export_rl_policy_candidate.py \
  --checkpoint-dir outputs/rl/latest --dry-run

python scripts/validate_candidate_oos.py \
  --candidate-id rl_feature_linear_policy_001_1 \
  --features-path /mnt/localDisk3/weizian/datasets/features/features.parquet \
  --config configs/candidate_oos.yaml
```

Verified: EXP-POP-009 oos **0.0** (all-cash); EXP-POP-010 oos **0.387**

---

## Enterprise DB (M9) and vLLM (M10)

### Postgres / pgvector smoke

```bash
python -m pip install "psycopg[binary]>=3.1" neo4j
export POSTGRES_DSN="postgresql://..."
python scripts/query_memory.py --backend postgres --help
python scripts/index_documents.py --backend pgvector --help
```

### local vLLM + ResearchAgent (EXP-LLM-002)

```bash
# Terminal 1: vLLM (separate conda env)
conda activate /mnt/localDisk3/weizian/conda_envs/vllm
export VLLM_USE_FLASHINFER_SAMPLER=0
CUDA_VISIBLE_DEVICES=0 vllm serve /mnt/localDisk3/weizian/models/Qwen2.5-7B-Instruct \
  --host 127.0.0.1 --port 8000 --dtype auto --max-model-len 8192

# Terminal 2: ResearchAgent
conda activate /mnt/localDisk3/weizian/conda_envs/quant-mas
export VLLM_BASE_URL=http://127.0.0.1:8000
export VLLM_MODEL=Qwen/Qwen2.5-7B-Instruct

python scripts/run_research_agent.py \
  --provider local_vllm --use-llm \
  --task "Interpret walk-forward OOS baseline EXP-20260602-008 (oos.sharpe ~ 0.586). List three research risks."
```

---

## M13 orchestration (complete: EXP-M13-001 to EXP-M13-004)

### M13.0-M13.1: Scheduler + YAML recipe dry-run

```bash
cd /mnt/localDisk3/weizian/Quant-MAS
git pull origin main
conda activate /mnt/localDisk3/weizian/conda_envs/quant-mas

python -m pytest tests/test_mcp_scheduler.py -v
python -m pytest tests/test_mcp_pipeline_recipes.py -v

python scripts/run_mcp_pipeline.py --list-recipes
python scripts/run_mcp_pipeline.py --recipe mock_research --dry-run
python scripts/run_mcp_pipeline.py --recipe configs/pipelines/text_enhanced.yaml.example --dry-run
python scripts/run_mcp_pipeline.py --recipe configs/pipelines/rl_ablation.yaml.example --dry-run
```

### M13.2: LangGraph backend

```bash
python -m pytest tests/test_langgraph_recipe_workflow.py -v
python -c "import importlib.metadata as m; print('langgraph', m.version('langgraph'))"

python scripts/run_mcp_pipeline.py --backend langgraph \
  --recipe configs/pipelines/text_enhanced.yaml.example --dry-run
python scripts/run_mcp_pipeline.py --backend langgraph \
  --recipe configs/pipelines/rl_ablation.yaml.example --dry-run
python scripts/run_mcp_pipeline.py --backend scheduler \
  --recipe configs/pipelines/ml_baseline.yaml.example --dry-run
```

Falls back to scheduler dry-run when LangGraph is not installed.

### M13.3: Paper artifact export

```bash
python -m pytest tests/test_paper_artifacts.py -v
python -m pytest -v

python scripts/export_paper_artifacts.py \
  --memory-path outputs/reports/experiments.json \
  --audit-dir outputs/pipelines \
  --output-dir outputs/paper

ls -la outputs/paper/
head -5 outputs/paper/paper_main_results.csv
```

Outputs: `paper_main_results.csv`, `paper_text_ablation.csv`, `paper_population_ablation.csv`, `paper_rl_ablation.csv`, `paper_experiment_index.md`, `audit_summary.json`

Rules: main table uses `oos.*` only; simulation-only RL excluded; missing values left blank.

See [mcp_protocol.md](mcp_protocol.md).

---

## Local vs server

| Action | Local Windows | Server |
|--------|---------------|--------|
| Dev | Codex / Cursor | SSH |
| Tests | `python -m pytest -v` | `conda activate .../quant-mas && python -m pytest -v` |
| Sync | `git push origin main` | `git pull origin main` |

```powershell
cd "D:\scientific reasearch and work\SRTP\Quant MAS"
git add .
git commit -m "your message"
git push origin main
```

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| LightGBM CUDA Fatal | Build from source; see [mistakes.md](../mistakes.md) M-010 |
| walk-forward `no complete windows` with text | Set `text_signal_fillna: 0` |
| vLLM OOM | `pkill -f "vllm serve"` or use another GPU |
| Finnhub fetch returns 0 | Check `--start` window (free tier ~1 year) |
| LangGraph has no `__version__` | Use `importlib.metadata.version('langgraph')` |
