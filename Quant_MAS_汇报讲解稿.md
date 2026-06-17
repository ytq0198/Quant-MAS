# Quant MAS v5.1 — SRTP 项目初期汇报讲解稿

> 对应 PPT：`Quant_MAS_ZJU_CS_Premium_PPT.html`（共 **31** 页）  
> 汇报人：魏子安 · 浙江大学计算机科学与技术学院  
> 建议总时长：**30–40 分钟**（Part I MAS 编排约 12 分钟 · Part II 算法约 15 分钟 · Part III 实验约 8 分钟）

---

## 第 1 页 · 封面

各位老师、同学，大家好。

我是来自浙江大学计算机科学与技术学院的魏子安。今天向大家汇报的是我的 SRTP 项目——**Quant MAS v5.1**，全称是「基于多智能体协同的量化研究平台」。

需要在一开始就强调：这不是一个自动炒股或实盘交易系统，而是一个**面向量化科学研究**的平台。我们在架构层面禁用了实盘下单，所有策略都必须经过回测、Walk-forward 样本外验证和人工审查。

目前项目的主要进展包括：v5 企业级 Web 控制台已上线，核心 Walk-forward OOS 主 baseline 的样本外夏普比率为 **0.586**，全项目 **361 项单元测试**全部通过。代码已开源在 GitHub：github.com/ytq0198/Quant-MAS。

下面我将从系统架构、核心算法设计和实验结果三个部分，汇报项目至今的工作与阶段性结论。

---

## 第 2 页 · 汇报大纲

本次汇报共分三大部分，对应 PPT 第 3 到 31 页。

**第一部分，系统架构与 MAS 编排**（第 3–11 页，**本次加强重点**）：除项目定位、8 层架构图和 Web 控制台外，我会专门介绍**工具层如何注册与调用**、**MCP 协议与 ToolPolicy 安全网关**、**三类 Agent 如何路由与编排**、**ResearchWorkflow 六节点 DAG 与 MCPScheduler 调度**，以及 **ExperimentMemory / RAG 如何为 Agent 装配上下文**。

**第二部分，核心算法演进设计**（第 12–25 页）：按时间线讲规则基线、ML 过拟合警示、Walk-forward OOS 主路径、文本消融、GRPO 与指标隔离。

**第三部分，实验验证与成果分析**（第 26–31 页）：8 组服务器实验、OOS 主结果、里程碑与展望。

---

## 第 3 页 · 项目定位：确定性科学研究平台

Quant MAS 的第一性设计原则，是**把「量化研究」和「实盘交易」彻底分开**。

左侧表格可以看到：平台原生支持的是「数据清洗 → 滚动回测 → OOS 验证 → 论文级审计」这条科研流水线；而「实盘账户对冲、自动下单」在架构上被**物理禁用**，不是功能没做完，而是刻意不做。

右侧是 **Core Separation 核心隔离设计**，分三层：

1. **Quant Engine（确定性计算层）**：用纯 Python 实现数据校验、特征、回测、Walk-forward OOS 和风险计算。Sharpe、回撤等指标在这里算出，保证可复现、无 LLM 幻觉。
2. **Agent Layer（智能编排层）**：Supervisor、Research、Report 等智能体负责理解任务、调用工具、检索 RAG 知识库、生成可读报告——但**不直接做数值计算，更不下单**。
3. **Web Console**：本地浏览器通过 SSH 隧道连接远程 GPU 服务器，提交 Job、查看进度和产物。

底部这条链路——Local Browser → SSH Tunnel → GPU Cluster——就是我们实际的开发部署方式。

---

## 第 4 页 · 系统架构全景图（8 层分层设计）

这一页展示的是 Quant MAS 的**完整架构全景图**，从下到上共 8 层。

请大家从下往上看：

