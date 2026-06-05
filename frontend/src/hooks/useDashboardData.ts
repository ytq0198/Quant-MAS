import { useCallback, useEffect, useState } from "react";

import { fallbackAuth, fetchAuthMe, type AuthMePayload } from "../api/auth";
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
} from "../api/phase2";
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
} from "../api/phase3";
import {
  fallbackDatabase,
  fallbackDeployment,
  fetchDatabaseStatus,
  fetchDeploymentStatus,
  type DatabaseStatus,
  type DeploymentStatus
} from "../api/phase4";
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
} from "../api/phase5";
import {
  fallbackJobs,
  fetchJobs,
  type JobsPayload
} from "../api/jobs";
import {
  fallbackReviewQueue,
  fetchReviewQueue,
  type ReviewQueuePayload
} from "../api/review";
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
} from "../api/phase8";
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
} from "../api/phase9";
import { fetchStatus, fallbackStatus, type StatusPayload } from "../api/status";

export interface DashboardData {
  status: StatusPayload;
  auth: AuthMePayload;
  agents: AgentInfo[];
  tools: ToolInfo[];
  memory: MemorySearchPayload;
  backtest: BacktestSummary;
  oos: OosSummary;
  risk: RiskSummary;
  database: DatabaseStatus;
  deployment: DeploymentStatus;
  experiments: ExperimentsPayload;
  paperArtifacts: PaperArtifactsPayload;
  auditLogs: AuditLogsPayload;
  reviewQueue: ReviewQueuePayload;
  jobs: JobsPayload;
  databaseTables: DatabaseTablesPayload;
  ragDocuments: RagDocumentsPayload;
  graph: GraphRelationshipsPayload;
  deepHealth: DeepHealthPayload;
  metricsSummary: MetricsSummaryPayload;
  recentLogs: RecentLogsPayload;
  effectiveConfig: EffectiveConfigPayload;
  source: "api" | "fallback";
  loading: boolean;
  refresh: () => Promise<void>;
}

export function useDashboardData(memoryQuery = "OOS baseline"): DashboardData {
  const [status, setStatus] = useState(fallbackStatus);
  const [auth, setAuth] = useState(fallbackAuth);
  const [agents, setAgents] = useState(fallbackAgents);
  const [tools, setTools] = useState(fallbackTools);
  const [memory, setMemory] = useState(fallbackMemory);
  const [backtest, setBacktest] = useState(fallbackBacktest);
  const [oos, setOos] = useState(fallbackOos);
  const [risk, setRisk] = useState(fallbackRisk);
  const [database, setDatabase] = useState(fallbackDatabase);
  const [deployment, setDeployment] = useState(fallbackDeployment);
  const [experiments, setExperiments] = useState(fallbackExperiments);
  const [paperArtifacts, setPaperArtifacts] = useState(fallbackPaperArtifacts);
  const [auditLogs, setAuditLogs] = useState(fallbackAuditLogs);
  const [reviewQueue, setReviewQueue] = useState(fallbackReviewQueue);
  const [jobs, setJobs] = useState(fallbackJobs);
  const [databaseTables, setDatabaseTables] = useState(fallbackDatabaseTables);
  const [ragDocuments, setRagDocuments] = useState(fallbackRagDocuments);
  const [graph, setGraph] = useState(fallbackGraph);
  const [deepHealth, setDeepHealth] = useState(fallbackDeepHealth);
  const [metricsSummary, setMetricsSummary] = useState(fallbackMetricsSummary);
  const [recentLogs, setRecentLogs] = useState(fallbackRecentLogs);
  const [effectiveConfig, setEffectiveConfig] = useState(fallbackEffectiveConfig);
  const [source, setSource] = useState<"api" | "fallback">("fallback");
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(async () => {
    setLoading(true);
    try {
      const [
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
      ] = await Promise.all([
        fetchAuthMe(),
        fetchStatus(),
        fetchAgents(),
        fetchTools(),
        fetchMemory(memoryQuery),
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
      ]);
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
    } catch {
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
    } finally {
      setLoading(false);
    }
  }, [memoryQuery]);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  return {
    status,
    auth,
    agents,
    tools,
    memory,
    backtest,
    oos,
    risk,
    database,
    deployment,
    experiments,
    paperArtifacts,
    auditLogs,
    reviewQueue,
    jobs,
    databaseTables,
    ragDocuments,
    graph,
    deepHealth,
    metricsSummary,
    recentLogs,
    effectiveConfig,
    source,
    loading,
    refresh
  };
}

export type { DashboardData as DashboardState };
