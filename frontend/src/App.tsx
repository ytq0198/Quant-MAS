import { useEffect, useState } from "react";

import { fallbackAuth, fetchAuthMe, type AuthMePayload } from "./api/auth";
import { getStoredApiKey, setStoredApiKey } from "./api/client";
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
import {
  fallbackDatabase,
  fallbackDeployment,
  fetchDatabaseStatus,
  fetchDeploymentStatus,
  type DatabaseStatus,
  type DeploymentStatus
} from "./api/phase4";
import {
  fallbackAuditLogs,
  fallbackExperiments,
  fallbackPaperArtifacts,
  fetchAuditLogs,
  fetchExperiments,
  fetchPaperArtifacts,
  type AuditLogsPayload,
  type ExperimentsPayload,
  type PaperArtifactsPayload
} from "./api/phase5";
import {
  fallbackJobs,
  fallbackReviewQueue,
  fetchJobs,
  fetchReviewQueue,
  type JobsPayload,
  type ReviewQueuePayload
} from "./api/phase7";
import {
  fallbackDatabaseTables,
  fallbackGraph,
  fallbackRagDocuments,
  fetchDatabaseTables,
  fetchGraphRelationships,
  fetchRagDocuments,
  type DatabaseTablesPayload,
  type GraphRelationshipsPayload,
  type RagDocumentsPayload
} from "./api/phase8";
import {
  fallbackDeepHealth,
  fallbackEffectiveConfig,
  fallbackMetricsSummary,
  fallbackRecentLogs,
  fetchDeepHealth,
  fetchEffectiveConfig,
  fetchMetricsSummary,
  fetchRecentLogs,
  type DeepHealthPayload,
  type EffectiveConfigPayload,
  type MetricsSummaryPayload,
  type RecentLogsPayload
} from "./api/phase9";
import { fetchStatus, fallbackStatus, type StatusPayload } from "./api/status";