- **L1 数据层**：从 Stooq、YFinance、FRED、SEC、Finnhub 等多源抓取 OHLCV、宏观和新闻，统一落盘为 Parquet。
- **L2 量化引擎层**：这是系统的数学核心——数据验证、特征工程、LightGBM 模型、MaCross / ml_signal 策略、BacktestEngine、Walk-forward OOS 和风险层，全部是确定性 Python 计算。
- **L3 实验层**：ExperimentMemory、BaselineRegistry，管理每次实验的配置和结果。
- **L4 Memory/RAG 层**：文档加载、混合检索、向量存储，为 Agent 提供知识上下文。
- **L5 工具层**：BacktestTool、TrainModelTool、RiskTool 等，Agent 只能通过这些白名单工具访问 Engine。
- **L6 智能体层**：Supervisor、Research、Report Agent——编排工具，解释结果，**不直接交易**。
- **L7 编排协议层**：M4 六节点 DAG、M13 MCP 调度、ToolPolicy 安全策略。
- **L8 输出与人工审核**：回测报告、Walk-forward 报告、Audit 日志、论文 CSV 导出，**必须经人工确认**。

图右侧还标注了两条**安全边界**：LLM Agent 不能下单；只有经过审计的 OOS 指标才能支撑论文结论。这是整个系统的设计红线。

---

## 第 5 页 · 部署拓扑与 v5 全栈控制台

左边是 **v5 Enterprise Research Console** 的实际界面截图。

可以看到 Overview 页面上几个关键信息：Backend 连接正常，**361 passed**，当前 OOS baseline **0.586**，以及醒目的 **Live trading disabled** 安全提示。

页面中间是 **Research Workflow** 九步流水线：Data → Features → Model → Backtest → Risk → OOS → Audit → Human Review → Paper Export。这九步不是装饰，而是我们规范每次实验必须走过的阶段。

右侧补充说明：控制台共有 13 个以上功能页面，包括 Experiments、Backtests、Walk-forward OOS、Agents、Audit、Paper Export、Help 等。后端提供 `POST /api/jobs` 接口，可以提交 backtest、walk_forward_oos 等任务。

部署方式是：本地 Windows 浏览器，通过 SSH 端口转发连到远程 A6000 GPU 服务器上的 FastAPI 后端；Web 和 CLI 共用同一套 Quant Engine，保证结果一致。

---

## 第 6 页 · 智能编排层与量化引擎的核心分工

这一页用一张流程图和一张对比表，把 Agent 和 Engine 的分工讲清楚。

流程是：**UI 触发任务 → Supervisor 分发 → ToolRegistry 鉴权 → BacktestTool 调度 → Engine 矩阵计算 → 输出 artifacts**。

表格里三行要点：

- **核心计算指标**：Sharpe、权益曲线、回撤、特征矩阵——全部由 Quant Engine 计算；Agent 只读结果、做解释，禁止自己「算数」。
- **工作流 DAG**：从数据输入、规则验证、特征衍生、模型重训、回测到审计，Engine 和 Agent 共享同一条有向图，但职责不同。
- **安全防线**：Engine 侧严格防止未来函数；Agent 侧硬编码禁止接入券商或实盘资金通道。

一句话总结：**Agent 负责「想和说」，Engine 负责「算和对」**。下面几页我会展开 MAS 各层是如何串起来的。

---

## 第 7 页 · 工具层：BaseTool 与 ToolRegistry

Quant MAS 的 Agent **不能直接** `import BacktestEngine` 去跑回测，必须通过**工具层（L5）**这一「唯一合法入口」。

每个工具继承 `BaseTool`，约定三个要素：`name`（唯一标识）、`description`（供 Agent/前端发现）、`run(**kwargs) → ToolResult`（执行并返回字符串化结果 + metadata）。

**ToolRegistry** 是注册中心，核心 API 很简单：

- `register(tool)` — 按 name 入库，重名会报错，防止工具冲突；
- `get(name).run(...)` — 按名取出并执行；
- `list()` / `names()` — 列出全部工具，供 MCP 导出和 Web「Tools」页展示。

