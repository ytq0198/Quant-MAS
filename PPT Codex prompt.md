# Quant MAS PPT 实验数据 — Codex 提示词

> **用途**：配合 [`PPT prompt.md`](PPT%20prompt.md) 使用。将下方「--- 复制给 Codex ---」整段粘贴给 Codex，让它基于 **真实服务器实验数据** 制作 PPT 图表、数据页文案与结果分析。  
> **数据位置**：`docs/ppt_data/`（已从 GitHub `main` 同步，共 46 文件，约 888 KB）  
> **GitHub**：https://github.com/ytq0198/Quant-MAS/tree/main/docs/ppt_data  
> **清单原文**：`docs/ppt_data/DATA_MANIFEST.md`

---

## 一、数据包是什么（给 Codex 的背景摘要）

这是 Quant MAS 项目在 **a6000 GPU 服务器**（`/mnt/localDisk3/weizian/`）上跑完实验后，于 **2026-06-04** 导出的 **PPT/论文专用脱敏数据包**。

| 属性 | 说明 |
|------|------|
| **包含** | 8 条实验的指标 JSON/CSV/MD、Walk-forward OOS 明细、回测权益曲线、LightGBM 训练指标、文本信号审计、LLM 实验记录、M13 论文导出表 |
| **不含** | `.env`、API Key、原始 `.parquet` 行情、`.pkl` 模型权重（体积大或敏感，见 `.gitignore`） |
| **实验标的** | AAPL、MSFT、SPY（2018-01-01 ~ 2025-12-31，约 6033 行特征） |
| **论文主指标** | **仅** Walk-forward **OOS** 的 `oos.sharpe` / `oos.total_return` |
| **主 baseline** | `server_walk_forward_001` → **oos.sharpe = 0.586**，19 滚动窗口，GPU LightGBM + ml_signal 策略 |

**核心科研结论（PPT 必须遵守）**：

1. **论文级唯一主结论**：OOS Sharpe **0.586**（baseline），总收益约 **44.3%**（OOS 段），最大回撤约 **-25.5%**  
2. **文本特征 ablation**：加入文本信号后 OOS Sharpe **0.563~0.579**，与 baseline **接近**，未显著超越  
3. **ML 单段回测 Sharpe 2.78** 是 **in-sample 对照**，**禁止**与 OOS 0.586 并列作为主结论  
4. **均线规则策略 Sharpe 1.00** 是全样本回测对照，**非 OOS**  
5. **RL / population ablation CSV 当前为空**（仅占位，PPT 可不展开或标「预留」）  
6. **文本 WF-003** 真实 Finnhub 新闻覆盖率仅 **~2.4%**（146/6033 行），解释文本实验提升有限  

---

## 二、文件地图与 PPT 用途

### 2.1 优先引用（核心表）

| 相对路径 | PPT 用途 | 关键内容 |
|----------|----------|----------|
| `paper/paper_main_results.csv` | **主结果页**柱状图/表格 | 4 条 OOS 实验 sharpe/return/drawdown |
| `paper/paper_text_ablation.csv` | 文本 ablation 专页 | WF-text-001/002/003 |
| `paper/paper_experiment_index.md` | 实验索引说明 | 8 条实验 ID 与 family |
| `research/comparison.md` | **全景对比页** | ma_cross / lgbm / ml_backtest / walk_forward 一行表 |
| `research/comparison.csv` | 同上（可画图） | 含非 OOS 与 OOS 分列 |

### 2.2 Walk-forward 明细（OOS 深入页）

