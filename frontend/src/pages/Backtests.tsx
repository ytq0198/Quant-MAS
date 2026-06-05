import { Badge, MetricFamilyBadge } from "../components/Badge";
import { Card } from "../components/Card";
import { ResearchJobPanel } from "../components/ResearchJobPanel";
import { useLanguage } from "../i18n/LanguageContext";
import type { DashboardData } from "../hooks/useDashboardData";

export function Backtests({ data, onRefresh }: { data: DashboardData; onRefresh: () => void }) {
  const { backtest } = data;
  const { t } = useLanguage();

  return (
    <div className="page">
      <div className="page-banner page-banner--warning">
        <Badge tone="warning">{t("safety.researchOnly")}</Badge>
        <span>{t("backtests.warning")}</span>
      </div>

      <Card title={backtest.title} subtitle={`${t("backtests.strategy")}: ${backtest.strategy}`}>
        <div className="badge-row">
          <MetricFamilyBadge family="simulation" />
          <Badge tone="muted">{t("safety.nonOos")}</Badge>
          <Badge tone="danger">{t("safety.liveTradingDisabled")}</Badge>
        </div>
        <p className="muted">{backtest.disclaimer}</p>

        <div className="chart-placeholder" aria-label={t("backtests.equityChart")}>
          {backtest.chart.map((point) => (
            <span
              key={point.label}
              title={`${point.label}: ${point.equity}`}
              style={{ height: `${Math.max(24, point.equity * 48)}px` }}
            />
          ))}
        </div>

        <dl className="metric-list">
          <div>
            <dt>{t("backtests.metricFamily")}</dt>
            <dd>{backtest.metric_family}</dd>
          </div>
          <div>
            <dt>{t("backtests.oosMetric")}</dt>
            <dd>{backtest.is_oos ? t("common.yes") : t("common.no")}</dd>
          </div>
          <div>
            <dt>{t("backtests.researchOnly")}</dt>
            <dd>{backtest.research_only ? t("common.yes") : t("common.no")}</dd>
          </div>
        </dl>

        <ul className="check-list">
          {backtest.notes.map((note) => (
            <li key={note}>{note}</li>
          ))}
        </ul>
      </Card>

      <ResearchJobPanel jobType="backtest" onComplete={onRefresh} />
    </div>
  );
}