工作流启动时调用 `create_default_tool_registry()`，默认注入五类工具：DataSummary、TrainModel、MLBacktest、Risk、Report；Supervisor 路由时还会用到 backtest、pipeline 等扩展工具。

PPT 表格列出了 **7 个白名单工具**及其职责：从 `data_summary` 看数据行数，到 `backtest` / `ml_backtest` 跑回测，`train_model` 训 LightGBM，`risk_check` 审权重，`pipeline` 跑端到端流水线，`report` 从 ExperimentMemory 出报告。

**讲解要点**：工具层是 Agent 与 Engine 之间的「防火墙 + 适配器」——Agent 只知道工具名和参数，不知道 Engine 内部怎么算 Sharpe。

---

## 第 8 页 · MCP 协议与 ToolPolicy 安全网关

光有 ToolRegistry 还不够，还要防止 Agent 或调度器调用危险操作。M13 模块实现了**内部 MCP 风格协议**（Model Context Protocol 的简化版，不是对外暴露的 MCP Server）。

完整调用链是：

**MCPToolCall(tool_name, arguments) → ToolPolicy.evaluate() → execute_mcp_tool_call() → ToolRegistry.get().run() → MCPToolResult**

三个适配函数值得记住：

1. `tool_to_mcp_spec()` — 把 BaseTool 转成带参数 schema 的 MCPToolSpec；
2. `registry_to_mcp_specs()` — 批量导出，Agent 和 UI 靠它「发现」有哪些工具、各要什么参数；
3. `execute_mcp_tool_call()` — 统一执行入口，先过 Policy 再调 Registry。

**ToolPolicy 是 deny-by-default（默认拒绝）**：

- **允许名单**：data_summary、backtest、train_model、report、ml_backtest、pipeline、risk_check；
- **工具名黑名单模式**：shell、exec、broker、order、live_trade 等一律 DENY；
- **参数黑名单**：api_key、secret、password、token，以及指向 `.env` 的路径；
- 决策三种：ALLOW、DENY、REQUIRE_CONFIRMATION（需人工确认才执行）。

如果 Policy 拒绝，调用到不了 Engine，结果写入 audit 日志。这保证了即使 LLM「想」执行 shell 或下单，也会在协议层被拦下。

---

## 第 9 页 · 智能体层：Supervisor / Research / Report

智能体层（L6）有三类角色，分工明确：

**1. SupervisorAgent — 轻量规则路由**

它不依赖复杂 LLM 规划，而是用**关键词规则**把用户任务映射到唯一工具。例如任务里含「回测」→ `backtest`；含「训练」→ `train_model`；含「ML回测」→ `ml_backtest`；含「全流程」→ `pipeline`。

执行过程全程留痕：`AgentEvent`（收到任务）→ `ToolCallEvent`（选定工具）→ 调用 Registry → `AgentFinishEvent`（返回结果）。`max_steps` 有上界，防止死循环。

**2. ResearchAgent — 研究解释（LLM）**

它消费 `AgentContextBundle`——里面打包了实验指标快照、RAG 检索片段、风险上下文。System prompt 硬性规定：**不得建议实盘下单、不得给 target weight**，Walk-forward OOS 才是 paper-grade 证据。

输出结构化 JSON：hypothesis、evidence_summary、suggested_experiments、risks_and_caveats。LLM  narrative 是非权威层，不能改写 Engine 算出的数字。

**3. ReportAgent — 报告格式化**

把 Engine 产物整理成可读报告，不改数值。

**补充**：Web 的 `POST /api/jobs` 和 CLI 可以**绕过 Agent 直接调 Engine**；Agent 是研究助手，不是交易执行器。

---

## 第 10 页 · 编排层：ResearchWorkflow 与 MCPScheduler

Supervisor 解决「一句话 → 一个工具」；**编排层**解决「一整条研究流水线 → 多个节点顺序/依赖执行」。

**M4 ResearchWorkflow — 六节点固定 DAG**

顺序是：