| 相对路径 | PPT 用途 |
|----------|----------|
| `walk_forward/baseline_walk_forward_latest/summary.md` | baseline 人类可读摘要（19 窗、15 特征、CUDA） |
| `walk_forward/baseline_walk_forward_latest/metrics.json` | 完整 train/val/test/oos 指标 |
| `walk_forward/baseline_walk_forward_latest/windows.csv` | **每窗 OOS Sharpe 折线图**（19 点） |
| `walk_forward/baseline_walk_forward_latest/oos_equity_curve.csv` | **OOS 权益曲线**（1197 bars） |
| `walk_forward/walk_forward_text_001/` | 文本 smoke（200 条）OOS 明细 |
| `walk_forward/walk_forward_text_002/` | 100% 占位文本 OOS 明细 |
| `walk_forward/walk_forward_text_003/` | Finnhub 真实新闻 OOS 明细 |

### 2.3 对照实验（说明「为什么不能只报回测」）

| 相对路径 | 指标 | PPT 角色 |
|----------|------|----------|
| `ma_cross/metrics.json` + `equity_curve.csv` | sharpe **1.00**, return **202%** | 规则策略 **in-sample** 对照 |
| `ml_backtest/metrics.json` + `equity_curve.csv` | sharpe **2.78**, return **6827%** | ML **单段过拟合**对照（醒目警示） |
| `lgbm/metrics.json` | test_auc **0.479** | 分类器接近随机，支撑「需 OOS」叙事 |
| `lgbm/feature_importance.csv` | volatility_20 等 Top 特征 | **特征重要性柱状图** |

### 2.4 文本与 LLM（扩展页）

| 相对路径 | PPT 用途 |
|----------|----------|
| `text/text_signal_audit_wf001/summary.md` | 覆盖率 **3.3%**（200 条 smoke） |
| `text/text_signal_audit_wf002/summary.md` | 覆盖率 **100%**（占位文本） |
| `text/text_signal_audit_wf003/summary.md` | 覆盖率 **2.4%**（Finnhub 真实新闻） |
| `text/real_news_alignment_wf003/` | 新闻对齐 metrics |
| `llm/EXP-LLM-002.json` | ResearchAgent + RAG 输出示例（**非权威指标**） |

### 2.5 元数据

| 相对路径 | 说明 |
|----------|------|
| `experiments/experiments.json` | ExperimentMemory 全量 8 条 |
| `paper/audit_summary.json` | 当前 audit 事件为 0（导出时无 JSONL） |

---

## 三、主结果数字速查（可直接写入 PPT）

### 3.1 OOS 主结果表（来自 `paper_main_results.csv`）

| 实验名 | family | oos.sharpe | oos.total_return | oos.max_drawdown | 解读 |
|--------|--------|------------|------------------|------------------|------|
| server_walk_forward_001 | walk_forward | **0.586** | 0.443 | -0.255 | **主 baseline** |
| server_walk_forward_text_001 | text_ablation | 0.563 | 0.420 | -0.259 | smoke 200 条文本 |
| server_walk_forward_text_002 | text_ablation | 0.579 | 0.443 | -0.265 | 100% 占位覆盖 |
| server_walk_forward_text_003 | text_ablation | 0.565 | 0.421 | -0.259 | Finnhub 真实新闻 ~2.4% |

**PPT 表述建议**：文本 ablation 三线与 baseline 差距 < 0.025 sharpe → 「文本信号在本数据覆盖下未带来稳定 OOS 提升，与 baseline 同量级」。

### 3.2 非 OOS 对照（来自 `research/comparison.md`）

| 实验名 | family | sharpe | total_return | 说明 |
|--------|--------|--------|--------------|------|
| server_ma_cross_real_001 | ma_cross | 1.00 | 202% | 均线全样本回测 |
| server_ml_backtest_001 | ml_backtest | **2.78** | 6827% | ⚠️ 单段 ML，**非 OOS** |
| server_lgbm_gpu_001 | lightgbm | — | — | test_auc 0.479 |

### 3.3 Baseline Walk-forward 配置摘要

- **窗口**：19 窗；train 504 / val 126 / test 126 / oos 63 / step 63（交易日）  
- **模型**：LightGBM 方向预测，`device=cuda`  
- **策略**：ml_signal（buy>0.6, sell<0.4）  
- **特征**：15 维（OHLCV + MA + RSI + volatility 等）  
- **OOS 段**：2021-02 ~ 2025-11，3591 samples，1197 bars  
- **训练 AUC ~0.997 vs OOS AUC ~0.472** → 典型过拟合，故必须报告 OOS 而非 train  

