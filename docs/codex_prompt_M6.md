# Plus M6：金融文本大模型 / 文本信号 — Codex 提示词

**状态：✅ 已完成（本地 EXP-019 + 服务器 EXP-020 / EXP-TEXT-001 / EXP-TEXT-WF-001，161 passed，2026-06-03）**

更新时间：2026-06-03（含服务器 FinBERT + walk-forward OOS 对比）

> **用法**：先粘贴下方「固定前缀」，再粘贴「M6 主任务」整段交给 Codex。  
> **设计依据**：[项目plus设计.md §M6](../项目plus设计.md#m6金融文本大模型--开源模型微调) · 前置：**M1–M5 ✅**（EXP-20260602-018 / EXP-LLM-001）

---

## 固定前缀（每次必贴）

```
你正在开发 Quant MAS 科研项目。
路径：D:\scientific reasearch and work\SRTP\Quant MAS

测试基线：本地 + 服务器 **150 passed**（Plus M5，EXP-20260602-017/018）。
DeepSeek ResearchAgent smoke ✅（EXP-LLM-001，openai_compatible）。
OOS 主 baseline：EXP-20260602-008，oos.sharpe **0.586**。

硬性原则：
1. **文本模型不替代 LightGBM 做价格预测**；文本产出为 **text_signals** 特征，仍走结构化 ML + walk-forward OOS。
2. LLM / 文本模型 **不允许**直接实盘下单；不得输出 target_weight / 订单。
3. pytest **不联网、不下载 HuggingFace 权重、不加载真实 FinBERT/LoRA**；全部用 mock / synthetic 小样本。
4. **禁止未来新闻泄漏**：text signal 只能使用 `date <= bar_date` 的文本；merge 到 features 时须 assert 无 future join。
5. 请只实现当前 **M6** 一个模块；改完后 `python -m pytest -v` 全量通过（预期 150+，新增 test_text_signals）。
6. HF_TOKEN / WANDB 仅 `.env`；不要 commit 权重、大数据或 token。
7. 新实验结论须与 **EXP-20260602-008 OOS sharpe 0.586** 对比（M1 compare_experiments），不得用单段 ML sharpe 2.78。
```

---

## M6 主任务（复制给 Codex）

```
请为 Quant MAS v2 增加金融文本信号模块（Plus M6）。

## 背景

v1 / Plus 已有：
- features/pipelines.py — build_feature_table（OHLCV 技术指标 + future labels）
- models/training.py、lightgbm_model.py — 结构化方向模型
- walk_forward.py — OOS 主指标（EXP-20260602-008，oos.sharpe 0.586）
- M5 ResearchAgent — 解释/报告 LLM（DeepSeek），**与 M6 文本特征分离**
- data/fetchers/ — 行情数据；**尚无**新闻/财报文本 pipeline

M6 目标：**文本 → sentiment/分类 signal → 并入 features → 仍用 LightGBM + walk-forward 评估**。

## 目标

1. **Text Layer**：FinancialTextRecord schema、按时间切分 dataset、FinBERT baseline（mock 可测）。
2. **LoRA 骨架**：train_lora_text_classifier 接口 + config（pytest 不跑真实训练）。
3. **Feature 融合**：text_signals.py 将 signal 列 merge 进现有 feature parquet（按 symbol+date left join）。
4. **CLI**：train_text_model.py（--help + dry-run / mock mode）。
5. **可选依赖**：transformers / peft / accelerate 不进核心 pytest 硬依赖。

第一版重点：**mock pytest 全绿** + CLI help；真实 FinBERT/LoRA 训练仅服务器手工（EXP-TEXT-001/002）。

## 需要实现的文件

### 1. 包结构

src/quant_mas/text/
  __init__.py
  data_schema.py       # FinancialTextRecord, TextSignalRecord
  dataset.py           # 按时间切分 train/val/test；禁止 shuffle 穿越
  finbert_baseline.py  # predict_sentiment(texts) -> scores；可注入 mock classifier
  lora_finetune.py     # train_lora_text_classifier 骨架（peft 可选 import）
  mock_classifier.py   # 确定性 mock，供 pytest 与 --mode mock

src/quant_mas/features/
  text_signals.py      # merge_text_signals_into_features(...)

configs/text_model.yaml

scripts/train_text_model.py

tests/test_text_signals.py   # ≥10 项，全 mock

### 2. data_schema.py

```python
@dataclass
class FinancialTextRecord:
    date: date | str          # 文本可用日（发布日或 as-of 日）
    symbol: str
    source: str               # news / filing / synthetic
    text: str
    metadata: dict[str, Any]

@dataclass
class TextSignalRecord:
    date: ...
    symbol: str
    signal_name: str          # e.g. finbert_sentiment
    value: float              # 连续分数或编码后的 float
    model_id: str
```

提供 `to_dict` / `from_dict` 或等价序列化。

### 3. dataset.py

- `load_text_records(path: Path | str) -> list[FinancialTextRecord]`（支持 jsonl / parquet）
- `split_text_records_by_time(records, *, train_end, val_end) -> tuple[list, list, list]`
  - **严格按 date 排序**；train < val < test，禁止随机 split 穿越时间
- 提供 `build_synthetic_text_records(n_days, symbol="AAA")` 供测试

### 4. finbert_baseline.py

- `class SentimentClassifier(Protocol)` 或 ABC：`predict(texts: list[str]) -> list[float]`
- `class MockSentimentClassifier` — 确定性（如 hash → [-1, 1]）
- `class FinBERTSentimentClassifier` — 真实实现（import transformers 失败时 raise ImportError 并提示 `pip install -e ".[text]"`）
- `predict_sentiment(records, classifier) -> list[TextSignalRecord]`

pytest **只用 MockSentimentClassifier**。

### 5. lora_finetune.py

- `train_lora_text_classifier(config: dict, *, records, output_dir) -> dict`
  - 第一版可为 **stub**：写 metadata.json + 空/ mock adapter 占位，或当 `mode=mock` 时直接返回固定 metrics
  - 真实 LoRA 逻辑可 skeleton + `# TODO server only`，但接口与 config 须完整
- 不得在无 GPU 的 pytest 中调用真实 `model.fit`

### 6. features/text_signals.py

```python
def merge_text_signals_into_features(
    features: pd.DataFrame,
    signals: pd.DataFrame,
    *,
    on: tuple[str, str] = ("date", "symbol"),
    signal_columns: list[str] | None = None,
) -> pd.DataFrame:
    """Left join text signals; reject duplicate keys and future-dated signals."""
```

规则：
- features 必须含 `date`, `symbol`
- signals 每 (date, symbol) 至多一行（或聚合后一行）
- **断言** merge 后 row 数不变（left join，无 many-to-many 膨胀）
- 可选：`assert_no_future_text_leakage(features, signals)` — signal.date <= feature.date

与 `build_feature_table_from_config` 兼容：可在 yaml 增加可选 `text_signals_path`。

### 7. configs/text_model.yaml

```yaml
text_model:
  mode: mock                    # mock | finbert_baseline | lora
  model_name: ProsusAI/finbert
  max_length: 128
  batch_size: 16
  output_signal_name: finbert_sentiment
paths:
  text_records: data/text/sample_news.jsonl
  output_dir: outputs/text_models
  signals_output: outputs/text/signals.parquet
split:
  train_end: "2023-12-31"
  val_end: "2024-06-30"
features:
  merge_signal_columns:
    - finbert_sentiment
```

### 8. scripts/train_text_model.py

CLI：
- `--mode mock|finbert_baseline|lora`（默认 **mock**）
- `--config configs/text_model.yaml`
- `--text-path`、`--output-dir`、`--dry-run`
- `--help` 必须可用

行为：
- `mock`：读 synthetic / fixture jsonl → MockSentimentClassifier → 写 signals.parquet + metadata.json
- `finbert_baseline` / `lora`：无 transformers/peft 时 exit 1 并提示安装 `pip install -e ".[text]"`
- **不**在默认路径下载 multi-GB 权重（文档说明服务器手工）

### 9. pyproject.toml 可选依赖

```toml
[project.optional-dependencies]
text = [
    "transformers>=4.40",
    "peft>=0.10",
    "accelerate>=0.30",
    "torch>=2.0",
]
```

核心 `pip install -e .` **不装** torch/transformers；pytest 必须无 text extra 也全绿。

### 10. tests/test_text_signals.py（≥10 项）

全部 mock / synthetic，**不联网**：

1. FinancialTextRecord / TextSignalRecord 序列化
2. split_text_records_by_time 时间顺序、无重叠
3. MockSentimentClassifier 确定性输出
4. predict_sentiment 生成 TextSignalRecord 列表
5. merge_text_signals_into_features 增加列且 row 数不变
6. merge 拒绝 future leakage（构造 feature.date < signal.date 应 fail 或 drop）
7. merge 拒绝 duplicate (date, symbol)
8. build_synthetic_text_records + mock pipeline 端到端写 parquet
9. train_text_model.py --help（subprocess）
10. train_text_model.py --mode mock --dry-run（subprocess 或 import main）
11. test_features.py / test_train_model.py **保持通过**（不破坏现有特征列）
12. 可选：build_feature_table_from_config 在提供 text_signals_path 时多一列

## 兼容性要求

- **不得修改** LightGBM 训练核心逻辑默认行为；text 列为**可选**增量
- test_walk_forward.py、test_end_to_end_pipeline.py 保持通过
- M5 ResearchAgent / ContextBuilder **不受影响**
- ExperimentMemory 新 run 使用 family=`text_signal` 或 `lightgbm_text`（文档说明，第一版可不写 memory）

## 禁止

- 用 LLM/FinBERT **直接**输出 target_weight 或订单
- pytest 中 `from_pretrained` 下载真实权重
- 将未来日期新闻 merge 到历史 bar
- 用单段 ML backtest sharpe 冒充 OOS 结论
- commit `.env`、HF 权重、大 jsonl 数据集

## 验收命令

python -m pytest tests/test_text_signals.py -v
python -m pytest -v                                    # 全量 150+ passed
python scripts/train_text_model.py --help
python scripts/train_text_model.py --mode mock --config configs/text_model.yaml --dry-run
```

---

## Cursor 后续（Codex 完成后）

1. ~~新增 `docs/text_model_plan.md`~~ ✅
2. ~~更新 `docs/architecture.md` — Text Signal Layer~~ ✅
3. ~~更新 `docs/experiment_log.md` — EXP-20260602-019~~ ✅
4. ~~服务器 FinBERT smoke（EXP-TEXT-001）~~ ✅ — ModelScope 本地 FinBERT；200 signals
5. ~~text signal 并入 features → walk-forward（EXP-TEXT-WF-001）~~ ✅ — oos.sharpe **0.563** vs baseline **0.586**（Δ -0.023，exploratory）

**下一步（科研，非 Codex 骨架）**：扩大 JSONL 新闻覆盖 → EXP-TEXT-WF-002；可选 LoRA（EXP-TEXT-002）。详见 [text_model_plan.md](text_model_plan.md)、[server_commands.md](server_commands.md) §6.9。

---

## 参考现有代码

| 模块 | 路径 |
|------|------|
| Feature pipeline | `src/quant_mas/features/pipelines.py` |
| Future labels | `src/quant_mas/features/labels.py` |
| Train model | `src/quant_mas/models/training.py` |
| Walk-forward | `src/quant_mas/backtest/walk_forward.py` |
| Research baseline | `src/quant_mas/research/baseline.py` |
| M5 context | `src/quant_mas/context/context_builder.py` |
| 数据校验 | `src/quant_mas/data/validation.py` |

---

## 与 M5 / M5.5 的关系

| 模块 | 用途 |
|------|------|
| **M5** DeepSeek | 研究解释、报告叙事（LLM API） |
| **M5.5** vLLM | 本地 LLM 推理（进阶，待定） |
| **M6** FinBERT/LoRA | **结构化 text_features** 输入 LightGBM |

三者并存；M6 **不**替换 ResearchAgent，**不**用生成式 LLM 直接预测收益率。