`data_check → feature_build → train_model → ml_backtest → risk_check → report`

状态放在 `QuantWorkflowState` 里，跨节点传递数据路径、已完成节点、错误列表。每个节点函数在 `nodes.py` 里实现，执行时注入**同一个 ToolRegistry**。

运行方式有两种：`run_sequential_workflow()` 顺序跑；或可选 **LangGraph** 后端做更复杂的状态机。任一步失败可 `stop_on_error` 中止，避免脏数据流向下游。

**M13 MCPScheduler — YAML Recipe 调度**

适合更灵活的流水线，例如文本 smoke 实验：

`align_real_news → audit_text_signals → walk_forward_eval`（带 depends_on 依赖）

调度器先 `plan(recipe)` 做**拓扑排序**，再 `run()` 逐节点：每步先 ToolPolicy 鉴权，通过后执行（当前 M13.0 默认 dry_run 模式），结果写入 `audit.jsonl`。`InMemoryMessageBus` 发布 PlanMessage、NodeResultMessage，便于审计和 UI 订阅。

**讲解对比**：Supervisor = 单步路由；ResearchWorkflow = 固定六步科研 DAG；MCPScheduler = 可配置 recipe + 依赖图。

---

## 第 11 页 · 记忆层与 RAG：ContextBuilder

Agent 要「懂」当前实验，不能靠幻觉，需要**记忆层（L3）+ RAG（L4）**。

**ExperimentMemory（L3）**

每次回测、Walk-forward OOS 结束都会注册到 `experiments.json`，记录 config、metrics 族（oos.* / simulation.*）、artifact 路径。存储后端支持 JSON、SQLite、Postgres；`BaselineRegistry` 锁定主 baseline（OOS Sharpe 0.586）；`compare_experiments` 做跨实验对比，但禁止混用不同指标族。

**RAG 检索链（L4）**

文档加载 → `chunk_text` 分块 → Embedding（默认 HashEmbedding，可选 OpenAI 兼容 / pgvector）→ VectorStore → Retriever.search。

两种检索器：`SimpleRetriever`（关键词/向量）和 `HybridRetriever`（混合）。Neo4j 可选做策略关系图谱。

**ContextBuilder** 把上述拼成 `AgentContextBundle`：实验快照 + 市场上下文 + 压缩后的 RAG chunks（默认 top_k=5）→ 交给 ResearchAgent。这样 LLM 的解释**有据可查**，且与 Engine 指标分离。

---

## 第 12 页 · Part II 章节扉页

下面进入**第二部分：核心算法设计、演进与隔离机制**。

这一部分按「改进过程」讲算法：从 MaCross 规则基线，到 ML 过拟合警示，再到 Walk-forward OOS 主路径，以及文本、RL 扩展与指标隔离。

---

## 第 13 页 · 系统演进全景

左边时间线讲**早期与对照实验**：

1. **v1 基础管道**：完成 validate_ohlcv、MaCross 策略、BacktestEngine，打通最小闭环。
2. **MaCross 对照**：实验 `server_ma_cross_real_001`，全样本 Sharpe **1.00**，总收益 202%。这是规则基线，不是 OOS 主结论。
3. **ML 单段警示**：LightGBM 在全段数据上训练再回测，Sharpe 高达 **2.78**——典型 in-sample 过拟合。平台明确标记：此指标**禁止作为主结论**。

右边是**突破与扩展**：

4. **Walk-forward OOS**：19 个滚动窗口、CUDA 加速，得到样本外主 Sharpe **0.586**——这是目前唯一论文级 baseline。
5. **M6–M12 扩展**：FinBERT 文本三线消融；GRPO + TradingEnv 强化学习；Population 种群演化——这些指标归属 simulation 或 population 命名空间，需独立 OOS 桥接验证。

这张页的核心信息是：**项目的改进是有迹可循的，每个阶段的指标族不同，不能混用**。

---

## 第 14 页 · 数据清洗 validate_ohlcv