### 3.4 特征重要性 Top 5（`lgbm/feature_importance.csv`）

1. volatility_20 (414)  
2. volume_ma_20 (378)  
3. ma_20 (329)  
4. ma_distance_20 (251)  
5. rsi_14 (221)  

---

## 四、建议制作的图表（文件 → 图类型）

| 图编号 | 标题建议 | 数据文件 | 画法 |
|--------|----------|----------|------|
| Fig-1 | OOS Sharpe 主结果对比 | `paper/paper_main_results.csv` | 柱状图：x=实验名，y=oos.sharpe，baseline 高亮 0.586 |
| Fig-2 | In-sample vs OOS 警示 | `research/comparison.csv` | 双柱：ML sharpe 2.78 vs OOS 0.586，**不同色 + 标注 metric 族** |
| Fig-3 | OOS 权益曲线 | `walk_forward/baseline_walk_forward_latest/oos_equity_curve.csv` | 折线图（归一化 equity） |
| Fig-4 | 19 窗 OOS Sharpe 稳定性 | `walk_forward/.../windows.csv` | 折线：window_id vs oos_backtest_sharpe |
| Fig-5 | 规则 vs ML 权益曲线 | `ma_cross/equity_curve.csv` + `ml_backtest/equity_curve.csv` | 双折线（需标注 in-sample） |
| Fig-6 | LightGBM 特征重要性 | `lgbm/feature_importance.csv` | 水平条形图 Top 10 |
| Fig-7 | 文本覆盖率 vs OOS | 三个 `text/text_signal_audit_wf*/summary.md` + `paper_main_results.csv` | 表格或气泡图：coverage vs oos.sharpe |
| Fig-8 | Walk-forward 窗口示意 | 无 CSV，自绘 | 时间轴滚动 train/val/test/oos 示意（见 `项目说明.md`） |

**[配图占位]**：UI 截图仍从控制平台截取；**数值图表务必从上述 CSV 读取真实数字**，禁止编造。

---

## 五、PPT 叙事线（基于数据的推荐故事）

1. **问题**：量化策略需要可复现、可审计的 **样本外** 验证，不能只报 in-sample 回测  
2. **方法**：Walk-forward OOS（19 窗）+ LightGBM + ml_signal + 佣金/滑点  
3. **主结果**：OOS Sharpe **0.586**，年化约 **8.0%**（OOS 段），回撤 **-25.5%**  
4. **对照**：ML 单段 Sharpe 2.78 → 说明过拟合风险；train AUC 0.997 vs OOS AUC 0.472  
5. **Ablation**：文本信号三线未超 baseline → 覆盖率太低（真实新闻 2.4%）是合理解释  
6. **工程**：8 条实验登记、论文 CSV 导出、361 tests、企业级 Web 控制台  
7. **边界**：非实盘、LLM 不下单、主指标仅 `oos.*`  

---

## --- 复制给 Codex ---

你正在协助制作 **Quant MAS SRTP 汇报 PPT**。请 **只使用仓库内真实数据**，路径根目录为：

```text
docs/ppt_data/
```

请先阅读 `docs/ppt_data/DATA_MANIFEST.md` 与 `docs/ppt_data/paper/paper_main_results.csv`，再完成以下任务。

### 任务 A：数据理解摘要（输出 1 页 Markdown）

用中文写一段 **300～500 字**「实验数据说明」，包含：

- 数据包来源（a6000 服务器，2026-06-04 导出，8 条实验）  
- 论文主指标为何只能是 **oos.sharpe**  
- 主 baseline **0.586** 的含义（19 窗 walk-forward，非单段回测）  
- 为何 **不能** 把 ML sharpe **2.78** 写进主结论  
- 文本 ablation 三线（0.563 / 0.579 / 0.565）与 baseline 的关系  