export function App() {
  const [status, setStatus] = useState<StatusPayload>(fallbackStatus);
  const [agents, setAgents] = useState<AgentInfo[]>(fallbackAgents);
  const [tools, setTools] = useState<ToolInfo[]>(fallbackTools);
  const [memory, setMemory] = useState<MemorySearchPayload>(fallbackMemory);
  const [backtest, setBacktest] = useState<BacktestSummary>(fallbackBacktest);
  const [oos, setOos] = useState<OosSummary>(fallbackOos);
  const [risk, setRisk] = useState<RiskSummary>(fallbackRisk);
  const [database, setDatabase] = useState<DatabaseStatus>(fallbackDatabase);
  const [deployment, setDeployment] = useState<DeploymentStatus>(fallbackDeployment);
  const [experiments, setExperiments] = useState<ExperimentsPayload>(fallbackExperiments);
  const [paperArtifacts, setPaperArtifacts] = useState<PaperArtifactsPayload>(fallbackPaperArtifacts);
  const [auditLogs, setAuditLogs] = useState<AuditLogsPayload>(fallbackAuditLogs);
  const [auth, setAuth] = useState<AuthMePayload>(fallbackAuth);
  const [reviewQueue, setReviewQueue] = useState<ReviewQueuePayload>(fallbackReviewQueue);
  const [jobs, setJobs] = useState<JobsPayload>(fallbackJobs);
  const [databaseTables, setDatabaseTables] = useState<DatabaseTablesPayload>(fallbackDatabaseTables);
  const [ragDocuments, setRagDocuments] = useState<RagDocumentsPayload>(fallbackRagDocuments);
  const [graph, setGraph] = useState<GraphRelationshipsPayload>(fallbackGraph);
  const [deepHealth, setDeepHealth] = useState<DeepHealthPayload>(fallbackDeepHealth);
  const [metricsSummary, setMetricsSummary] = useState<MetricsSummaryPayload>(fallbackMetricsSummary);
  const [recentLogs, setRecentLogs] = useState<RecentLogsPayload>(fallbackRecentLogs);
  const [effectiveConfig, setEffectiveConfig] = useState<EffectiveConfigPayload>(fallbackEffectiveConfig);
  const [apiKeyDraft, setApiKeyDraft] = useState<string>(() => getStoredApiKey());
  const [source, setSource] = useState<"api" | "fallback">("fallback");

  useEffect(() => {
    void loadDashboard();
  }, []);

  function saveApiKey() {
    setStoredApiKey(apiKeyDraft);
    void loadDashboard();
  }

  function clearApiKey() {
    setApiKeyDraft("");
    setStoredApiKey("");
    void loadDashboard();
  }

  async function loadDashboard() {
    Promise.all([
      fetchAuthMe(),
      fetchStatus(),
      fetchAgents(),
      fetchTools(),
      fetchMemory("OOS baseline"),
      fetchBacktestSummary(),
      fetchOosSummary(),
      fetchRiskSummary(),
      fetchDatabaseStatus(),
      fetchDeploymentStatus(),
      fetchExperiments(),
      fetchPaperArtifacts(),
      fetchAuditLogs(),
      fetchReviewQueue(),
      fetchJobs(),
      fetchDatabaseTables(),
      fetchRagDocuments(),
      fetchGraphRelationships(),
      fetchDeepHealth(),
      fetchMetricsSummary(),
      fetchRecentLogs(),
      fetchEffectiveConfig()
    ])
      .then(([
        authPayload,
        statusPayload,
        agentPayload,
        toolPayload,
        memoryPayload,
        backtestPayload,
        oosPayload,
        riskPayload,
        databasePayload,
        deploymentPayload,
        experimentsPayload,
        paperPayload,
        auditPayload,
        reviewPayload,
        jobsPayload,
        databaseTablesPayload,
        ragPayload,
        graphPayload,
        deepHealthPayload,
        metricsPayload,
        logsPayload,
        configPayload
      ]) => {
        setAuth(authPayload);
        setStatus(statusPayload);
        setAgents(agentPayload);
        setTools(toolPayload);
        setMemory(memoryPayload);
        setBacktest(backtestPayload);
        setOos(oosPayload);
        setRisk(riskPayload);
        setDatabase(databasePayload);
        setDeployment(deploymentPayload);
        setExperiments(experimentsPayload);
        setPaperArtifacts(paperPayload);
        setAuditLogs(auditPayload);
        setReviewQueue(reviewPayload);
        setJobs(jobsPayload);
        setDatabaseTables(databaseTablesPayload);
        setRagDocuments(ragPayload);
        setGraph(graphPayload);
        setDeepHealth(deepHealthPayload);
        setMetricsSummary(metricsPayload);
        setRecentLogs(logsPayload);
        setEffectiveConfig(configPayload);
        setSource("api");
      })
      .catch(() => {
        setAuth(fallbackAuth);
        setStatus(fallbackStatus);
        setAgents(fallbackAgents);
        setTools(fallbackTools);
        setMemory(fallbackMemory);
        setBacktest(fallbackBacktest);
        setOos(fallbackOos);
        setRisk(fallbackRisk);
        setDatabase(fallbackDatabase);
        setDeployment(fallbackDeployment);
        setExperiments(fallbackExperiments);
        setPaperArtifacts(fallbackPaperArtifacts);
        setAuditLogs(fallbackAuditLogs);
        setReviewQueue(fallbackReviewQueue);
        setJobs(fallbackJobs);
        setDatabaseTables(fallbackDatabaseTables);
        setRagDocuments(fallbackRagDocuments);
        setGraph(fallbackGraph);
        setDeepHealth(fallbackDeepHealth);
        setMetricsSummary(fallbackMetricsSummary);
        setRecentLogs(fallbackRecentLogs);
        setEffectiveConfig(fallbackEffectiveConfig);
        setSource("fallback");
      });
  }

  return (
    <main className="app-shell">
      <section className="hero">
        <div>
          <p className="eyebrow">Quant MAS v5 Enterprise Preview</p>
          <h1>{status.project}</h1>
          <p className="hero-copy">{status.description}</p>
        </div>
        <div className="status-panel">
          <span className={`status-dot ${source}`} />
          <span>{source === "api" ? "Connected to backend API" : "Using local UI fallback"}</span>
        </div>
      </section>

      <section className="panel access-panel">
        <div>
          <h2>API Access</h2>
          <p className="muted">
            Mode: {auth.auth_mode} · Role: {auth.role}
            {auth.key_fingerprint ? ` · ${auth.key_fingerprint}` : ""}
          </p>
        </div>
        <div className="access-controls">
          <input
            aria-label="Quant MAS API key"
            placeholder="X-Quant-MAS-Key"
            type="password"
            value={apiKeyDraft}
            onChange={(event) => setApiKeyDraft(event.target.value)}
          />
          <button type="button" onClick={saveApiKey}>
            Save
          </button>
          <button type="button" onClick={clearApiKey}>
            Clear
          </button>
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

      <section className="grid">
        <article className="panel">
          <h2>Database Backends</h2>
          <p className="muted">Mode: {database.mode} · Default: {database.default_backend}</p>
          <div className="module-grid">
            {database.backends.map((backend) => (
              <span className="module-pill" key={backend.name}>
                {backend.name}: {backend.status}
              </span>
            ))}
          </div>
        </article>

        <article className="panel">
          <h2>Deployment Skeleton</h2>
          <p className="muted">
            {deployment.frontend.stack} · {deployment.backend.stack}
          </p>
          <div className="module-grid">
            {deployment.artifacts.map((artifact) => (
              <span className="module-pill" key={artifact}>
                {artifact}
              </span>
            ))}
          </div>
        </article>
      </section>

      <section className="phase-grid">
        <article className="panel">
          <h2>Experiment Registry</h2>
          <p className="muted">Source: {experiments.source}</p>
          <div className="stack">
            {experiments.experiments.slice(0, 3).map((experiment) => (
              <div className="list-card" key={experiment.experiment_id}>
                <strong>{experiment.experiment_id}</strong>
                <p>{experiment.name}</p>
                <span>OOS: {experiment.metric_family_summary.oos ? "yes" : "no"}</span>
              </div>
            ))}
          </div>
        </article>

        <article className="panel">
          <h2>Paper Artifacts</h2>
          <p className="muted">Source: {paperArtifacts.source} · Count: {paperArtifacts.artifacts.length}</p>
          <div className="module-grid">
            {(paperArtifacts.artifacts.length ? paperArtifacts.artifacts : [{ name: "No paper artifacts loaded yet" }]).map(
              (artifact) => (
                <span className="module-pill" key={artifact.name}>
                  {artifact.name}
                </span>
              )
            )}
          </div>
        </article>

        <article className="panel">
          <h2>Audit Logs</h2>
          <p className="muted">Source: {auditLogs.source} · Events: {auditLogs.events.length}</p>
          <p className="safety-state">
            Server mode reads JSONL audit events when `QUANT_MAS_AUDIT_DIR` or artifact root is configured.
          </p>
        </article>
      </section>

      <section className="grid">
        <article className="panel">
          <h2>Human Review Queue</h2>
          <p className="muted">Source: {reviewQueue.source} · Pending: {reviewQueue.reviews.length}</p>
          <div className="stack">
            {reviewQueue.reviews.slice(0, 2).map((review) => (
              <div className="list-card" key={review.review_id}>
                <strong>{review.review_id}</strong>
                <p>{review.summary}</p>
                <span>{review.metric_family} · {review.status}</span>
              </div>
            ))}
          </div>
        </article>

        <article className="panel">
          <h2>Job Status</h2>
          <p className="muted">Source: {jobs.source}</p>
          <div className="stack">
            {jobs.jobs.slice(0, 2).map((job) => (
              <div className="list-card" key={job.job_id}>
                <strong>{job.job_id}</strong>
                <p>{job.summary}</p>
                <span>{job.type} · {job.status} · {Math.round(job.progress * 100)}%</span>
              </div>
            ))}
          </div>
        </article>
      </section>

      <section className="phase-grid">
        <article className="panel">
          <h2>Database Tables</h2>
          <p className="muted">Mode: {databaseTables.mode} · Status: {databaseTables.status}</p>
          <div className="module-grid">
            {databaseTables.tables.slice(0, 5).map((table) => (
              <span className="module-pill" key={table}>
                {table}
              </span>
            ))}
          </div>
        </article>

        <article className="panel">
          <h2>RAG Documents</h2>
          <p className="muted">Source: {ragDocuments.source} · Store: {ragDocuments.vector_store}</p>
          <div className="stack">
            {ragDocuments.documents.slice(0, 2).map((document) => (
              <div className="list-card" key={document.document_id}>
                <strong>{document.title}</strong>
                <p>{document.snippet}</p>
                <span>{document.type}</span>
              </div>
            ))}
          </div>
        </article>

        <article className="panel">
          <h2>Graph Relationships</h2>
          <p className="muted">Source: {graph.source}</p>
          <div className="stack">
            {graph.relationships.slice(0, 2).map((relationship) => (
              <div className="list-card" key={`${relationship.source}-${relationship.relation}-${relationship.target}`}>
                <strong>{relationship.source}</strong>
                <p>{relationship.relation}</p>
                <span>{relationship.target}</span>
              </div>
            ))}
          </div>
        </article>
      </section>

      <section className="phase-grid">
        <article className="panel">
          <h2>System Health</h2>
          <p className="muted">
            {deepHealth.service} | Status: {deepHealth.status} | Research-only:{" "}
            {deepHealth.research_only ? "yes" : "no"}
          </p>
          <div className="stack">
            {deepHealth.components.slice(0, 3).map((component) => (
              <div className="list-card" key={component.name}>
                <strong>{component.name}</strong>
                <p>{component.detail}</p>
                <span>{component.status}</span>
              </div>
            ))}
          </div>
        </article>

        <article className="panel">
          <h2>Metrics Summary</h2>
          <p className="muted">Source: {metricsSummary.source}</p>
          <dl className="metric-list compact">
            {Object.entries(metricsSummary.counters).slice(0, 3).map(([key, value]) => (
              <div key={key}>
                <dt>{key.replace(/_/g, " ")}</dt>
                <dd>{value}</dd>
              </div>
            ))}
          </dl>
          <p className="muted">{metricsSummary.notes[0]}</p>
        </article>

        <article className="panel">
          <h2>Server Logs</h2>
          <p className="muted">Source: {recentLogs.source} | Root: {recentLogs.log_root}</p>
          <p className="safety-state">Recent events: <strong>{recentLogs.events.length}</strong></p>
          <p className="muted">
            Server deployments can point `QUANT_MAS_LOG_ROOT` at JSONL audit or service logs.
          </p>
        </article>
      </section>

      <section className="panel">
        <h2>Effective Config</h2>
        <p className="muted">
          Auth: {effectiveConfig.auth_mode} | Storage: {effectiveConfig.storage_mode} | Vector:{" "}
          {effectiveConfig.vector_store} | Live trading: {effectiveConfig.live_trading_enabled ? "yes" : "no"}
        </p>
        <div className="module-grid">
          {Object.entries(effectiveConfig.env).slice(0, 8).map(([key, value]) => (
            <span className="module-pill" key={key}>
              {key}: {value || "unset"}
            </span>
          ))}
        </div>
      </section>
    </main>
  );
}