算法链路的起点是**干净的数据**。

左侧：多源数据整合。量价方面覆盖 AAPL、MSFT、SPY；宏观接 FRED；文本接 Finnhub 新闻。原始数据经 `validate_ohlcv` 清洗后，统一写入 Parquet。

右侧是**硬编码校验规则**，Agent 无法绕过：

- 必须包含 date、symbol、OHLCV 六列；
- high 不能低于 low，volume 不能为负；
- 不允许重复 date+symbol；
- 按 symbol 分组、时间升序排列。

如果校验失败，整张表直接拒绝。这样可以在 LLM 参与编排之前，就把脏数据和时序错乱挡在门外，避免「看起来能跑、实际上有前视泄漏」的假策略。

---

## 第 15 页 · 特征工程 build_feature_table

特征流水线从左到右：原始量价 → 收益率 → 均线及距离 → 波动率 → 成交量比 → RSI → 可选文本信号。

**主 baseline 使用 15 维技术特征**，包括 return_1、ma_5/20、ma_distance、volatility_20、volume_ratio、rsi_14 等。每个 symbol 独立计算，避免跨标的泄漏。

预测标签是 `future_direction_5`：未来第 5 个交易日的涨跌方向。当前特征表共 **6033 行**，对应三只标的、约 2018–2025 年日频数据。

右侧是 **M6 文本融合支线**：用 `merge_text_signals_into_features` 把 FinBERT 情感分数按 date+symbol 对齐到特征表；缺失值填零或占位；`text_signal_audit` 审计实际覆盖率——后面会看到，覆盖率只有 2.4%，是文本 ablation 未跑赢 baseline 的主因。

---

## 第 16 页 · MaCross 规则基线

在讲 ML 之前，先介绍**最简单的规则对照**。

MovingAverageCrossStrategy 逻辑很直观：5 日均线在 20 日均线之上 → 满仓（weight=1）；否则空仓（weight=0）。Long-only，按 symbol 独立计算。

实验 `server_ma_cross_real_001` 结果：Sharpe **1.00**，总收益 **202%**，最大回撤 **-20.6%**。

需要强调：这是**全样本 in-sample 回测**，用于验证 BacktestEngine 是否正常、提供可解释对照，**不是** Walk-forward OOS 主结论。Web 控制台默认回测用的也是这套策略，方便快速演示。

---

## 第 17 页 · BacktestEngine 成交机制

BacktestEngine 是所有策略共用的**确定性仿真内核**，设计重点是**无未来函数**。

四步成交假设：

1. T 日收盘后，策略根据已知信息算出 `target_weight`；
2. **T+1 日开盘价**成交——不用收盘价，避免偷看未来；
3. 扣除滑点和佣金（各约 1 bps）；
4. 多标的时初始资金均分，权益曲线合并缩放。

输出三类产物：`equity_curve.csv`、`trades.csv`、`metrics.json`，并注册到 ExperimentMemory。

LLM 和 Agent 可以改策略参数、触发 Job，但**不能修改**这套成交数学逻辑——这是 reproducibility 的底线。

---

## 第 18 页 · LightGBM 两种训练模式

LightGBM 方向模型在项目里有**两种用法**，结论完全不同。

**模式 A：单次时序切分**（70/15/15）。实验 `server_lgbm_gpu_001` 的 test AUC 只有 **0.479**，接近随机猜测。说明：金融时序非平稳，静态切分一次训练**不能**代表策略真实能力。

**模式 B：Walk-forward 滚动重训**（主路径）。每个窗口独立 fit 一个 LightGBM，GPU 训练。典型现象：训练集 AUC 接近 **0.997**，但 OOS AUC 约 **0.472**——过拟合非常明显。

正是模式 A 和 B 的对比，支撑了我们必须用 19 窗 Walk-forward 才能汇报可信结论的设计选择。

超参方面：n_estimators=100，learning_rate=0.05，num_leaves=31，random_state=42，与服务器实验一致。

