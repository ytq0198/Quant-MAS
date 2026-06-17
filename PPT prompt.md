# Quant MAS 汇报 PPT — ChatGPT 提示词

> **用法**：将下方「--- 复制从这里开始 ---」到「--- 复制到这里结束 ---」之间的整段内容，粘贴给 ChatGPT（或 Claude、Gemini 等），让它生成 PPT 大纲、每页文案与演讲者备注。  
> **图片**：提示词中已用 `[配图占位：…]` 标出需插图的位置；PPT 做好后，你再自行替换为截图或项目内图片。  
> **仓库图片**：根目录有 `architecture.png`，可用于架构页。

---

## --- 复制从这里开始 ---

你是一位擅长 **科研汇报 / SRTP 中期或结题答辩** 的 PPT 设计顾问。请根据以下项目材料，为我制作一份 **中文为主、关键术语保留英文** 的汇报 PPT 方案。

### 一、输出要求

1. **先给出整体方案**：页数建议 **18～22 页**（含封面、目录、致谢/Q&A），汇报时长约 **12～15 分钟**。
2. **逐页输出**，每一页必须包含：
   - **页码 + 标题**
   - **页面类型**（封面 / 目录 / 内容 / 过渡 / 总结 / Q&A）
   - **正文要点**（每页 3～6 条 bullet，简洁、适合投影）
   - **演讲者备注**（每页 2～4 句口语化讲解，方便我照着讲）
   - **视觉建议**（配色、版式、图标/图表类型）
   - **配图占位**（若需要图片，用 `[配图占位：描述]` 标出；**不要生成假截图**，留空位即可）
3. **额外输出**：
   - 一页「**30 秒电梯演讲**」版本（口头开场用）
   - 一页「**预期提问与回答**」（5～8 个 Q&A，含「这是不是自动炒股」「Agent 和回测区别」等）
4. **风格**：
   - 学术 + 工程汇报风，专业、克制、可信
   - 主色建议：深青/teal + 深灰 + 白底（与 Quant MAS v5 企业控制台气质一致）
   - 避免花哨动画描述；强调 **结构清晰、安全边界、可复现**
5. **禁止**：
   - 不得宣传「自动盈利」「实盘荐股」「保证收益」
   - 不得把 in-sample 回测 Sharpe 说成论文最终结论
   - 不得省略「Live trading disabled / 非实盘系统」的说明

若你支持直接导出 PPT 结构（如 Markdown 大纲、Canva 分镜、PowerPoint 大纲格式），请用 **Markdown 表格 + 分级标题** 输出，方便我复制到 PowerPoint / WPS / Google Slides。

---

### 二、项目基本信息（事实依据，请准确引用）

**项目名称**：Quant MAS — Multi-Agent Quantitative Research Platform  
**中文名**：多智能体量化研究平台  
**GitHub**：https://github.com/ytq0198/Quant-MAS  
**性质**：SRTP / 科研训练项目 — **量化策略研究、验证与审计平台**，**不是**实盘自动交易系统  

**一句话定位**：  
将 **确定性 Quant Engine（量化引擎）** 与 **多智能体 Agent 编排** 分离：代码负责可复现的回测与 Walk-forward OOS；Agent 负责研究规划、工具路由与结果解释；Web 控制台提供企业级研究工作台。

**核心数字（可写在 KPI 页）**：
- 单元测试基线：**361 passed**
- 论文级 OOS 基线：**OOS Sharpe 0.586**（Walk-forward，实验 EXP-20260602-008，19 窗口）
- Python 3.11+，FastAPI 后端 + React 前端（v5 Enterprise Research Console）

**安全边界（必须在 PPT 中单独强调）**：
- Live trading disabled — 实盘交易已禁用
- LLM agents do not place live orders — LLM 不下实盘单
- Paper-grade metrics = **oos.*** only — 论文级指标仅 Walk-forward OOS
- 不得混用 simulation.* / training.* / population.* 与 oos.*

**技术栈关键词**（可做成标签云页）：  
Python · FastAPI · React · Vite · Parquet · LightGBM · Walk-forward OOS · Memory/RAG · LangGraph-style workflow · ToolPolicy · Audit JSONL · SSH 远程算力 · Job Queue

