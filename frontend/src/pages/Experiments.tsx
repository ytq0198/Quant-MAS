import { useState } from "react";

import { Badge, MetricFamilyBadge } from "../components/Badge";
import { Card, EmptyState } from "../components/Card";
import { ResearchJobPanel } from "../components/ResearchJobPanel";
import { useLanguage } from "../i18n/LanguageContext";
import type { DashboardData } from "../hooks/useDashboardData";
import type { ExperimentRecord } from "../api/phase5";

export function Experiments({ data, onRefresh }: { data: DashboardData; onRefresh: () => void }) {
  const { experiments, source } = data;
  const { t } = useLanguage();
  const [selectedId, setSelectedId] = useState(
    experiments.experiments[0]?.experiment_id ?? "EXP-20260602-008"
  );
  const selected = experiments.experiments.find((e) => e.experiment_id === selectedId);

  return (
    <div className="page page--split">
      <Card
        title={t("experiments.registry")}
        subtitle={`${t("common.source")}: ${experiments.source} · ${
          source === "api" ? t("common.server") : t("common.fallback")
        }`}
      >
        {experiments.experiments.length === 0 ? (
          <EmptyState title={t("experiments.emptyTitle")} description={t("experiments.emptyDesc")} />
        ) : (
          <div className="table-wrap">
            <table className="data-table">
              <thead>
                <tr>
                  <th>{t("experiments.colId")}</th>
                  <th>{t("experiments.colTitle")}</th>
                  <th>{t("experiments.colMetricFamily")}</th>
                  <th>{t("experiments.colOosAvailable")}</th>
                  <th>{t("experiments.colStatus")}</th>
                </tr>
              </thead>
              <tbody>
                {experiments.experiments.map((row) => (
                  <tr
                    key={row.experiment_id}
                    className={row.experiment_id === selectedId ? "data-table__row--active" : ""}
                    onClick={() => setSelectedId(row.experiment_id)}
                  >
                    <td className="mono">{row.experiment_id}</td>
                    <td>{row.name}</td>
                    <td>
                      {row.metric_family_summary.oos ? (
                        <MetricFamilyBadge family="oos" />
                      ) : (
                        <MetricFamilyBadge family="research" />
                      )}
                    </td>
                    <td>{row.metric_family_summary.oos ? t("common.yes") : t("common.no")}</td>
                    <td>
                      <Badge tone={row.status === "documented" ? "success" : "default"}>{row.status}</Badge>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>

      <Card title={t("experiments.summary")}>
        {selected ? (
          <ExperimentDetail experiment={selected} />
        ) : (
          <EmptyState title={t("experiments.selectTitle")} description={t("experiments.selectDesc")} />
        )}
      </Card>

      <ResearchJobPanel jobType="backtest" onComplete={onRefresh} />
    </div>
  );
}

function ExperimentDetail({ experiment }: { experiment: ExperimentRecord }) {
  const { t } = useLanguage();
  const oosMetrics = experiment.metrics.oos as { sharpe?: number; window_count?: number } | undefined;

  return (
    <div className="detail-stack">
      <p className="mono">{experiment.experiment_id}</p>
      <h3>{experiment.name}</h3>
      <p className="muted">{experiment.notes}</p>
      <div className="badge-row">
        <MetricFamilyBadge family="oos" />
        <Badge tone="muted">{experiment.status}</Badge>
      </div>
      {oosMetrics && (
        <dl className="metric-list">
          <div>
            <dt>{t("experiments.sharpe")}</dt>
            <dd>{oosMetrics.sharpe?.toFixed(3) ?? "—"}</dd>
          </div>
          <div>
            <dt>{t("experiments.windows")}</dt>
            <dd>{oosMetrics.window_count ?? "—"}</dd>
          </div>
        </dl>
      )}
    </div>
  );
}