---

## 第 19 页 · MLSignalStrategy 概率映射

模型输出的是上涨概率 `pred_proba`，真正下单逻辑在 **MLSignalStrategy**：

- p ≥ **0.6**（buy_threshold）→ 信号 +1，目标权重 1.0；
- p ≤ **0.4**（sell_threshold）→ 信号 -1，权重 0；
- 中间区间 → 信号 0，**维持上一期权重**。

注意：策略层**不调用模型**，只消费预先算好的概率表——训练和回测在时间上严格分离，保证因果。

与 MaCross 对比：MaCross 可解释、无 ML 过拟合风险；ml_signal 能捕捉非线性模式，但必须配合 Walk-forward OOS 才有学术意义。两者共用同一 BacktestEngine，对比公平。

---

## 第 20 页 · Walk-forward OOS 核心机制

这是全项目**最重要的算法页**。

为解决全样本过拟合，我们把时间轴切成 **19 个滚动窗口**。每个窗口内：

- **Train 504 天** → 训练 LightGBM  
- **Val 126 天** → 调参/监控  
- **Test 126 天** → 样本内测试  
- **OOS 63 天** → **从未参与训练的样本外回测**

窗口以 **step=63 天** 向前滚动，共 19 轮。每轮 OOS 段跑 MLSignal + BacktestEngine，最后拼接成全局 OOS 权益曲线。

主实验 `server_walk_forward_001`（EXP-20260602-008）汇总指标：

| 指标 | 值 |
|------|-----|
| oos.sharpe | **0.586** |
| oos.total_return | 44.3% |
| oos.max_drawdown | -25.5% |
| oos.annualized_return | ~8.0% |
| 窗口数 | 19 |

**0.586 是目前唯一应写入论文主表的 Sharpe**。它比 ML 单段的 2.78 低很多，但这才是样本外的真实表现。

---

## 第 21 页 · 文本消融三线实验

M6 模块问的问题是：**FinBERT 文本情绪能不能提升 OOS？**

我们设计了三线 ablation，Walk-forward 配置与 baseline 完全一致，只改文本输入：

| 实验 | 文本策略 | 覆盖率 | oos.sharpe | vs 0.586 |
|------|----------|--------|------------|----------|
| WF-text-001 | 200 条 FinBERT smoke | 3.3% | 0.563 | -0.023 |
| WF-text-002 | 100% 占位文本（噪声对照） | 100% | 0.579 | -0.007 |
| WF-text-003 | Finnhub 真实新闻 | 2.4% | 0.565 | -0.021 |
| 纯量价 baseline | 无文本 | — | **0.586** | — |

结论很清晰：**三条文本线都没有稳定超越 baseline**。审计发现真实新闻只覆盖了 146/6033 行（2.4%），模型很难从如此稀疏的信号里学到稳健规律。

这不是 Walk-forward 框架的问题，而是**数据覆盖不足**。下一步计划是 EXP-TEXT-002：LoRA 微调 FinBERT + 更长窗口。

---

## 第 22 页 · GRPO 强化学习（M7）

GRPO 是我们探索的**仿真侧**策略优化方法，不属于 OOS 主表。

动机：传统 PPO 需要 Critic 估计 V(s)，金融噪声大时 Critic 容易发散。GRPO **去掉 Critic**，在同一状态下并行采样 G 个动作/策略，用组内收益的相对排名算优势：

\[
A_i = \frac{R_i - \mathrm{mean}(R_{1..G})}{\mathrm{std}(R_{1..G})}
\]

目标函数带 PPO 式 clip 和 KL 惩罚，防止策略漂移过快。

**重要边界**：GRPO 训练产出只归入 `simulation.*` 或 `training.*`，**严禁**直接写入论文主表。要想推广到 OOS，必须走 M11.7/M11.8 的候选策略 OOS 桥接。

---

## 第 23 页 · TradingEnv MDP

TradingEnv 把交易建模为 MDP：

