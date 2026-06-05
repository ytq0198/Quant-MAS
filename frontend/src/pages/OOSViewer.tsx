import { Badge, MetricFamilyBadge } from "../components/Badge";
import { Card } from "../components/Card";
import { ResearchJobPanel } from "../components/ResearchJobPanel";
import { useLanguage } from "../i18n/LanguageContext";
import type { DashboardData } from "../hooks/useDashboardData";

export function OOSViewer({ data, onRefresh }: { data: DashboardData; onRefresh: () => void }) {
  const { oos } = data;
  const { t } = useLanguage();

  return (
    <div className="page">
      <Card title={oos.title} subtitle={oos.id}>
        <div className="badge-row">
          <MetricFamilyBadge family="oos" />
          <Badge tone={oos.paper_grade ? "success" : "warning"}>
            {t("oos.paperGradeLabel")}: {oos.paper_grade ? t("common.yes") : t("common.no")}
          </Badge>
        </div>

        <dl className="metric-list kpi-inline">
          <div>
            <dt>{t("experiments.sharpe")}</dt>
            <dd className="metric-highlight">{oos.sharpe.toFixed(3)}</dd>
          </div>
          <div>
            <dt>{t("experiments.windows")}</dt>
            <dd>{oos.window_count}</dd>
          </div>
          <div>
            <dt>{t("backtests.metricFamily")}</dt>
            <dd>{oos.metric_family}.*</dd>
          </div>
        </dl>

        <p className="muted">{oos.notes[0]}</p>

        <h4 className="section-title">{t("oos.windowsTitle")}</h4>
        <div className="table-wrap">
          <table className="data-table">
            <thead>
              <tr>
                <th>{t("oos.colWindow")}</th>
                <th>{t("oos.colStatus")}</th>
              </tr>
            </thead>
            <tbody>
              {oos.windows.map((row) => (
                <tr key={row.window}>
                  <td className="mono">{row.window}</td>
                  <td>
                    <Badge tone={row.status === "completed" ? "success" : "muted"}>{row.status}</Badge>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>

      <ResearchJobPanel jobType="walk_forward_oos" onComplete={onRefresh} />
    </div>
  );
}
