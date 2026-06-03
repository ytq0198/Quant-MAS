# Context Engineering and LLM Access

Updated: 2026-06-03  
Scope: Plus M5 context layer, M6 text-signal boundary, and v3 M10 LLM productionization.

Quant MAS keeps the Quant Engine deterministic. LLM agents read structured context,
generate hypotheses, explain results, and draft reports. They must not place orders,
emit broker instructions, create target weights, or overwrite Quant Engine metrics.

## Positioning

| Layer | Responsibility | Can Change Metrics? |
| --- | --- | --- |
| Quant Engine | Data, features, models, backtests, risk, walk-forward OOS | Yes, through deterministic runs |
| ContextBuilder | Memory/RAG/workflow state to bounded `AgentContextBundle` | No |
| ResearchAgent / ReportAgent | Narrative, hypotheses, caveats, next experiments | No |

Paper-level evidence should use walk-forward OOS metrics. Current baseline reference:
`EXP-20260602-008`, `oos.sharpe = 0.586`.

## Architecture

```text
ExperimentMemory / Workflow State / RAG
        -> ContextBuilder -> AgentContextBundle -> compression
        -> ResearchAgent / ReportAgent
        -> resolve_llm_client(use_llm=...)
        -> MockLLMClient | OpenAICompatibleLLMClient | LocalVLLMClient
```

| Module | Path |
| --- | --- |
| Context schema | `src/quant_mas/context/context_schema.py` |
| Context builder | `src/quant_mas/context/context_builder.py` |
| Compression | `src/quant_mas/context/compression.py` |
| LLM boundary | `src/quant_mas/core/llm.py` |
| ResearchAgent | `src/quant_mas/agents/research_agent.py` |
| ReportAgent | `src/quant_mas/agents/report_agent.py` |

## LLM Providers

| Provider | Environment | Use Case |
| --- | --- | --- |
| `mock` | none | pytest, offline development, default behavior |
| `openai_compatible` | `LLM_API_KEY`, `LLM_BASE_URL`, `LLM_MODEL` | DeepSeek cloud smoke (`EXP-LLM-001`) |
| `local_vllm` | `VLLM_BASE_URL`, `VLLM_MODEL`, optional `VLLM_API_KEY` | A6000 local vLLM OpenAI-compatible endpoint |

Default behavior is safe:

- `resolve_llm_client(use_llm=False)` always returns `MockLLMClient`.
- `openai_compatible` without `LLM_API_KEY` warns and falls back to Mock.
- `local_vllm` without `VLLM_BASE_URL` warns and falls back to Mock.
- pytest must mock HTTP and never call DeepSeek, vLLM, or Hugging Face.

## Environment

Keep real secrets only in `.env`; never commit them.

```env
LLM_PROVIDER=mock
LLM_BASE_URL=https://api.deepseek.com
LLM_API_KEY=
LLM_MODEL=deepseek-chat
LLM_TIMEOUT_SECONDS=60

VLLM_BASE_URL=
VLLM_MODEL=
VLLM_API_KEY=
```

Server-side vLLM example (a6000, verified **EXP-LLM-002**):

```bash
# Terminal 1 — vLLM service (conda env vllm, NOT quant-mas)
conda activate /mnt/localDisk3/weizian/conda_envs/vllm
export HF_HUB_OFFLINE=1
export VLLM_USE_FLASHINFER_SAMPLER=0   # required on CUDA 11 hosts

CUDA_VISIBLE_DEVICES=0 vllm serve /mnt/localDisk3/weizian/models/Qwen2.5-7B-Instruct \
  --host 127.0.0.1 --port 8000 --dtype auto --max-model-len 8192 \
  --served-model-name Qwen/Qwen2.5-7B-Instruct --enforce-eager

# Terminal 2 — Quant-MAS client
conda activate /mnt/localDisk3/weizian/conda_envs/quant-mas
export VLLM_BASE_URL=http://127.0.0.1:8000
export VLLM_MODEL=Qwen/Qwen2.5-7B-Instruct

python scripts/run_research_agent.py \
  --provider local_vllm --use-llm \
  --task "Interpret ONLY walk-forward OOS baseline EXP-20260602-008 (oos.sharpe ≈ 0.586)." \
  --rag-query "OOS baseline EXP-20260602-008 sharpe 0.586"
```

Full setup (model mirror download, FlashInfer workaround, GPU OOM): [`server_commands.md`](server_commands.md) §6.13.

DeepSeek cloud example:

```bash
export LLM_PROVIDER=openai_compatible
export LLM_BASE_URL=https://api.deepseek.com
export LLM_MODEL=deepseek-chat
export LLM_API_KEY=<set in private .env>

python scripts/run_research_agent.py \
  --task "Summarize OOS baseline" \
  --use-llm \
  --provider openai_compatible
```

## M6 Text Boundary

M10 does not replace the M6 text-signal path.

- `scripts/train_text_model.py` produces structured text signals.
- `src/quant_mas/features/text_signals.py` merges those signals into feature tables.
- LoRA in `src/quant_mas/text/lora_finetune.py` is a server-side skeleton; pytest uses mock mode and does not download HF weights.
- Text signals must still go through LightGBM or other deterministic models, walk-forward OOS, risk checks, and `compare_experiments`.
- LLM narration does not perform `merge_text_signals_into_features` and does not participate in Sharpe or AUC calculation.

Known exploratory result: `EXP-TEXT-WF-001` produced `oos.sharpe = 0.563` versus
baseline `0.586`, with limited text coverage. This is not a replacement for the
main OOS baseline.

## Local Validation

```bash
python -m pytest tests/test_context_engineering.py -v
python -m pytest -v
python scripts/run_research_agent.py --help
python scripts/generate_report.py --help
```

**EXP-LLM-002** ✅ (2026-06-03): server `local_vllm` smoke on a6000; `llm_provider=local_vllm`.
Use constrained tasks (OOS **0.586** only); Qwen may wrap JSON in markdown fences.
LLM narrative is non-authoritative — paper metric remains **oos.sharpe 0.586**.