**状态 S_t** 包含：过去 N 步的 15 维技术特征、上一期权重、当前回撤、以及 RAG 检索到的历史相似形态上下文。

**动作 A_t** 可以是离散 {Buy, Sell, Hold}，也可以是连续权重向量，满足 Σw=1、w≥0。

**奖励 R_t** 是复合塑形：Sharpe 项 − λ₁×最大回撤惩罚 − λ₂×换手惩罚。目的是在仿真里鼓励稳健收益，而不是无脑追求高回报。

Again，这是在 simulation 环境里训练，指标不能和 oos.* 混谈。

---

## 第 24 页 · 种群演化与 RL→OOS 教训

**PopulationManager（M11）**维护多个候选 Agent，用汉明距离保证策略多样性，避免种群塌缩到同一策略；池内还有 Elo 式相对评分。研究扩展中，局部 OOS 最优候选曾出现约 1.039 的 Sharpe，但这**不在**服务器主表 export 里，且需独立验证。

**M12 的教训**更值得关注：

| 阶段 | 问题 | oos.sharpe |
|------|------|------------|
| M12.3 POP-009 | Policy 不读观测，仿真奖励虚高 → 实盘 OOS 全空仓 | **0.0** |
| M12.4 POP-010 | Observation-aware RL，修复特征感知 | **0.387** |
| WF baseline | LightGBM Walk-forward | **0.586** |

这说明：**仿真里 reward 很高 ≠ OOS 有效**。RL 路线必须独立过 Walk-forward 桥，目前仍低于 ML baseline，是诚实的 negative result。

---

## 第 25 页 · 指标命名空间隔离

为防止「拿 in-sample 2.78 当结论」这类学术陷阱，我们在源码层做了**命名空间物理隔离**：

| 命名空间 | 场景 | 规则 |
|----------|------|------|
| **oos.*** | Walk-forward 19 窗样本外 | 🏆 **唯一可写论文主表** |
| simulation.* | RL 仿真、ML 单段回测 | ❌ 仅警示，如 sharpe 2.78 |
| training.* | AUC、Loss | ❌ 只看收敛，不作业绩结论 |
| population.* | 种群内 Elo、Hamming | ⚠ 须 OOS 桥接后才可对比 |

这是 M13 合规设计的一部分，配合 ToolPolicy（拒绝 shell、broker、secrets）和 Audit JSONL 全链路留痕，保证实验可审计、可复现。

---

## 第 26 页 · Part III 章节扉页

第三部分汇报**服务器上的真实实验数据**。

数据来源：A6000 GPU 服务器，2026 年 6 月 4 日导出，共 46 个文件，落在 `docs/ppt_data/`。标的为 AAPL、MSFT、SPY。主表是 `paper_main_results.csv`。

---

## 第 27 页 · 8 组关键实验一览

服务器 `experiments.json` 里注册了 **8 组**核心实验：

1. **ma_cross_real_001** — 规则基线，sharpe 1.00  
2. **lgbm_gpu_001** — 静态切分，test_auc 0.479  
3. **ml_backtest_001** — ML 全段回测，sharpe **2.78**（过拟合警示，系统拦截）  
4. **walk_forward_001** — 🏆 主 baseline，**oos.sharpe 0.586**  
5–7. **walk_forward_text_001/002/003** — 文本 ablation，oos 0.563–0.579  
8. **EXP-LLM-002** — Agent 解释层与 RAG 审计  

每一行实验的 family 不同，指标不能横向直接比——必须看命名空间。

---

## 第 28 页 · OOS 主结果与特征重要性

左边柱状图：上面四根是 OOS 家族——baseline **0.586** 最高，三条文本线略低；下面两根是对照——ML in-sample **2.78** 虚高（红色警示），MaCross **1.00** 是全样本规则基线。

右边是 LightGBM **特征重要性 Top 5**：

1. volatility_20 — 414  
2. volume_ma_20 — 378  
3. ma_20 — 329  
4. ma_distance_20 — 251  
5. rsi_14 — 221  

