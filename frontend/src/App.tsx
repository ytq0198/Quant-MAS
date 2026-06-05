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
import { fetchStatus, fallbackStatus, type StatusPayload } from "./api/status";

export function App() {
  const [status, setStatus] = useState<StatusPayload>(fallbackStatus);
  const [agents, setAgents] = useState<AgentInfo[]>(fallbackAgents);
  const [tools, setTools] = useState<ToolInfo[]>(fallbackTools);
  const [memory, setMemory] = useState<MemorySearchPayload>(fallbackMemory);
  const [source, setSource] = useState<"api" | "fallback">("fallback");

  useEffect(() => {
    Promise.all([fetchStatus(), fetchAgents(), fetchTools(), fetchMemory("OOS baseline")])
      .then(([statusPayload, agentPayload, toolPayload, memoryPayload]) => {
        setStatus(statusPayload);
        setAgents(agentPayload);
        setTools(toolPayload);
        setMemory(memoryPayload);
        setSource("api");
      })
      .catch(() => {
        setStatus(fallbackStatus);
        setAgents(fallbackAgents);
        setTools(fallbackTools);
        setMemory(fallbackMemory);
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
    </main>
  );
}