**部署架构（口述/架构页）**：
- 本地 Windows：浏览器 + Vite 前端（localhost:5173）
- SSH 隧道：本地 8000 → 远程服务器 8000
- 远程 GPU/算力服务器：uvicorn 后端 + Quant Engine + 数据/产物目录

**研究流水线**：
```text
Data → Features → Model/Strategy → Backtest → Risk → Walk-forward OOS → Audit → Human Review → Paper Export
```

**Web 控制台主要模块**（可做成「功能地图」页）：
Overview · Experiments · Backtests · Walk-forward OOS · Risk Review · Agents · Tools · Memory/RAG · Audit Logs · Paper Artifacts · Database · Observability · Settings · Help

**可演示的 UI 操作（Demo 页依据）**：
1. 顶栏显示 Server connected
2. Backtests 页提交 Run backtest Job → Job Console 显示进度 → completed → Refresh 看权益曲线
3. Experiments 注册表出现新实验
4. Walk-forward OOS 页查看 oos.* 指标（需 features.parquet）
5. Risk Review 人工 Approve/Reject
6. Help 页内置中英文使用指南

**Agent vs 回测（需单独一页对比）**：
| | Backtest / Quant Engine | Agent |
|--|-------------------------|-------|
| 角色 | 确定性计算 | 任务编排与解释 |
| 算什么 | 权益曲线、Sharpe、回撤 | 不直接算指标 |
| 可复现 | 同配置同结果 | 工具调用结果可复现 |

**Backtest vs OOS（需单独一页对比）**：
| | Backtest | Walk-forward OOS |
|--|----------|------------------|
| 目的 | 快速验证策略逻辑 | 检验样本外泛化 |
| 指标族 | simulation.* / backtest.summary | **oos.***（论文级） |
| 输入 | market_data.parquet | features.parquet |
| UI | Backtests | Walk-forward OOS |

**项目阶段（进度页）**：
- v1：确定性量化流水线（数据、特征、回测、OOS）— 已完成
- Plus v2 M1–M8：研究平台扩展 — 已完成
- v3 M9–M13：企业级审计、ToolPolicy、MCP 风格调度 — 已完成
- v5：Enterprise Research Console UI + Job 提交 API — 已完成

**创新点 / 贡献（请帮我在 PPT 中提炼 4～5 条）**：
1. LLM 与量化计算 **分层架构**，安全边界写入设计而非事后补丁  
2. **指标族分离**（oos.* vs simulation.*），避免科研结论混淆  
3. **可审计工作流**：Job、Audit Logs、Human Review 闭环  
4. **Memory/RAG + Agent 工具路由**，服务实验检索与报告  
5. **Web 研究控制台**：从只读 Dashboard 升级为可提交 Job 的实验工作台  

**局限与展望（诚实页）**：
- 当前 UI 回测默认均线策略；完整 Agent 流水线以 CLI 为主  
- 无券商接口、无实盘  
- 后续：更多策略、更强 Agent 编排、论文图表自动化  

---

### 三、建议幻灯片结构（可按此展开，允许微调）

请按以下结构生成逐页内容；每页若需配图，插入 `[配图占位：…]`。