### 任务 B：PPT 数据页文案（输出 4～6 页幻灯片内容）

每页含：**标题、3～5 bullet、演讲备注、建议图表（Fig-1～Fig-8 编号）**。

必须覆盖：

1. **主结果页** — 引用 `paper_main_results.csv` 四行 OOS 数据  
2. **In-sample vs OOS 警示页** — ma_cross 1.00、ML 2.78 vs OOS 0.586  
3. **Walk-forward 方法页** — 19 窗、504/126/126/63 配置（来自 baseline summary.md）  
4. **文本 ablation 页** — 覆盖率 3.3% / 100% / 2.4% 与 OOS sharpe  
5. **特征重要性页** — Top 5 来自 `lgbm/feature_importance.csv`  
6. **（可选）LLM/RAG 页** — EXP-LLM-002 仅作「Agent 解释层」示例，**非量化主指标**  

### 任务 C：图表规格（输出表格）

对每个 Fig-1～Fig-7 给出：

- CSV 路径  
- X/Y 列名  
- 推荐图表类型  
- 必须在图注中写明的 metric 族（oos / simulation / training）  
- 若用 Python 画图，给出 **matplotlib/plotly 伪代码或完整脚本**（读取相对路径 `docs/ppt_data/...`）  

### 任务 D：禁止事项

- 禁止将 sharpe 2.78 或 return 6827% 作为「策略最终表现」  
- 禁止暗示实盘盈利或自动交易  
- 禁止编造 CSV 中不存在的实验行  
- `paper_rl_ablation.csv` 与 `paper_population_ablation.csv` 为空，不要虚构 RL/population 数字  
- 文本 audit 文件的 coverage **不是 OOS 结果**，仅说明数据质量  

### 任务 E：与 [`PPT prompt.md`](PPT%20prompt.md) 的衔接

假设整体 PPT 还有架构、Demo、安全边界等页（见 `PPT prompt.md`）。你输出的数据页应：

- 插入在「Walk-forward OOS 与论文级指标」章节 **之后**  
- 数字与 `项目说明.md`、`README.md` 中 OOS baseline 0.586 一致  
- 图表占位符用 `[Fig-N：描述]`，方便我后期插入 PNG  

请开始执行 Task A～E。若需读取 CSV，以仓库内文件为准；Sharpe 展示建议 **保留 3 位小数**（0.586 而非 0.585673…）。

## --- 复制结束 ---

---

## 六、本地验证命令（可选）

在项目根目录用 Python 快速查看主表：

```bash
python -c "import pandas as pd; print(pd.read_csv('docs/ppt_data/paper/paper_main_results.csv').to_string(index=False))"
```

或用 Excel / WPS 直接打开：

- `docs/ppt_data/paper/paper_main_results.csv`  
- `docs/ppt_data/research/comparison.csv`  

---

## 七、与现有文档的关系

| 文档 | 关系 |
|------|------|
| [`PPT prompt.md`](PPT%20prompt.md) | 整体 PPT 结构、架构、Demo、安全边界（**不含具体实验数字**） |
| **本文件** | **实验数据**解读、图表规格、Codex 数据页任务 |
| [`项目说明.md`](项目说明.md) | 系统与量化研究关系、Backtest vs OOS 概念 |
| [`docs/ppt_data/DATA_MANIFEST.md`](docs/ppt_data/DATA_MANIFEST.md) | 服务器导出的原始清单 |

**推荐工作流**：

1. 用 `PPT prompt.md` 让 Codex/ChatGPT 生成 **整体 PPT 骨架**  
2. 用 **本文件「复制给 Codex」段** 生成 **数据结果专页 + 图表脚本**  
3. 按 Fig-1～Fig-7 从 CSV 出图，UI 截图单独补  
4. 合并进最终 PPT  

---

*数据已于本地 `git pull origin main` 同步至 `docs/ppt_data/`。*
