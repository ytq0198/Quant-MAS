import { useEffect, useState } from "react";

import {
  fetchAgents,
  fetchMemory,
  fetchTools,
  fallbackAgents,
  fallbackMemory,
  fallbackTools,
  type AgentInfo,
  type MemorySearchPayload,
  type ToolInfo
} from "./api/phase2";
import {
  fallbackBacktest,
  fallbackOos,
  fallbackRisk,
  fetchBacktestSummary,
  fetchOosSummary,
  fetchRiskSummary,
  type BacktestSummary,
  type OosSummary,
  type RiskSummary
} from "./api/phase3";
import { fetchStatus, fallbackStatus, type StatusPayload } from "./api/status";

export function App() {
  const [status, setStatus] = useState<StatusPayload>(fallbackStatus);
  const [agents, setAgents] = useState<AgentInfo[]>(fallbackAgents);
  const [tools, setTools] = useState<ToolInfo[]>(fallbackTools);
  const [memory, setMemory] = useState<MemorySearchPayload>(fallbackMemory);
  const [backtest, setBacktest] = useState<BacktestSummary>(fallbackBacktest);
  const [oos, setOos] = useState<OosSummary>(fallbackOos);
  const [risk, setRisk] = useState<RiskSummary>(fallbackRisk);
  const [source, setSource] = useState<"api" | "fallback">("fallback");

  useEffect(() => {
    Promise.all([
      fetchStatus(),
      fetchAgents(),
      fetchTools(),
      fetchMemory("OOS baseline"),
      fetchBacktestSummary(),
      fetchOosSummary(),
      fetchRiskSummary()
    ])
      .then(([statusPayload, agentPayload, toolPayload, memoryPayload, backtestPayload, oosPayload, riskPayload]) => {
        setStatus(statusPayload);
        setAgents(agentPayload);
        setTools(toolPayload);
        setMemory(memoryPayload);
        setBacktest(backtestPayload);
        setOos(oosPayload);
        setRisk(riskPayload);
        setSource("api");
      })
      .catch(() => {
        setStatus(fallbackStatus);
        setAgents(fallbackAgents);
        setTools(fallbackTools);
        setMemory(fallbackMemory);
        setBacktest(fallbackBacktest);
        setOos(fallbackOos);
        setRisk(fallbackRisk);
        setSource("fallback");
      });
  }, []);

  return (
    <main className="app-shell">
      <section className="hero">
        <div>
          <p className="eyebrow">Quant MAS v4 Full-stack Preview</p>
          <h1>{status.project}</h1>
          <p className="hero-copy">{status.description}</p>
        </div>
        <div className="status-panel">
          <span className={`status-dot ${source}`} />
          <span>{source === "api" ? "Connected to backend API" : "Using local UI fallback"}</span>
        </div>
      </section>

      <section className="grid">
        <article className="panel">
          <h2>Research Baseline</h2>
          <dl className="metric-list">
            <div>
              <dt>Tests</dt>
              <dd>{status.baselines.tests}</dd>
            </div>
            <div>
              <dt>OOS Experiment</dt>
              <dd>{status.baselines.oos_experiment}</dd>
            </div>
            <div>
              <dt>OOS Sharpe</dt>
              <dd>{status.baselines.oos_sharpe.toFixed(3)}</dd>
            </div>
          </dl>
        </article>

        <article className="panel">
          <h2>Safety Boundary</h2>
          <p className="safety-state">
            Live trading enabled: <strong>{status.safety.live_trading ? "yes" : "no"}</strong>
          </p>
          <ul className="check-list">
            {status.safety.principles.map((principle) => (
              <li key={principle}>{principle}</li>
            ))}
          </ul>
        </article>
      </section>

      <section className="panel">
        <h2>Planned UI Modules</h2>
        <div className="module-grid">
          {status.ui_modules.map((module) => (
            <span className="module-pill" key={module}>
              {module}
            </span>
          ))}
        </div>
      </section>

      <section className="phase-grid">
        <article className="panel">
          <h2>Agents</h2>
          <div className="stack">
            {agents.map((agent) => (
              <div className="list-card" key={agent.name}>
                <strong>{agent.name}</strong>
                <p>{agent.role}</p>
                <span>Live trading: {agent.live_trading_enabled ? "enabled" : "disabled"}</span>
              </div>
            ))}
          </div>
        </article>

        <article className="panel">
          <h2>Controlled Tools</h2>
          <div className="stack">
            {tools.map((tool) => (
              <div className="list-card" key={tool.name}>
                <strong>{tool.name}</strong>
                <p>{tool.description}</p>
                <span>{tool.allowed_operations.join(" · ")}</span>
              </div>
            ))}
          </div>
        </article>

        <article className="panel">
          <h2>Memory/RAG Search</h2>
          <p className="muted">Query: {memory.query || "latest research context"} · Mode: {memory.mode}</p>
          <div className="stack">
            {memory.results.map((item) => (
              <div className="list-card" key={item.id}>
                <strong>{item.title}</strong>
                <p>{item.snippet}</p>
                <span>{item.type}</span>
              </div>
            ))}
          </div>
        </article>
      </section>

      <section className="phase-grid">
        <article className="panel">
          <h2>Backtest Summary</h2>
          <p className="muted">{backtest.title} · {backtest.metric_family}</p>
          <div className="spark-bars" aria-label="Backtest equity preview">
            {backtest.chart.map((point) => (
              <span
                key={point.label}
                title={`${point.label}: ${point.equity}`}
                style={{ height: `${Math.max(18, point.equity * 42)}px` }}
              />
            ))}
          </div>
          <p className="safety-state">OOS metric: <strong>{backtest.is_oos ? "yes" : "no"}</strong></p>
          <p className="muted">{backtest.disclaimer}</p>
        </article>

        <article className="panel">
          <h2>Walk-forward OOS</h2>
          <dl className="metric-list compact">
            <div>
              <dt>Sharpe</dt>
              <dd>{oos.sharpe.toFixed(3)}</dd>
            </div>
            <div>
              <dt>Windows</dt>
              <dd>{oos.window_count}</dd>
            </div>
            <div>
              <dt>Paper grade</dt>
              <dd>{oos.paper_grade ? "yes" : "no"}</dd>
            </div>
          </dl>
          <p className="muted">{oos.notes[0]}</p>
        </article>

        <article className="panel">
          <h2>Risk Review</h2>
          <p className="safety-state">Status: <strong>{risk.status}</strong></p>
          <ul className="check-list">
            {risk.checks.map((check) => (
              <li key={check.name}>{check.name}: {check.status}</li>
            ))}
          </ul>
          <p className="muted">{risk.decision}</p>
        </article>
      </section>
    </main>
  );
}
