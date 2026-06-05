import { Badge } from "../components/Badge";
import { Card, EmptyState } from "../components/Card";
import { useLanguage } from "../i18n/LanguageContext";
import type { DashboardData } from "../hooks/useDashboardData";

export function AuditLogs({ data }: { data: DashboardData }) {
  const { auditLogs } = data;
  const { t } = useLanguage();

  return (
    <div className="page">
      <Card
        title={t("audit.title")}
        subtitle={t("audit.subtitle", { source: auditLogs.source, count: auditLogs.events.length })}
      >
        {auditLogs.events.length === 0 ? (
          <EmptyState title={t("audit.emptyTitle")} description={t("audit.emptyDesc")} />
        ) : (
          <div className="table-wrap">
            <table className="data-table">
              <thead>
                <tr>
                  <th>{t("audit.colTimestamp")}</th>
                  <th>{t("audit.colActor")}</th>
                  <th>{t("audit.colAction")}</th>
                  <th>{t("audit.colResource")}</th>
                  <th>{t("audit.colStatus")}</th>
                </tr>
              </thead>
              <tbody>
                {auditLogs.events.map((event, index) => (
                  <tr key={String(event.hash ?? index)}>
                    <td className="mono">{String(event.timestamp ?? "—")}</td>
                    <td>{String(event.actor ?? "—")}</td>
                    <td>{String(event.action ?? "—")}</td>
                    <td>{String(event.resource ?? "—")}</td>
                    <td>
                      <Badge tone="success">{String(event.status ?? t("audit.logged"))}</Badge>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>
    </div>
  );
}
