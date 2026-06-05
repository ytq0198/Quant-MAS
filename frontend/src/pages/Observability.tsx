import { Badge } from "../components/Badge";
import { Card } from "../components/Card";
import { useLanguage } from "../i18n/LanguageContext";
import type { DashboardData } from "../hooks/useDashboardData";

export function Observability({ data, onRefresh }: { data: DashboardData; onRefresh: () => void }) {
  const { deepHealth, metricsSummary, recentLogs, jobs, effectiveConfig } = data;
  const { t } = useLanguage();

  return (
    <div className="page">
      <Card title={t("obs.health")} subtitle={`${deepHealth.service} · ${deepHealth.status}`}>
        <div className="badge-row">
          <Badge tone={deepHealth.research_only ? "success" : "warning"}>
            {t("obs.researchOnlyLabel")}: {deepHealth.research_only ? t("common.yes") : t("common.no")}
          </Badge>
        </div>
        <div className="stack compact">
          {(deepHealth.components ?? []).map((component) => (
            <div className="list-card" key={component.name}>
              <strong>{component.name}</strong>
              <p>{component.detail}</p>
              <Badge tone={component.status === "ok" ? "success" : "warning"}>{component.status}</Badge>
            </div>
          ))}
        </div>
      </Card>

      <div className="page--split">
        <Card title={t("obs.jobs")} subtitle={`${t("common.source")}: ${jobs.source}`}>
          <button type="button" className="btn btn--secondary" onClick={onRefresh} style={{ marginBottom: 12 }}>
            {t("common.refresh")}
          </button>
          <div className="stack compact">
            {(jobs.jobs ?? []).map((job) => (
              <div className="list-card" key={job.job_id}>
                <strong>{job.job_id}</strong>
                <p>{job.summary}</p>
                <span className="muted">
                  {job.type} · {job.status} · {Math.round((job.progress ?? 0) * 100)}%
                </span>
              </div>
            ))}
          </div>
        </Card>

        <Card title={t("obs.metrics")} subtitle={`${t("common.source")}: ${metricsSummary.source}`}>
          <dl className="metric-list compact">
            {Object.entries(metricsSummary.counters ?? {}).map(([key, value]) => (
              <div key={key}>
                <dt>{key.replace(/_/g, " ")}</dt>
                <dd>{value}</dd>
              </div>
            ))}
          </dl>
          <p className="muted">{metricsSummary.notes?.[0] ?? ""}</p>
        </Card>
      </div>

      <Card title={t("obs.logs")} subtitle={`Root: ${recentLogs.log_root}`}>
        {recentLogs.events.length === 0 ? (
          <p className="muted">{t("obs.noLogs")}</p>
        ) : (
          <pre className="console-panel compact">
            {recentLogs.events.slice(0, 8).map((event, i) => (
              <span key={i}>{JSON.stringify(event)}</span>
            ))}
          </pre>
        )}
      </Card>

      <Card title={t("obs.websocket")} subtitle={t("obs.websocketSubtitle")}>
        <p className="muted">{t("obs.websocketText")}</p>
      </Card>

      <Card title={t("obs.effectiveConfig")}>
        <p className="muted">
          {t("obs.configSummary", {
            auth: effectiveConfig.auth_mode,
            storage: effectiveConfig.storage_mode,
            vector: effectiveConfig.vector_store,
            live: effectiveConfig.live_trading_enabled ? t("common.yes") : t("safety.disabled")
          })}
        </p>
        <div className="chip-grid">
          {Object.entries(effectiveConfig.env ?? {}).slice(0, 10).map(([key, value]) => (
            <span className="chip" key={key}>
              {key}: {value || t("common.unset")}
            </span>
          ))}
        </div>
      </Card>
    </div>
  );
}