| 页 | 建议标题 | 配图占位建议 |
|----|----------|--------------|
| 1 | 封面：Quant MAS 多智能体量化研究平台 | `[配图占位：项目 Logo 或 architecture.png 缩略]` |
| 2 | 汇报提纲 / Contents | 无 |
| 3 | 研究背景与动机：为什么做这个项目 | `[配图占位：量化研究 vs 实盘交易 对比示意图（双轨）]` |
| 4 | 问题定义：我们要解决什么 | 无或简单 icon |
| 5 | 一句话定位 + 安全边界（重要） | `[配图占位：红色徽章 Live trading disabled 的 UI 顶栏截图]` |
| 6 | 系统总体架构（分层） | `[配图占位：architecture.png 或自绘 8 层架构图]` |
| 7 | Quant Engine：量化研究流水线 | `[配图占位：Data→Features→Backtest→OOS 流程图]` |
| 8 | Agent 层：编排而非下单 | `[配图占位：Agents 页或 Supervisor 路由示意图]` |
| 9 | Web 控制平台 v5：企业研究工作台 | `[配图占位：Overview 全页截图]` |
| 10 | 功能模块地图（13+ 页面） | `[配图占位：Sidebar 导航截图]` |
| 11 | 核心 Demo：一次完整回测 | `[配图占位：Backtests 页 + Job Console completed 截图]` |
| 12 | 回测结果展示 | `[配图占位：权益曲线小图 + metrics 摘要]` |
| 13 | Walk-forward OOS 与论文级指标 | `[配图占位：OOS 页 + oos.sharpe 0.586 基线]` |
| 14 | Backtest vs OOS：为什么不能只报回测 | `[配图占位：Walk-forward 时间窗口滚动示意图]` |
| 15 | 风控、审计与人工审查 | `[配图占位：Risk Review 或 Audit Logs 截图]` |
| 16 | 实验成果与工程指标 | `[配图占位：361 tests passed / GitHub 徽章]` |
| 17 | 部署架构：本地前端 + 远程算力 | `[配图占位：SSH 隧道架构图（Windows↔Server）]` |
| 18 | 创新点与项目贡献 | 无或 icon 列表 |
| 19 | 局限性与后续工作 | 无 |
| 20 | 总结 | 无 |
| 21 | Q&A / 致谢 | `[配图占位：团队照片或学校 Logo（可选）]` |

---

### 四、配图清单（我会在 PPT 做好后自行插入）

请在 PPT 方案末尾，单独列出 **「配图插入 checklist」**，方便我对照拍摄/截图：

1. **architecture.png** — 仓库根目录官方架构图（架构页）
2. **UI-Overview.png** — 控制平台总览页（Server connected 状态）
3. **UI-Backtests-Job.png** — Backtests 页 + Job Console 完成状态
4. **UI-Equity-Chart.png** — 回测权益曲线区域（归一化柱状图）
5. **UI-OOS.png** — Walk-forward OOS 页指标
6. **UI-Risk-or-Audit.png** — Risk Review 或 Audit Logs
7. **UI-Help.png** — Help 使用指南页（体现文档化）
8. **Diagram-SSH-Tunnel.png** — 自绘或截图：本地 5173 → 隧道 8000 → 服务器
9. **Diagram-Backtest-vs-OOS.png** — Walk-forward 窗口滚动示意（可用 PPT 自绘）
10. **（可选）团队/答辩信息** — 学校、SRTP 编号、成员、导师

---

### 五、语气与受众

- **受众**：SRTP 指导教师、同学、可能含非技术评委  
- **语气**：严谨、清晰、不夸大；先讲「研究平台」再讲「技术细节」  
- **开场建议**：用「这不是自动炒股软件，而是可审计的量化研究工程」建立正确预期  
- **结尾建议**：强调可复现、可扩展、GitHub 开源、欢迎交流  

请现在开始生成完整 PPT 方案。

## --- 复制到这里结束 ---

---

## 附：本地可截图页面速查

制作 PPT 前，可在本地启动 `npm run dev` 并确保 **Server connected**，按下列路径截图：

| 占位编号 | 建议截图内容 | 对应菜单 |
|----------|--------------|----------|
| UI-Overview | 总览 KPI + 工作流 + 快捷入口 | Overview |
| UI-Backtests-Job | Run backtest 表单 + Job Console | Backtests |
| UI-Equity-Chart | 回测摘要卡片内权益曲线 | Backtests（Job 完成后 Refresh） |
| UI-OOS | OOS Sharpe 与窗口信息 | Walk-forward OOS |
| UI-Risk-or-Audit | Review Queue 或审计表 | Risk Review / Audit Logs |
| UI-Help | 左侧目录 + 某一章节正文 | Help |
| UI-Sidebar | 完整侧边栏导航 | 任意页 |

静态架构图：项目根目录 **`architecture.png`**（README 同款）。

---

## 附：若 ChatGPT 支持「直接生成 .pptx」时的补充指令（可选）

若对方支持生成 PowerPoint 文件，可在原提示词末尾追加：

```text
请输出 PowerPoint 可导入的大纲，并确保：
- 每页标题不超过 15 字
- 正文每行不超过 28 字
- 安全边界页使用醒目色块（红/橙标注「非实盘」）
- 架构页、Demo 页、Backtest vs OOS 对比页留 50% 以上面积给 [配图占位]
- 不要嵌入虚构数据截图
```