解读：**波动率和成交量**主导模型分裂，与均线规则形成互补——ML 主要在抓「波动+量能」 regime，而不是简单复制 MaCross。

---

## 第 29 页 · 工程里程碑

四个 KPI：**361** pytest 全过；**M1–M13** 模块全线交付；**46** 个 PPT 数据文件；**v5.1** 已开源。

模块交付摘要：

- M1–M2：BaselineRegistry + 多源数据  
- M4–M5：六节点 DAG + RAG  
- M6：文本三线 ablation + 覆盖率审计  
- M7：TradingEnv + GRPO  
- M11–M12：Population + RL→OOS 桥  
- M13：MCP、ToolPolicy、论文 CSV 一键导出  

作为初期汇报，工程侧我们已经搭好了**可跑、可测、可审计**的完整平台，而不只是算法 demo。

---

## 第 30 页 · 局限性与下一步

三块诚实汇报：

**文本局限**：Finnhub 新闻覆盖率仅 2.4%，文本特征难以发挥；计划 LoRA FinBERT + 更长窗口。

**RL 转化**：仿真 reward 高但 OOS 衰减明显；M12.4 修到 0.387 仍低于 0.586 baseline；需更强方差控制和更长训练。

**下一步工作**：

1. 推进论文撰写与多种子 OOS 稳健性检验（p-value）；  
2. 补全 Population/RL 的 ablation 导出；  
3. WebUI 端到端 Agent 自动提交、监控全流程。

---

## 第 31 页 · 致谢与 Q&A

以上就是 Quant MAS 项目初期的主要工作汇报。

**三句话总结**：

1. 我们做的是**量化研究平台**，不是自动炒股；Live trading disabled 是设计选择。  
2. **Agent 编排、Engine 计算**严格分离；主结论只看 **oos.***，当前 baseline Sharpe **0.586**。  
3. 从 MaCross → ML 过拟合警示 → Walk-forward → 文本/RL 扩展，**改进过程可追溯**，negative result 也如实报告。

开源地址：github.com/ytq0198/Quant-MAS。欢迎老师同学们批评指正，谢谢！

---

## 附录：常见问题速答（Q&A 备用）

**Q：这是不是 AI 自动炒股？**  
A：不是。LLM Agent 只编排研究和解释结果，Quant Engine 做历史回测；无券商接口，无实盘下单。

**Q：为什么 OOS 0.586 比 ML 2.78 低那么多？**  
A：2.78 是全样本 in-sample 过拟合；0.586 是 19 窗 Walk-forward 真实样本外表现。论文只能信后者。

**Q：文本和 RL 是不是失败了？**  
A：在当前数据与配置下，文本未超 baseline、RL OOS 低于 ML baseline——这是有价值的 ablation 结论，说明主路径仍是 15 维量价 + LightGBM + WF OOS。

**Q：Agent 是怎么调用回测的？**  
A：用户任务 → SupervisorAgent 关键词路由 → MCPToolCall → ToolPolicy 鉴权 → ToolRegistry.get("backtest").run() → BacktestEngine 计算 → 结果写入 ExperimentMemory 和 audit 日志。Agent 本身不算 Sharpe。

**Q：ResearchWorkflow 和 Supervisor 有什么区别？**  
A：Supervisor 是「一句话一个工具」；ResearchWorkflow 是固定的六节点 DAG，状态在 QuantWorkflowState 里传递；MCPScheduler 则支持 YAML recipe 和节点依赖，适合文本 smoke 等复杂流水线。

**Q：和同类工作的差异？**  
A：核心差异是「多智能体编排 + 确定性 Engine + 指标命名空间隔离 + 企业级 Web 控制台」一体化，强调可复现与合规，而非追求 in-sample 漂亮数字。

---

*讲解稿版本：2026-06 · 与 Quant_MAS_ZJU_CS_Premium_PPT.html 同步*
