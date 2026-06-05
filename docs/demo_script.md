# Quant MAS v5 Demo Script / 演示脚本

This script is for a project demo, interview walkthrough, or team review. It avoids real-data claims unless the server has already been validated by Cursor/server tests.

该脚本适合项目演示、面试讲解或团队评审。除非服务器已由 Cursor/服务器测试验证，否则不使用真实数据结论。

## 1. Opening / 开场

English:
Quant MAS is a research-only multi-agent quantitative research platform. It combines deterministic quant pipelines with AI Agent orchestration, Memory/RAG, audit logs, and human review gates. The system is useful for AI Agent, Quant, and Financial AI internship practice.

中文：
Quant MAS 是一个研究型多智能体量化研究平台。它把确定性量化流水线与 AI Agent 编排、Memory/RAG、审计日志和人工审核关卡结合起来，适合 AI Agent、Quant 和 Financial AI 实习项目练习。

## 2. Architecture / 架构

English:
The architecture separates data, quant engine, research experiments, Memory/RAG, tools, agents, orchestration, and human review. The safety boundary is explicit: agents can plan, retrieve, call approved tools, and summarize evidence, but they do not place live orders.

中文：
架构分为数据层、量化引擎、研究实验层、Memory/RAG、工具层、智能体层、编排层和人工审核层。安全边界很明确：智能体可以规划、检索、调用授权工具并总结证据，但不直接下单。

## 3. Dashboard Walkthrough / 仪表盘讲解

English:
Show the backend connection state, research baseline, safety boundary, agent/tool/memory panels, backtest/OOS/risk panels, artifact panels, review queue, optional database/RAG/graph panels, and observability panels.

中文：
依次展示后端连接状态、研究基线、安全边界、智能体/工具/记忆面板、回测/OOS/风险面板、产物面板、审核队列、可选数据库/RAG/图谱面板和可观测性面板。

## 4. Server Mode / 服务器模式

English:
In server mode, the backend can run with API key authentication and read real experiment artifacts from configured output directories. Local fallback remains available so development does not depend on server data.

中文：
服务器模式下，后端可以启用 API Key 认证，并从配置的输出目录读取真实实验产物。本地 fallback 仍然保留，因此开发不依赖服务器真实数据。

## 5. Evidence Boundary / 证据边界

English:
The OOS baseline is `EXP-20260602-008`, Sharpe `0.586`, across 19 walk-forward windows. This is a historical research baseline. Backtest, simulation, training, population, and audit metrics are different metric families and must not be mixed with OOS conclusions.

中文：
当前 OOS 基线是 `EXP-20260602-008`，Sharpe `0.586`，包含 19 个 Walk-forward 窗口。这是历史研究基线。回测、仿真、训练、种群和审计指标属于不同指标族，不能与 OOS 结论混用。

## 6. Closing / 收尾

English:
The value of the project is not automatic trading. The value is showing how to design a safe, auditable, extensible AI Agent + Quant Research system that can be deployed, reviewed, and extended.

中文：
项目价值不是自动交易，而是展示如何设计一个安全、可审计、可扩展、可部署、可评审的 AI Agent + Quant Research 系统。
