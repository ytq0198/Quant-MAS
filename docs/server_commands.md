# Quant MAS ???????

GitHub ???[https://github.com/ytq0198/Quant-MAS](https://github.com/ytq0198/Quant-MAS)

**???????**?`/mnt/localDisk3/weizian/Quant-MAS`

> **??**???? `conda activate quant-mas`??? `python -m pytest` ? `python -m pip`????? `pytest` / `pip`?

## ????

| ?? | ?? | ?? | ?? |
|------|------|------|------|
| 2026-06-04 | v3 M13.0 ??? pytest + pipeline smoke | **342 passed**?53.99s?+ dry-run ? | EXP-M13-001 @ `605fa66` |
| 2026-06-04 | v3 M12.1 ??? RL training smoke | GRPO **simulation.sharpe_mean 6.31** ? | EXP-POP-007 @ `e291cf9` |
| 2026-06-04 | v3 M11.8 ??? pytest | **266 passed**?45.63s?? | EXP-POP-006 |
| 2026-06-04 | v3 M11.7 ??? candidate OOS | `cand_mean_rev_1` **oos.sharpe 1.036** vs **0.586** ? | EXP-POP-005 @ `ffef849` |
| 2026-06-03 | v3 M11.7 ??? pytest | **259 passed**?48.32s?? | EXP-POP-005 @ `f804a95` |
| 2026-06-03 | v3 M11.7 ?? OOS hook??? mock? | **259 passed**?OOS **11/11** ? | EXP-20260602-032 |
| 2026-06-03 | v3 M11.6 ??? pytest + candidate export | **248 passed**?55.15s?+ dry-run ? | EXP-POP-004 @ `7ab510f` |
| 2026-06-03 | v3 M11.6 ????????? | **248 passed**?bridge **11/11** ? | EXP-20260602-031 |
| 2026-06-03 | v3 M11.5 ??? pytest + population training | **237 passed**?41.83s?+ 3-gen dry-run ? | EXP-POP-003 @ `aa841d4` |
| 2026-06-03 | v3 M11 ??? pytest + competitive mock | **225 passed**?17.32s?+ dry-run ? | EXP-POP-002 @ `64a5b2a` |
| 2026-06-03 | v3 M10 local_vLLM smoke | ResearchAgent `local_vllm` ? | EXP-LLM-002 |
| 2026-06-01 | v3 M9/M10 ??? pytest | **212 passed**?11.39s? | EXP-20260602-028 |
| 2026-06-01 | v3 M9 ?? DB???? | **207 passed**?+12??enterprise **12/12** | EXP-20260602-025 |
| 2026-06-01 | Plus M8 MCP/A2A ??? | **195 passed**?12.41s??export_agent_cards ? | EXP-20260602-024 |
| 2026-06-01 | Plus M7 ??? | **180 passed**?10.15s??RL dry-run ? | EXP-20260602-022 |
| 2026-06-01 | Plus M8 MCP/A2A???? | **195 passed**?+15? | EXP-20260602-023 |
| 2026-06-01 | Plus M7 RL ?????? | **180 passed**?+19? | EXP-20260602-021 |
| 2026-06-03 | EXP-TEXT-WF-001 text + walk-forward | oos.sharpe **0.563** vs **0.586** | EXP-TEXT-001 |
| 2026-06-03 | Plus M6 ????????? | **161 passed**?22.14s? | EXP-20260602-020 |
| 2026-06-03 | Plus M6 ???????? | **161 passed** | EXP-20260602-019 |
| 2026-06-03 | Plus M5 ???/LLM????? | **150 passed**?7.24s? | EXP-20260602-018 |
| 2026-06-03 | Plus M5 ???/LLM???? | **150+1 warning** | EXP-20260602-017 |
| 2026-06-03 | Plus M4 LangGraph ??? | langgraph dry-run ? | EXP-20260602-016 |
| 2026-06-02 | Plus M3 Memory/RAG v2???+???? | **126 passed** | EXP-20260602-013/014 |
| 2026-06-02 | Plus M2 ???????+???? | **115 passed** / test_data_sources **13/13** | EXP-20260602-011/012 |
| 2026-06-02 | Plus M1 research baseline (local) | **102 passed** | EXP-20260602-009 |
| 2026-06-01 | pytest?Prompt 20 ?????? | **98 passed**?1.93s? | EXP-20260601-014 |
| 2026-06-01 | pytest?Prompt 20 ????? | **98 passed** | EXP-20260601-013 |
| 2026-06-02 | Walk-forward ??? | `server_walk_forward_001`?OOS sharpe **0.586** | Prompt 17 ? |
| 2026-06-02 | pytest | **71 passed**?Prompt 17 ?? |
| 2026-06-02 | Walk-forward ?? | **71 passed**?Prompt 17 ?? ? | ? |
| 2026-06-02 | GPU ?? | `server_lgbm_gpu_001`?device=cuda?test AUC 0.479 | ? M-010 |
| 2026-06-02 | ML ?? | `server_ml_backtest_001`?sharpe **2.78** | Prompt 16 ? |
| 2026-06-02 | pytest??? | **44 passed**?Python 3.11.15?1.19s? |
| 2026-06-01 | LightGBM ?? | `server_lgbm_001`?test AUC 0.466 | ????? |
| 2026-06-01 | Prompt 16 + GPU ?? | **68 passed**?`--device` ?? | ? |
| 2026-06-01 | ???? + pipeline | Stooq 6033 rows?`server_ma_cross_real_001` | ? |

### pytest

```bash
conda activate /mnt/localDisk3/weizian/conda_envs/quant-mas
cd /mnt/localDisk3/weizian/Quant-MAS
python -m pytest -v
```

## ??????

```bash
# 1. ???????
mkdir -p /mnt/localDisk3/weizian/conda_envs
cd /mnt/localDisk3/weizian
git clone https://github.com/ytq0198/Quant-MAS.git
cd Quant-MAS

# 2. ??????
mkdir -p /mnt/localDisk3/weizian/datasets/{raw,processed,features}
mkdir -p /mnt/localDisk3/weizian/{models,reports,logs}

# 3. ???????
cp configs/storage.server.yaml.example configs/storage.server.yaml

# 4. ?? Python 3.11 ?????? 3.11???? 3.9?
# ???????? env?????
# rm -rf /mnt/localDisk3/weizian/conda_envs/quant-mas

CONDA_ENV_PREFIX=/mnt/localDisk3/weizian/conda_envs/quant-mas bash server/setup_server.sh

# 5. ?????
conda activate /mnt/localDisk3/weizian/conda_envs/quant-mas
python --version              # ?? 3.11.x
python -m pip --version       # ???? 3.11???? 3.9

# 6. ? setup ??????????? bare pip?
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt
python -m pip install -e .
python -m pip install -r requirements-data.txt   # ????????
python -m pip install -r requirements-ml.txt     # ML ????
python -m pytest -v
```

> **???? A**?`Python 3.9.13 not in '>=3.11'` ? ??? 3.9?? `rm -rf .../conda_envs/quant-mas` ????
>
> **???? B**?`python` ? 3.11 ? `pip` ?? `~/.local` ? 3.9 ? **??? `python -m pip`**?????? `pip`?
>
> ```bash
> conda activate /mnt/localDisk3/weizian/conda_envs/quant-mas
> python -m pip install -e ".[data,ml]"
> ```

???

```bash
which python      # ??? /mnt/localDisk3/weizian/conda_envs/quant-mas/bin/python
python --version  # ??? 3.11.x???? 3.9?
which pytest      # ???? conda env ?
```

## ????????

```bash
cd /mnt/localDisk3/weizian/Quant-MAS
git pull origin main
conda activate /mnt/localDisk3/weizian/conda_envs/quant-mas
python -m pip install -r requirements.txt
python -m pip install -e .
python -m pip install -r requirements-data.txt
python -m pip install -r requirements-ml.txt
python -m pytest -v
```

## ??????????

**yfinance ??**??? `YFRateLimitError` ???????????? **Stooq + API Key**?

### 0. ?? Stooq API Key?????

1. ??????https://stooq.com/q/d/?s=aapl.us&get_apikey  
2. ?? captcha??? 32 ? apikey  
3. ??????????

```bash
cd /mnt/localDisk3/weizian/Quant-MAS
cp .env.example .env
nano .env   # ?? STOOQ_API_KEY=??key?? commit?
```

???

```bash
python scripts/download_data.py \
  --symbols AAPL \
  --start 2018-01-01 --end 2019-01-01 \
  --source stooq \
  --storage-config configs/storage.server.yaml \
  --filename AAPL_2018.parquet
```

### ?? A??? resilient ??????

```bash
cd /mnt/localDisk3/weizian/Quant-MAS
conda activate /mnt/localDisk3/weizian/conda_envs/quant-mas
git pull origin main
python -m pip install -e .

# ??? .env ??? STOOQ_API_KEY
SOURCE=stooq SYMBOLS="AAPL" bash server/download_data_resilient.sh
SOURCE=stooq SYMBOLS="AAPL MSFT SPY" bash server/download_data_resilient.sh

# Yahoo ??????? yfinance??? 30?60 ???
# INITIAL_COOLDOWN_SECONDS=1800 SOURCE=yfinance SYMBOLS="AAPL" bash server/download_data_resilient.sh
```

????
1. ?? `source .env` ?? `STOOQ_API_KEY`
2. ???? **??** ?????`AAPL_2018.parquet` ??
3. ????? **????**???????
4. ????? `datasets/raw/market_data.parquet`

### ?? B???????

`download_data.py` ??????????? `.env`?`STOOQ_API_KEY`??

```bash
python scripts/download_data.py \
  --symbols AAPL \
  --start 2018-01-01 --end 2019-01-01 \
  --source stooq \
  --storage-config configs/storage.server.yaml \
  --filename AAPL_2018.parquet \
  --skip-existing
sleep 30
```

???

```bash
python scripts/merge_parquet.py \
  --input-dir /mnt/localDisk3/weizian/datasets/raw \
  --pattern "*_*.parquet" \
  --exclude market_data.parquet \
  --output /mnt/localDisk3/weizian/datasets/raw/market_data.parquet
```

### ?? C??? CSV???????

? CSV ?? `/mnt/localDisk3/weizian/datasets/raw/manual/`?????? parquet?Phase 3 ????

## ????? Pipeline

?????????`market_data.parquet` ?????

```bash
cd /mnt/localDisk3/weizian/Quant-MAS
conda activate /mnt/localDisk3/weizian/conda_envs/quant-mas

python scripts/run_pipeline.py \
  --symbols AAPL MSFT SPY \
  --start 2018-01-01 \
  --end 2025-12-31 \
  --storage-config configs/storage.server.yaml \
  --skip-download \
  --experiment-name server_ma_cross_real_001
```

**????2026-06-01?**?6033 feature rows?sharpe ? 1.00??? `/mnt/localDisk3/weizian/reports/server_ma_cross_real_001/`?

Synthetic / ??? smoke test?`bash server/run_small_pipeline.sh`

## ??ML ???Prompt 15 + GPU?

### CPU ????? / ???

```bash
conda activate /mnt/localDisk3/weizian/conda_envs/quant-mas
cd /mnt/localDisk3/weizian/Quant-MAS
python -m pip install -r requirements-ml.txt

python scripts/train_model.py \
  --config configs/train.yaml \
  --storage-config configs/storage.server.yaml \
  --experiment-name server_lgbm_001
```

### GPU / CUDA ???A6000?

**?? GPU ???**???? LightGBM ? CUDA ????PyPI ?? wheel ?? **CPU-only**?? `nvidia-smi` ?? **??** ?? `--device cuda` ??????? CUDA ??`fit()` ?????? **??** ?? fallback?

```text
[LightGBM] [Fatal] CUDA Tree Learner was not enabled in this build.
```

?? [`mistakes.md` M-010](../mistakes.md#m-010-lightgbm-pypi-wheel-?-cpu-only)?

#### 0. ?? CUDA ? LightGBM?????????? 5 ???

```bash
conda activate /mnt/localDisk3/weizian/conda_envs/quant-mas
cd /mnt/localDisk3/weizian/Quant-MAS

python -m pip uninstall -y lightgbm
python -m pip install --no-binary lightgbm \
  --config-settings=cmake.define.USE_CUDA=ON 'lightgbm==4.6.0'

# ???????
python -c "from lightgbm import LGBMClassifier; LGBMClassifier(device='cuda').fit([[0],[1]], [0,1])"
```

???4× NVIDIA RTX A6000??? 580?CUDA 13.0?2026-06-02 ?????

#### 1. ??

```bash
nvidia-smi

python scripts/train_model.py \
  --config configs/train.gpu.yaml \
  --storage-config configs/storage.server.yaml \
  --device cuda \
  --experiment-name server_lgbm_gpu_001

# ?? device ????? cuda ? fallback=false?
grep device /mnt/localDisk3/weizian/models/lightgbm_direction_latest/metadata.json
grep device /mnt/localDisk3/weizian/models/lightgbm_direction_latest/metrics.json
```

#### CPU ??????? EXP-20260601-006 ???

```bash
python scripts/train_model.py \
  --config configs/train.yaml \
  --storage-config configs/storage.server.yaml \
  --device cpu \
  --experiment-name server_lgbm_cpu_001
```

~6k ???? GPU ????????????? metrics ?????metadata ? `device_resolved` ?????

? GPU ? CUDA ?????Quant MAS ? **??????** ? fallback ? CPU??? `device=cuda` ? LightGBM ??? CUDA ????? `fit()` ? **Fatal**?? M-010??

## ??ML ?? / Walk-forward

**ML ???Prompt 16 ???????? EXP-20260602-005?**?

```bash
git pull origin main
python -m pip install -e .
python -m pytest -v

python scripts/run_ml_backtest.py \
  --config configs/backtest_ml.yaml \
  --storage-config configs/storage.server.yaml \
  --features-path /mnt/localDisk3/weizian/datasets/features/features.parquet \
  --model-path /mnt/localDisk3/weizian/models/lightgbm_direction_latest/model.pkl \
  --experiment-name server_ml_backtest_001
```

?????2026-06-02??sharpe **2.78**?max_drawdown **-0.246**?2011 bars??? `outputs/reports/ml_backtest_latest/summary.md`?

**Walk-forward?Prompt 17 ??EXP-20260602-008?**?

????2026-06-02??19 ???? 17s?OOS sharpe **0.586**?total_return **0.443**?auc_mean **0.472**?

```bash
git pull origin main
python -m pip install -e .
python -m pytest -v   # ?? 126 passed?Plus M3 ??

python scripts/run_walk_forward.py \
  --config configs/walk_forward.yaml \
  --storage-config configs/storage.server.yaml \
  --features-path /mnt/localDisk3/weizian/datasets/features/features.parquet \
  --experiment-name server_walk_forward_001
```

???`metrics.json`?? train/val/test/oos??`windows.csv`?`oos_equity_curve.csv`?`oos_trades.csv`?`summary.md`?

## ????Plus M2 ?? API smoke?EXP-DATA-001??

> **??**??? key ?? `.env.example` ? commit ? GitHub?????? **`/mnt/localDisk3/weizian/Quant-MAS/.env`** ???????? `.gitignore`??

**???**?2026-06-02?EXP-20260602-012??FRED DGS10 262 ??Stooq 105 ??Alpha Vantage 100 ??Finnhub ?? tier 403?????SEC ???

?????

```bash
cd /mnt/localDisk3/weizian/Quant-MAS
git pull origin main
conda activate /mnt/localDisk3/weizian/conda_envs/quant-mas
python -m pip install -e .
python -m pytest tests/test_data_sources.py -v   # ?? 13 passed

# ???????? .env?? nano/vim ?? key??? paste ? .env.example?
cp .env.example .env
nano .env
```

`.env` ???????????????

```env
STOOQ_API_KEY=...
ALPHAVANTAGE_API_KEY=...
FINNHUB_API_KEY=...
FRED_API_KEY=...
SEC_EDGAR_USER_AGENT=YourName your@email.com   # SEC ????? M2 ??? key ???? FRED/AV/Finnhub
```

`download_data.py` ??? `load_repo_dotenv()` ????????? `.env`?

**?? smoke ??**?? key ????

```bash
# 1. FRED ??????
python scripts/download_data.py --source fred --series-id DGS10 \
  --start 2024-01-01 --end 2024-12-31 \
  --storage-config configs/storage.server.yaml
ls -la /mnt/localDisk3/weizian/datasets/raw/macro/

# 2. Alpha Vantage OHLCV??? tier ? ~100 ???????? 2024 ???
python scripts/download_data.py --source alpha_vantage \
  --symbols AAPL --start 2026-01-01 --end 2026-06-01 \
  --storage-config configs/storage.server.yaml

# 3. Finnhub OHLCV
python scripts/download_data.py --source finnhub \
  --symbols AAPL --start 2024-01-01 --end 2024-06-01 \
  --storage-config configs/storage.server.yaml

# 4. Stooq??? key????
python scripts/download_data.py --source stooq \
  --symbols AAPL --start 2024-01-01 --end 2024-06-01 \
  --storage-config configs/storage.server.yaml
```

SEC???? `.env` ? `SEC_EDGAR_USER_AGENT` ?????+????

```bash
python scripts/download_data.py --source sec_edgar --cik 0000320193 \
  --storage-config configs/storage.server.yaml
ls -la /mnt/localDisk3/weizian/datasets/raw/sec/
```

??????? `docs/experiment_log.md` **EXP-20260602-012** / **EXP-DATA-001**?

## ????Plus M3 Memory/RAG?EXP-20260602-013?

M3 pull ??????

```bash
cd /mnt/localDisk3/weizian/Quant-MAS
git pull origin main
conda activate /mnt/localDisk3/weizian/conda_envs/quant-mas
python -m pip install -e .
python -m pytest -v   # ?? 126 passed

python scripts/index_documents.py --help
python scripts/query_memory.py --help

# ?? smoke?????hash embedding?
python scripts/index_documents.py --dirs docs --vector-store in_memory
python scripts/query_memory.py --rag-query "walk-forward OOS sharpe"

python scripts/query_memory.py \
  --backend json \
  --json-path /mnt/localDisk3/weizian/reports/experiments.json \
  --best-metric oos.sharpe
```

???**EXP-20260602-014**??? `--json-path outputs/reports/experiments.json` ???? `reports_dir`?

## ????Plus M4 LangGraph?EXP-20260602-015/016?

```bash
cd /mnt/localDisk3/weizian/Quant-MAS
git pull origin main   # ? >= c0fa5e3?M-016 ?????
conda activate /mnt/localDisk3/weizian/conda_envs/quant-mas
python -m pip install -e .
python -m pip install -e ".[orchestration]"

python -m pytest tests/test_langgraph_workflow.py::test_langgraph_build_and_dry_run_when_available -v
python scripts/run_langgraph_workflow.py --help
python scripts/run_langgraph_workflow.py --dry-run --backend sequential
python scripts/run_langgraph_workflow.py --dry-run --backend langgraph
# ????????? 137+1 skip?? orchestration 138 passed
# python -m pytest -v
```

???**EXP-20260602-016**?2026-06-03?a6000-9961 @ `c0fa5e3`???? M4 pull ? langgraph backend ? `zip() argument 2 is shorter`?? [`mistakes.md`](../mistakes.md) **M-016**?

## ????Plus M5 ???/LLM?EXP-20260602-017/018 / EXP-LLM-001?

```bash
cd /mnt/localDisk3/weizian/Quant-MAS
git pull origin main   # ?? 43c812a?M-017 pytest ???
conda activate /mnt/localDisk3/weizian/conda_envs/quant-mas
python -m pip install -e .
python -m pip install -e ".[llm]"

python -m pytest tests/test_context_engineering.py -v   # 12 passed, 1 warning
python scripts/run_research_agent.py --help
python scripts/run_research_agent.py --task "Summarize OOS baseline vs latest ML run"
python -m pytest -v   # 150 passed?EXP-018?7.24s?? .env LLM_API_KEY?

# ?? LLM smoke?DeepSeek?key ? repo ? .env??????
python scripts/run_research_agent.py \
  --storage-config configs/storage.server.yaml \
  --json-path /mnt/localDisk3/weizian/reports/experiments.json \
  --task "Explain walk-forward OOS sharpe baseline and compare to latest ML run" \
  --use-llm
# ? EXP-LLM-001?llm_provider=openai_compatible?baseline oos.sharpe ? 0.586
```

???**EXP-20260602-018**?2026-06-03?a6000-9961 @ `43c812a`??**EXP-LLM-001**?DeepSeek smoke??`.env` ?? mock ????? [`mistakes.md`](../mistakes.md) **M-017**?

## ????Plus M6 ???? + Walk-forward?EXP-TEXT-001 / EXP-TEXT-WF-001??

```bash
cd /mnt/localDisk3/weizian/Quant-MAS
git pull origin main
conda activate /mnt/localDisk3/weizian/conda_envs/quant-mas
python -m pip install -e ".[ml,text]"
python -m pytest -v   # 161 passed

# ????? example ? ????
# cp configs/text_model.server.yaml.example configs/text_model.server.yaml
# cp configs/features.text.server.yaml.example configs/features.text.yaml

# FinBERT?Hub ????? ModelScope ?????? mistakes.md M-018?
python scripts/train_text_model.py --mode finbert_baseline \
  --config configs/text_model.server.yaml \
  --text-path data/text/smoke_from_features.jsonl \
  --output-dir /mnt/localDisk3/weizian/models/text/exp_text_001 \
  --signals-output /mnt/localDisk3/weizian/datasets/text/signals_finbert.parquet \
  2>&1 | tee /mnt/localDisk3/weizian/logs/exp_text_001_finbert.log

python scripts/build_features.py \
  --config configs/features.text.yaml \
  --storage-config configs/storage.server.yaml \
  --input /mnt/localDisk3/weizian/datasets/raw/market_data.parquet \
  --output /mnt/localDisk3/weizian/datasets/features/features_with_text.parquet
# fillna(0) on finbert_sentiment if sparse ? see text_model_plan.md

python scripts/run_walk_forward.py \
  --config configs/walk_forward.yaml \
  --storage-config configs/storage.server.yaml \
  --features-path /mnt/localDisk3/weizian/datasets/features/features_with_text.parquet \
  --experiment-name server_walk_forward_text_001 \
  --output-dir /mnt/localDisk3/weizian/reports/walk_forward_text_001

python scripts/compare_experiments.py \
  --storage-config configs/storage.server.yaml \
  --memory-path /mnt/localDisk3/weizian/reports/experiments.json \
  --output-dir /mnt/localDisk3/weizian/reports/research
```

**EXP-TEXT-WF-001 ??**?oos.sharpe **0.563** vs baseline **0.586**?? -0.023??200/6033 text ?? + fillna(0)?exploratory?

**EXP-TEXT-WF-002 ??**?oos.sharpe **0.579** vs baseline **0.586**?? **-0.007**??100% ?? + `feature_aligned_smoke` ?????19 ??comparison **7 rows**?

**??**???? `market_data.parquet` ?????? **M-019**???? `merge_parquet.py` ?? 6033 ??

???**EXP-20260602-020**?pytest 161??**EXP-TEXT-001**?**EXP-TEXT-WF-001**?

?? [`docs/text_model_plan.md`](text_model_plan.md)?

### EXP-TEXT-WF-002???????? + ????? + Walk-forward ?

**??**?`signals_finbert_wf002.parquet` ????? 1 ???**??**???????? `/path/to/...`?  
??? EXP-TEXT-001 ??? baseline ????? 0??????? wf002 ???

```bash
cd /mnt/localDisk3/weizian/Quant-MAS
git pull origin main
conda activate /mnt/localDisk3/weizian/conda_envs/quant-mas
python -m pip install -e ".[ml,text]"
python -m pytest -v   # ?? 314 passed

# 0) ????? EXP-TEXT-001 ?????baseline ??? ~200/6033?
python scripts/audit_text_signals.py \
  --features-path /mnt/localDisk3/weizian/datasets/features/features.parquet \
  --signals-path /mnt/localDisk3/weizian/datasets/text/signals_finbert.parquet \
  --output-dir /mnt/localDisk3/weizian/reports/text_signal_audit_wf001

# 1) ????????????????wf002 ????????????
# CLI ???--text-path??? JSONL??--signals-output??? parquet??--output-dir???????
# ?????????--records-path / --output-path
#
# 1a) ????????????????? 1b?
ls -la /mnt/localDisk3/weizian/datasets/text/news_wf002.jsonl
ls -la data/text/smoke_from_features.jsonl   # EXP-TEXT-001 ?? 200 ? smoke
#
# 1b) ? news_wf002.jsonl ?????? features ???????? JSONL?6033 ? × 3 symbol?
python scripts/build_text_records_from_features.py \
  --features-path /mnt/localDisk3/weizian/datasets/features/features.parquet \
  --output-path /mnt/localDisk3/weizian/datasets/text/news_wf002.jsonl \
  2>&1 | tee /mnt/localDisk3/weizian/logs/exp_text_wf002_build_records.log
#
# ??????? signals_finbert_wf002.parquet????? EXP-TEXT-001 ??
python scripts/train_text_model.py --mode finbert_baseline \
  --config configs/text_model.server.yaml \
  --text-path /mnt/localDisk3/weizian/datasets/text/news_wf002.jsonl \
  --output-dir /mnt/localDisk3/weizian/models/text/exp_text_wf002 \
  --signals-output /mnt/localDisk3/weizian/datasets/text/signals_finbert_wf002.parquet \
  2>&1 | tee /mnt/localDisk3/weizian/logs/exp_text_wf002_finbert.log

# 2) ??????????? OOS
python scripts/audit_text_signals.py \
  --features-path /mnt/localDisk3/weizian/datasets/features/features.parquet \
  --signals-path /mnt/localDisk3/weizian/datasets/text/signals_finbert_wf002.parquet \
  --output-dir /mnt/localDisk3/weizian/reports/text_signal_audit_wf002 \
  2>&1 | tee /mnt/localDisk3/weizian/logs/exp_text_wf002_audit.log

# 3) ???? signals ?? features_with_text_wf002.parquet
# ? configs/features.text.yaml ? text_signals_path ?? signals_finbert_wf002.parquet
python scripts/build_features.py \
  --config configs/features.text.yaml \
  --storage-config configs/storage.server.yaml \
  --input /mnt/localDisk3/weizian/datasets/raw/market_data.parquet \
  --output /mnt/localDisk3/weizian/datasets/features/features_with_text_wf002.parquet

# 4) ??? walk-forward ???? EXP-20260602-008 baseline 0.586
python scripts/run_walk_forward.py \
  --config configs/walk_forward.yaml \
  --storage-config configs/storage.server.yaml \
  --features-path /mnt/localDisk3/weizian/datasets/features/features_with_text_wf002.parquet \
  --experiment-name server_walk_forward_text_002 \
  --output-dir /mnt/localDisk3/weizian/reports/walk_forward_text_002

python scripts/compare_experiments.py \
  --storage-config configs/storage.server.yaml \
  --memory-path /mnt/localDisk3/weizian/reports/experiments.json \
  --output-dir /mnt/localDisk3/weizian/reports/research
```

?????

- `text_signal_audit_wf002/metrics.json`????? `coverage_ratio`?`matched_rows`?`matched_symbol_count`
- `walk_forward_text_002/metrics.json`???? `oos.*`??? **0.586** ??
- ? coverage ??? WF-001 ? `200/6033`??????? exploratory
- `simulation.*`?LLM ??????????? OOS

### EXP-TEXT-WF-003??????? JSONL + ???? ?

**???2026-06-04?**?fetch **9434** ? align **5088** ? FinBERT **146** signals ? coverage **2.42%** ? **oos.sharpe 0.565**?? vs baseline **-0.021**???? [real_news_text_experiment.md](real_news_text_experiment.md)?

**??**?`real_news_wf003.jsonl` ??**????**?? `published_at` ?????**??**? `docs/examples/real_news_wf003.sample.jsonl`?? schema ?????? OOS????? Finnhub???? `.env` ?? `FINNHUB_API_KEY`??

JSONL schema example: [`docs/examples/real_news_wf003.sample.jsonl`](examples/real_news_wf003.sample.jsonl).

```bash
cd /mnt/localDisk3/weizian/Quant-MAS
git pull origin main
conda activate /mnt/localDisk3/weizian/conda_envs/quant-mas
python -m pip install -e ".[ml,text]"
python -m pytest tests/test_text_signals.py -v   # ?? 31 passed
python -m pytest -v   # ?? 330 passed????

# 0) ? Finnhub ??????
# ??? company-news ?????? 1 ??--start 2018-01-01 ? raw=0
# ????2026-06-04??--start 2025-06-04 --end 2026-06-04 -> 9434 ?
python scripts/fetch_real_news.py \
  --source finnhub \
  --symbols AAPL MSFT SPY \
  --start 2025-06-04 \
  --end 2026-06-04 \
  --chunk-months 1 \
  --delay 1.0 \
  --output-path /mnt/localDisk3/weizian/datasets/text/real_news_wf003.jsonl \
  2>&1 | tee /mnt/localDisk3/weizian/logs/exp_text_wf003_fetch_news.log
# ?????--recent-days 365????????????????

# 1) ???????????????? bar
python scripts/align_real_news.py \
  --news-path /mnt/localDisk3/weizian/datasets/text/real_news_wf003.jsonl \
  --features-path /mnt/localDisk3/weizian/datasets/features/features.parquet \
  --output-dir /mnt/localDisk3/weizian/reports/real_news_alignment_wf003 \
  --market-close 16:00

# 2) ???? JSONL ?? FinBERT ????
python scripts/train_text_model.py --mode finbert_baseline \
  --config configs/text_model.server.yaml \
  --text-path /mnt/localDisk3/weizian/reports/real_news_alignment_wf003/aligned_news.jsonl \
  --output-dir /mnt/localDisk3/weizian/models/text/exp_text_wf003 \
  --signals-output /mnt/localDisk3/weizian/datasets/text/signals_finbert_wf003.parquet

# 3) ?????
python scripts/audit_text_signals.py \
  --features-path /mnt/localDisk3/weizian/datasets/features/features.parquet \
  --signals-path /mnt/localDisk3/weizian/datasets/text/signals_finbert_wf003.parquet \
  --output-dir /mnt/localDisk3/weizian/reports/text_signal_audit_wf003

# 4) ?? text-enhanced features?????? fillna(0)?? WF-001 ???
# configs/features.text.yaml ???text_signal_fillna: 0
python scripts/build_features.py \
  --config configs/features.text.yaml \
  --storage-config configs/storage.server.yaml \
  --input /mnt/localDisk3/weizian/datasets/raw/market_data.parquet \
  --output /mnt/localDisk3/weizian/datasets/features/features_with_text_wf003.parquet

python scripts/run_walk_forward.py \
  --config configs/walk_forward.yaml \
  --storage-config configs/storage.server.yaml \
  --features-path /mnt/localDisk3/weizian/datasets/features/features_with_text_wf003.parquet \
  --experiment-name server_walk_forward_text_003 \
  --output-dir /mnt/localDisk3/weizian/reports/walk_forward_text_003

python scripts/compare_experiments.py \
  --storage-config configs/storage.server.yaml \
  --memory-path /mnt/localDisk3/weizian/reports/experiments.json \
  --output-dir /mnt/localDisk3/weizian/reports/research
```

????????? fetch record_count?alignment dropped rows?coverage ratio?OOS sharpe??? **0.586** baseline?WF-002 **0.579**?WF-001 **0.563** ???

## ????Plus M7 RL ???EXP-20260602-021 / EXP-20260602-022??

```bash
cd /mnt/localDisk3/weizian/Quant-MAS
git pull origin main
conda activate /mnt/localDisk3/weizian/conda_envs/quant-mas
python -m pip install -e .
python -m pytest -v   # ?? 180 passed

python scripts/run_rl_baseline.py --help
python scripts/run_rl_baseline.py --config configs/rl.yaml --policy random --dry-run \
  --output-dir /mnt/localDisk3/weizian/reports/rl_baseline_001

# ?? policies: buy_hold | ml_copy?ml_copy ? --signals-path?
python scripts/run_rl_baseline.py --config configs/rl.yaml --policy buy_hold --dry-run
```

**??**?

- **simulation only** ? ?? broker?metrics ? `simulation.*`?**??**? walk-forward `oos.sharpe` **0.586** ??
- ???`pip install -e ".[rl]"` ?? gymnasium wrapper??? pytest ????
- ???**EXP-20260602-021**?????**EXP-20260602-022**???? **180 passed**?10.15s?

?? [`docs/rl_plan.md`](rl_plan.md)?

## ?????Plus M8 MCP/A2A?EXP-20260602-023 / EXP-20260602-024??

```bash
cd /mnt/localDisk3/weizian/Quant-MAS
git pull origin main
conda activate /mnt/localDisk3/weizian/conda_envs/quant-mas
python -m pip install -e .
python -m pytest -v   # ?? 195 passed

python scripts/export_agent_cards.py --help
python scripts/export_agent_cards.py --config configs/protocols.yaml \
  --output-dir /mnt/localDisk3/weizian/reports/protocols \
  --include-mcp-specs
```

**??**?

- **?? adapter only** ? ???? MCP server???? network listener
- policy ?? deny shell/broker/order/secrets
- ???**EXP-20260602-023**??? 195 passed??**EXP-20260602-024**???? **195 passed**?12.41s?

?? [`docs/protocols.md`](protocols.md)?

## ?????v3 M9 ?? DB?EXP-025 / EXP-026?

### 6.12.1 ????

| ? | ?? |
|----|------|
| Docker | weizian ? **docker ?**?`groups` ? `docker`?????? **?? SSH ??**? |
| infra | `/mnt/localDisk3/weizian/infra/quant-mas-db/`?compose + `setup.sh` + `.env`? |
| ?? | `POSTGRES_DSN` ? `Quant-MAS/.env`?? infra `.env` ???**? commit**? |
| ?? | `origin/main` ? M10?**212 pytest**?? `seed_postgres_from_json.py`? |
| Python | conda `quant-mas`?`psycopg[binary]>=3.1` |

### 6.12.2 ?? Postgres + pgvector

```bash
# 0) ?? docker ?????????????
groups | tr ' ' '\n' | grep -x docker && echo "docker OK"

# 1) ????????
bash /mnt/localDisk3/weizian/infra/quant-mas-db/setup.sh

# ????
# cd /mnt/localDisk3/weizian/infra/quant-mas-db
# docker compose up -d postgres
# docker exec quant-mas-postgres psql -U quant_mas -d quant_mas \
#   -c "CREATE EXTENSION IF NOT EXISTS vector;"

# 2) ???????
docker ps --filter name=quant-mas-postgres
ss -ltn | grep 5432 || true
docker exec quant-mas-postgres psql -U quant_mas -d quant_mas -c "SELECT extname FROM pg_extension WHERE extname='vector';"
```

?? Neo4j?`cd /mnt/localDisk3/weizian/infra/quant-mas-db && docker compose --profile neo4j up -d neo4j`

### 6.12.3 ??? + pytest?? DB ???

```bash
cd /mnt/localDisk3/weizian/Quant-MAS
git fetch origin main
git merge --ff-only origin/main   # ???d10a641+?212 pytest + seed ???

conda activate /mnt/localDisk3/weizian/conda_envs/quant-mas
python -m pip install -e .
python -m pip install "psycopg[binary]>=3.1" neo4j
python -m pytest -v   # ?? 212 passed
```

### 6.12.4 EXP-026 ?? DB smoke

```bash
cd /mnt/localDisk3/weizian/Quant-MAS
conda activate /mnt/localDisk3/weizian/conda_envs/quant-mas
set -a && source .env && set +a   # ?? POSTGRES_DSN

# A) ???? experiments.json ?? Postgres?????????? --skip-existing?
python scripts/seed_postgres_from_json.py \
  --json-path /mnt/localDisk3/weizian/reports/experiments.json

# B) ? best OOS?????? walk-forward OOS???? ML?
python scripts/query_memory.py --backend postgres --best-metric oos.sharpe
# ???? oos.sharpe ? 0.586 ? baseline ???

# C) pgvector ?? docs
python scripts/index_documents.py --vector-store pgvector --dirs docs --embedding-dimensions 64
# ???[index] documents=? chunks=???? 100+ chunks?

# D) SQL ??????
docker exec quant-mas-postgres psql -U quant_mas -d quant_mas \
  -c "SELECT COUNT(*) FROM experiments;"
docker exec quant-mas-postgres psql -U quant_mas -d quant_mas \
  -c "SELECT COUNT(*) FROM rag_vectors;"
```

**??**?

- pytest ?? mock?**???**?? Postgres / vLLM
- `--best-metric oos.sharpe` ?? Postgres ??????? ? ?? **seed**??? JSON ???????????????? `reports/experiments.json`?
- ???**EXP-025** ?? 207?**EXP-027/028** 212?**EXP-LLM-002** ??**EXP-026** ??2026-06-03?6 exp, 443 chunks, OOS 0.586 @ `02bdb8a`?

?? [`docs/database_setup.md`](database_setup.md) §M9 · [`docs/context_engineering.md`](context_engineering.md) M10?

## ?????v3 M10 LLM?EXP-027 / EXP-028 / EXP-LLM-002??

### 6.13.1 pytest?mock??? vLLM?

```bash
cd /mnt/localDisk3/weizian/Quant-MAS
conda activate /mnt/localDisk3/weizian/conda_envs/quant-mas
python -m pytest tests/test_context_engineering.py -v   # 17 passed
python -m pytest -v                                     # 212 passed
```

???**EXP-20260602-027**??? 212??**EXP-20260602-028**???? 212?11.39s??

### 6.13.2 vLLM ????? conda???? quant-mas?

```bash
# ????????
conda create -p /mnt/localDisk3/weizian/conda_envs/vllm python=3.11 -y
conda activate /mnt/localDisk3/weizian/conda_envs/vllm
pip install vllm
which vllm   # ??? .../conda_envs/vllm/bin/vllm??? ~/.local/bin/vllm
```

**??**???????? huggingface.co ???????????

```bash
export HF_ENDPOINT=https://hf-mirror.com
huggingface-cli download Qwen/Qwen2.5-7B-Instruct \
  --local-dir /mnt/localDisk3/weizian/models/Qwen2.5-7B-Instruct \
  --local-dir-use-symlinks False
```

**??**?

| ?? | ?? |
|------|------|
| `Network is unreachable`?HF? | ???? + ???? serve |
| FlashInfer / CUDA 12 ???? | `export VLLM_USE_FLASHINFER_SAMPLER=0` |
| `vllm: command not found` | ? `conda activate .../vllm` |
| GPU OOM?3GB free? | ? vLLM ?? GPU 0?`pkill -f "vllm serve"` ? `kill <EngineCore PID>` |
| ?? `VLLM_USE_FLASHINFER` | v0.22 ???? **`VLLM_USE_FLASHINFER_SAMPLER=0`** |

### 6.13.3 ?? vLLM??? 1??? tmux?

```bash
tmux new -s vllm
conda activate /mnt/localDisk3/weizian/conda_envs/vllm

export HF_HUB_OFFLINE=1
export VLLM_USE_FLASHINFER_SAMPLER=0
unset VLLM_BASE_URL VLLM_MODEL VLLM_USE_FLASHINFER

CUDA_VISIBLE_DEVICES=0 vllm serve /mnt/localDisk3/weizian/models/Qwen2.5-7B-Instruct \
  --host 127.0.0.1 --port 8000 --dtype auto --max-model-len 8192 \
  --served-model-name Qwen/Qwen2.5-7B-Instruct --enforce-eager
# ?? Application startup complete?Ctrl+B D detach
```

### 6.13.4 ResearchAgent smoke??? 2?EXP-LLM-002?

```bash
conda activate /mnt/localDisk3/weizian/conda_envs/quant-mas
cd /mnt/localDisk3/weizian/Quant-MAS

curl -s http://127.0.0.1:8000/v1/models | python -m json.tool

export VLLM_BASE_URL=http://127.0.0.1:8000
export VLLM_MODEL=Qwen/Qwen2.5-7B-Instruct

mkdir -p /mnt/localDisk3/weizian/reports/llm

python scripts/run_research_agent.py \
  --provider local_vllm --use-llm \
  --task "Interpret ONLY the walk-forward OOS baseline EXP-20260602-008 (oos.sharpe ? 0.586). Do NOT treat workflow_ml_backtest, single-segment ML sharpe, or pytest milestones as paper metrics. List three research risks." \
  --experiment-name walk-forward \
  --rag-query "OOS baseline EXP-20260602-008 sharpe 0.586" \
  --output-json /mnt/localDisk3/weizian/reports/llm/EXP-LLM-002-constrained.json
```

???`llm_provider=local_vllm`?RAG ?? `experiment_log.md`?**?**??? ML sharpe ??????

???**EXP-LLM-002** ??2026-06-03?Qwen2.5-7B-Instruct @ GPU 0?vLLM 0.22.0??

## ?????v3 M11 ?????EXP-029 / EXP-POP-002??

### 6.14.1 ??? + pytest

```bash
cd /mnt/localDisk3/weizian/Quant-MAS
git fetch origin main
git merge --ff-only origin/main   # ???? M11?225 pytest

conda activate /mnt/localDisk3/weizian/conda_envs/quant-mas
python -m pip install -e .
python -m pytest tests/test_population_training.py -v   # 13 passed
python -m pytest -v                                     # ?? 225 passed
```

### 6.14.2 competitive mock dry-run

```bash
python scripts/run_competitive_experiment.py --help

python scripts/run_competitive_experiment.py \
  --config configs/competitive.yaml \
  --mode mock \
  --dry-run
```

**??**?

- `--dry-run` ? stdout??? ExperimentMemory / artifacts
- ??? `population.*` / `simulation.*`?**??**? OOS **0.586** ??
- ???**EXP-20260602-029** ?? 225?**EXP-POP-002** ? ??? **225 passed**?17.32s?+ dry-run?2026-06-03 @ `64a5b2a`?

?? [`docs/competitive_learning.md`](competitive_learning.md)?

## ?????v3 M11.5 ???????EXP-030 / EXP-POP-003??

### 6.15.1 ??? + pytest

```bash
cd /mnt/localDisk3/weizian/Quant-MAS
git fetch origin main
git merge --ff-only origin/main   # ???? M11.5?237 pytest

conda activate /mnt/localDisk3/weizian/conda_envs/quant-mas
python -m pip install -e .
python -m pytest tests/test_population_training_loop.py -v   # 12 passed
python -m pytest -v                                             # ?? 237 passed
```

### 6.15.2 population training dry-run

```bash
python scripts/run_population_training.py --help

python scripts/run_population_training.py \
  --config configs/population_training.yaml \
  --dry-run
```

? dry-run ?? `outputs/population_training/` ? ExperimentMemory??? `population.*` / `simulation.*`??

- ???**EXP-20260602-030** ?? 237?**EXP-POP-003** ? ??? **237 passed**?41.83s?+ training dry-run?2026-06-03 @ `aa841d4`?

?? [`docs/population_training.md`](population_training.md)?

## ?????v3 M11.6 ??????EXP-031 / EXP-POP-004??

### 6.16.1 ??? + pytest

```bash
cd /mnt/localDisk3/weizian/Quant-MAS
git fetch origin main
git merge --ff-only origin/main   # ???? M11.6?248 pytest

conda activate /mnt/localDisk3/weizian/conda_envs/quant-mas
python -m pip install -e .
python -m pytest tests/test_strategy_candidate_bridge.py -v   # 11 passed
python -m pytest -v                                             # ?? 248 passed
```

### 6.16.2 export candidates + backtest smoke dry-run

```bash
python scripts/export_population_candidates.py --help

python scripts/export_population_candidates.py \
  --population-config configs/population_training.yaml \
  --top-k 2 \
  --run-backtest-smoke \
  --dry-run
```

**??**?

- `--dry-run` ? stdout??? ExperimentMemory / artifacts
- ??? `population.*` / `simulation.*` / `backtest.*`?**??**???? `oos.*`?????? **0.586**?
- `--run-walk-forward` ???? stub???? OOS ??
- ???**EXP-20260602-031** ?? 248?**EXP-POP-004** ? ??? **248 passed**?55.15s?bridge 2.48s?+ export dry-run?2026-06-03 @ `7ab510f`?

?? [`docs/strategy_candidate_bridge.md`](strategy_candidate_bridge.md)?

## ?????v3 M11.7 ?? Walk-forward OOS?EXP-032 / EXP-POP-005??

### 6.17.1 ??? + pytest

```bash
cd /mnt/localDisk3/weizian/Quant-MAS
git fetch origin main
git merge --ff-only origin/main   # ???? M11.7?259 pytest

conda activate /mnt/localDisk3/weizian/conda_envs/quant-mas
python -m pip install -e .
python -m pytest tests/test_candidate_oos_validation.py -v   # 11 passed
python -m pytest -v                                             # ?? 259 passed
```

### 6.17.2 ?? features ?? candidate OOS

??????M11.6???**?? `--no-dry-run`** ???? `outputs/candidates/candidates.json`?

```bash
python scripts/export_population_candidates.py \
  --population-config configs/population_training.yaml \
  --top-k 2 \
  --run-backtest-smoke \
  --no-dry-run
```

???????

```bash
ls -la outputs/candidates/candidates.json
```

**??? features ??**?? repo ? `data/features/`?? walk-forward EXP-008 ????

```bash
FEATURES=/mnt/localDisk3/weizian/datasets/features/features.parquet
ls -la "$FEATURES"   # ?????? 6033 rows
```

?? walk-forward OOS?M11.7??

```bash
python scripts/validate_candidate_oos.py --help

python scripts/validate_candidate_oos.py \
  --candidate-json outputs/candidates/candidates.json \
  --candidate-id cand_mean_rev_1 \
  --features-path /mnt/localDisk3/weizian/datasets/features/features.parquet \
  --config configs/candidate_oos.yaml \
  --storage-config configs/storage.yaml \
  --dry-run

# ? dry-run ? artifacts + ExperimentMemory
python scripts/validate_candidate_oos.py \
  --candidate-json outputs/candidates/candidates.json \
  --candidate-id cand_mean_rev_1 \
  --features-path /mnt/localDisk3/weizian/datasets/features/features.parquet \
  --config configs/candidate_oos.yaml \
  --no-dry-run
```

**??**?

- **M11.7 ???**????????? `oos.*` ???
- ?? baseline?**EXP-20260602-008**?`oos.sharpe = 0.586`
- ???**EXP-20260602-032** ?? mock?**EXP-POP-005** ? ??? `cand_mean_rev_1` **oos.sharpe 1.036**?77 ??2019-07?2025-12?vs ML baseline **0.586**?2026-06-04 @ `ffef849`?

?? [`docs/strategy_candidate_oos.md`](strategy_candidate_oos.md)?

## ?????v3 M11.8 ???? OOS?EXP-033 / EXP-POP-006??

```bash
cd /mnt/localDisk3/weizian/Quant-MAS
conda activate /mnt/localDisk3/weizian/conda_envs/quant-mas
git pull origin main   # ???? M11.8?266 pytest

python -m pytest -v    # ?? 266 passed

# ?? candidates.json????
python scripts/export_population_candidates.py \
  --population-config configs/population_training.yaml \
  --top-k 5 \
  --run-backtest-smoke \
  --no-dry-run

python scripts/batch_validate_candidates.py \
  --candidate-json outputs/candidates/candidates.json \
  --features-path /mnt/localDisk3/weizian/datasets/features/features.parquet \
  --config configs/candidate_oos.yaml \
  --top-k 5 \
  --no-dry-run
```

**??**?

- ?? M11.7 `run_candidate_walk_forward`??? `candidate_oos_comparison.csv` / `.md`
- ?? baseline?**EXP-20260602-008**?`oos.sharpe = 0.586`
- ???**EXP-20260602-033** ???**EXP-POP-006** ? ??? 4 ???? baseline?best **1.039**?2026-06-04 @ `9477c3d`?
- ?? **ablation / ????**???? ML ? baseline

?? [`docs/candidate_oos_batch.md`](candidate_oos_batch.md)?

## ?????v3 M12.1 RL Training Loop?EXP-034 / EXP-POP-007??

```bash
cd /mnt/localDisk3/weizian/Quant-MAS
conda activate /mnt/localDisk3/weizian/conda_envs/quant-mas
git pull origin main   # ???? M12.1?282 pytest ??

python -m pytest -v    # ?? 282 passed

python scripts/run_rl_experiment.py --help

python scripts/run_rl_experiment.py \
  --config configs/rl_training.yaml \
  --algorithm grpo \
  --max-steps 10 \
  --dry-run

python scripts/run_rl_experiment.py \
  --config configs/rl_training.yaml \
  --algorithm grpo \
  --max-steps 50 \
  --no-dry-run
```

**??**?

- **simulation only**?metrics ? `training.*` / `simulation.*`?**??**?? OOS
- ?? baseline ????/summary ?? **EXP-20260602-008** `oos.sharpe = 0.586`
- ???**EXP-20260602-034** ?? ??**EXP-POP-007** / **EXP-RL-003** ? ??? GRPO smoke?2026-06-04 @ `e291cf9`?**simulation only**?
- OOS ??????M11.6 export ? M11.7/M11.8 validate

?? [`docs/rl_experiment.md`](rl_experiment.md)?

## ?????v3 M12.2 RL Policy Export?EXP-035 / EXP-POP-008??

```bash
cd /mnt/localDisk3/weizian/Quant-MAS
conda activate /mnt/localDisk3/weizian/conda_envs/quant-mas
git pull origin main   # ? M12.2+?296 pytest

python -m pytest -v    # ?? 296 passed

python scripts/export_rl_policy_candidate.py \
  --config configs/rl_policy_export.yaml \
  --no-dry-run
```

**??**?

- M12.2 **? export** `StrategyCandidate`?`source=rl_training`??**?? oos.***
- ???**EXP-20260602-035** ?? ??**EXP-POP-008** ??? ??`e7fea132af8a451ba9c999762d220ee6`?`rl_grpo_policy_001_1`?

?? [`docs/rl_policy_export.md`](rl_policy_export.md)?

## ??????v3 M12.3 RL ?? Walk-forward OOS?EXP-POP-009??

???**EXP-POP-008** ??? `outputs/rl_candidates/candidates.json`?

```bash
python scripts/validate_candidate_oos.py \
  --candidate-json outputs/rl_candidates/candidates.json \
  --features-path /mnt/localDisk3/weizian/datasets/features/features.parquet \
  --config configs/candidate_oos.yaml \
  --no-dry-run
```

**?????**?2026-06-04 @ `6e8c507`??

| ?? | ? | ?? |
|------|-----|------|
| `candidate_id` | `rl_grpo_policy_001_1` | EXP-POP-008 ?? |
| `window_count` | **77** | ? population OOS ??? |
| `oos.sharpe` | **0.0** | argmax logit ? `target_weight=0.0`????? |
| `vs_baseline_sharpe` | **-0.586** | ?? EXP-008 **0.586** |
| `simulation.sharpe_mean` | **6.31** | M12.1 ???**????? OOS** |

- ???**EXP-POP-009** ??**296 passed** in **45.05s**
- ???`outputs/candidate_oos/`?metrics.json?windows.csv?oos_equity_curve.csv?

## ??????v3 M12.4 Observation-Aware RL Policy?EXP-036 / EXP-POP-010??

???`git pull` ? M12.4??? **308 pytest**??

```bash
cd /mnt/localDisk3/weizian/Quant-MAS
conda activate /mnt/localDisk3/weizian/conda_envs/quant-mas

python -m pytest -v    # ?? 308 passed

python scripts/run_rl_experiment.py \
  --config configs/rl_training.yaml \
  --policy-type feature_linear \
  --algorithm grpo \
  --max-steps 50 \
  --no-dry-run

python scripts/export_rl_policy_candidate.py \
  --config configs/rl_policy_export.yaml \
  --no-dry-run

python scripts/validate_candidate_oos.py \
  --candidate-json outputs/rl_candidates/candidates.json \
  --features-path /mnt/localDisk3/weizian/datasets/features/features.parquet \
  --config configs/candidate_oos.yaml \
  --no-dry-run
```

**??**?

- M12.4 ???? `training.*` / `simulation.*`?OOS ? M11.7 ? `oos.*`
- ? EXP-POP-009?logits ??? `oos.sharpe=0.0`????feature_linear ???**???** `target_weight`
- ???**EXP-20260602-036** ?? ??**EXP-POP-010** ??? ??`rl_feature_linear_policy_001_1` **oos.sharpe 0.387** vs baseline **0.586**?

?? [`docs/rl_observation_policy.md`](rl_observation_policy.md)?

## ??????????? ~/quant-mas ???

```bash
rm -rf ~/quant-mas
# conda ???????conda env remove -n quant-mas -y
```

## ???? ? ??????

| ?? | ?? Windows | ??? |
|------|-------------|--------|
| ??? | Codex | ? |
| ?? | `python -m pytest -v` | `conda activate quant-mas && python -m pytest -v` |
| ??/?? | `git push` | `git pull` |

?????

```powershell
cd "D:\scientific reasearch and work\SRTP\Quant MAS"
git add .
git commit -m "your message"
git push origin main
```

## M13 ???M13.0 ? · M13.1 ??

### M13.0 smoke?EXP-M13-001??? 342 pytest?

```bash
cd /mnt/localDisk3/weizian/Quant-MAS
git pull origin main
conda activate /mnt/localDisk3/weizian/conda_envs/quant-mas
python -m pytest -v                              # ?? 349 passed
python -m pytest tests/test_mcp_scheduler.py -v  # 11 passed
python -m pytest tests/test_mcp_pipeline_recipes.py -v  # 7 passed

python scripts/run_mcp_pipeline.py --list-recipes
python scripts/run_mcp_pipeline.py --recipe mock_research --dry-run
python scripts/run_mcp_pipeline.py --recipe text_smoke --dry-run
```

### M13.1 YAML recipe dry-run?EXP-M13-002??? ? · ???? smoke?

```bash
python scripts/run_mcp_pipeline.py --recipe configs/pipelines/ml_baseline.yaml.example --dry-run
python scripts/run_mcp_pipeline.py --recipe configs/pipelines/text_enhanced.yaml.example --dry-run
python scripts/run_mcp_pipeline.py --recipe configs/pipelines/population_oos.yaml.example --dry-run
python scripts/run_mcp_pipeline.py --recipe configs/pipelines/rl_ablation.yaml.example --dry-run
```

???`outputs/pipelines/<run_id>/audit.jsonl`

???

- ? dry-run??? GPU / ?? / LLM / ?? walk-forward
- `ToolPolicy` ?? deny shell / broker / order / secrets
- ???? OOS ????
- `text_enhanced`?`audit_text_signals` ??? `walk_forward_eval` ?

?? [mcp_protocol.md](mcp_protocol.md)?????**M13.2** ?????? YAML smoke?
