import { postJson, readJson } from "./client";

export interface AgentInfo {
  name: string;
  role: string;
  live_trading_enabled: boolean;
  tools: string[];
}

export interface ToolInfo {
  name: string;
  description: string;
  allowed_operations: string[];
}

export interface MemoryItem {
  id: string;
  title: string;
  type: string;
  snippet: string;
}

export interface MemorySearchPayload {
  query: string;
  mode: string;
  results: MemoryItem[];
}

export const fallbackAgents: AgentInfo[] = [
  {
    name: "SupervisorAgent",
    role: "Routes research tasks and enforces tool policy.",
    live_trading_enabled: false,
    tools: ["DataSummaryTool", "PipelineTool", "ReportTool"]
  },
  {
    name: "ResearchAgent",
    role: "Summarizes experiments, retrieves memory, and drafts research notes.",
    live_trading_enabled: false,
    tools: ["BacktestTool", "MLBacktestTool", "RiskTool", "ReportTool"]
  },
  {
    name: "ReportAgent",
    role: "Turns audited experiment outputs into readable reports.",
    live_trading_enabled: false,
    tools: ["ReportTool"]
  }
];

export const fallbackTools: ToolInfo[] = [
  {
    name: "BacktestTool",
    description: "Runs deterministic backtest workflows through Quant Engine.",
    allowed_operations: ["run_backtest", "read_report"]
  },
  {
    name: "RiskTool",
    description: "Checks risk constraints before any candidate can move forward.",
    allowed_operations: ["run_risk_check", "read_decision"]
  },
  {
    name: "PipelineTool",
    description: "Runs configured YAML pipeline recipes under audit policy.",
    allowed_operations: ["run_pipeline", "dry_run", "read_audit"]
  }
];

export const fallbackMemory: MemorySearchPayload = {
  query: "OOS baseline",
  mode: "local-fallback",
  results: [
    {
      id: "memory-oos-baseline",
      title: "EXP-20260602-008 OOS baseline",
      type: "experiment",
      snippet: "Walk-forward OOS Sharpe = 0.586. Paper-grade baseline, not a trading promise."
    },
    {
      id: "memory-safety-boundary",
      title: "Safety boundary",
      type: "policy",
      snippet:
        "LLM agents do not place live orders. Candidates require backtest, risk check, audit log, and human confirmation."
    }
  ]
};

export function fetchAgents(): Promise<AgentInfo[]> {
  return readJson<AgentInfo[]>("/api/agents");
}

export function fetchTools(): Promise<ToolInfo[]> {
  return readJson<ToolInfo[]>("/api/tools");
}

export function fetchMemory(query: string): Promise<MemorySearchPayload> {
  return readJson<MemorySearchPayload>(`/api/memory/search?q=${encodeURIComponent(query)}`);
}

export interface AgentRunResult {
  agent: string;
  task: string;
  status: string;
  summary: string;
  live_trading_enabled: boolean;
}

export function runAgent(agent: string, task: string): Promise<AgentRunResult> {
  return postJson<AgentRunResult>("/api/agents/run", { agent, task });
}
