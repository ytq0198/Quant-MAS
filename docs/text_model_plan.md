# 金融文本模型计划（Plus M6）

更新时间：2026-06-03（M6 第一版本地 ✅ EXP-20260602-019）

> Codex 任务：[codex_prompt_M6.md](codex_prompt_M6.md) · 设计：[项目plus设计.md §M6](../项目plus设计.md#m6金融文本大模型--开源模型微调)

## 定位

M6 **不**用生成式 LLM / FinBERT **直接**预测价格或下单。路线：

```
FinancialTextRecord → sentiment/classifier → TextSignalRecord
    → merge_text_signals_into_features → LightGBM + walk-forward OOS
```

与 **M5 ResearchAgent**（DeepSeek 解释层）分离：M5 叙事，M6 结构化特征。

## 已交付（第一版，mock pytest）

| 组件 | 路径 |
|------|------|
| Schema | `src/quant_mas/text/data_schema.py` |
| 时间切分 | `src/quant_mas/text/dataset.py` |
| Mock 分类器 | `src/quant_mas/text/mock_classifier.py` |
| FinBERT 骨架 | `src/quant_mas/text/finbert_baseline.py` |
| LoRA 骨架 | `src/quant_mas/text/lora_finetune.py` |
| Feature merge | `src/quant_mas/features/text_signals.py` |
| CLI | `scripts/train_text_model.py` |
| 配置 | `configs/text_model.yaml` |
| 测试 | `tests/test_text_signals.py`（**11 passed**） |

**pytest 基线**：全量 **161 passed**（EXP-20260602-019）；核心安装不含 `torch` / `transformers`。

## 可选依赖

```bash
pip install -e ".[text]"   # transformers, peft, accelerate, torch
```

仅服务器手工 FinBERT / LoRA 训练时需要；CI 与默认 pytest **不安装**。

## 服务器验收（待做）

```bash
cd /mnt/localDisk3/weizian/Quant-MAS
git pull origin main
conda activate /mnt/localDisk3/weizian/conda_envs/quant-mas
python -m pip install -e .
python -m pytest -v                    # 预期 161 passed

# 可选 FinBERT smoke（EXP-TEXT-001）：
python -m pip install -e ".[text]"
nvidia-smi
python scripts/train_text_model.py --mode finbert_baseline --config configs/text_model.yaml
```

## 与 OOS baseline 对比流程

1. mock / FinBERT 生成 `signals.parquet`（`finbert_sentiment` 等列）
2. `merge_text_signals_into_features` 并入 feature table（**禁止 future text leakage**）
3. 重新训练 LightGBM 或 walk-forward pipeline（**不修改**默认无 text 路径行为）
4. `scripts/compare_experiments.py` 与 **EXP-20260602-008**（**oos.sharpe 0.586**）对比
5. 未跑 walk-forward **不得**写入 oos.sharpe 结论

## 待验证实验

| 编号 | 内容 | 状态 |
|------|------|------|
| EXP-TEXT-001 | 服务器 FinBERT baseline smoke | 待验证 |
| EXP-TEXT-002 | LoRA 小样本微调 | 待验证 |
| EXP-TEXT-WF-001 | text signal + walk-forward vs 0.586 | 待验证 |

## 环境变量（`.env`，不入库）

```env
HF_TOKEN=...
WANDB_API_KEY=...          # 可选
MODEL_CACHE_DIR=/mnt/localDisk3/weizian/models/hf
```

## 相关文档

- [architecture.md](architecture.md) — Text Signal Layer
- [experiment_log.md](experiment_log.md)
- [research_protocol.md](research_protocol.md) — OOS 主指标
