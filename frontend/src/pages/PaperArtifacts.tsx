import { Badge } from "../components/Badge";
import { Card, EmptyState } from "../components/Card";
import { PaperExportPanel } from "../components/ResearchJobPanel";
import { useLanguage } from "../i18n/LanguageContext";
import type { DashboardData } from "../hooks/useDashboardData";

export function PaperArtifacts({ data, onRefresh }: { data: DashboardData; onRefresh: () => void }) {
  const { paperArtifacts } = data;
  const { t } = useLanguage();

  return (
    <div className="page">
      <PaperExportPanel onComplete={onRefresh} />

      <Card
        title={t("paper.title")}
        subtitle={t("paper.subtitle", { source: paperArtifacts.source, path: paperArtifacts.path })}
      >
        {paperArtifacts.artifacts.length === 0 ? (
          <EmptyState title={t("paper.emptyTitle")} description={t("paper.emptyDesc")} />
        ) : (
          <div className="table-wrap">
            <table className="data-table">
              <thead>
                <tr>
                  <th>{t("paper.colName")}</th>
                  <th>{t("paper.colSuffix")}</th>
                  <th>{t("paper.colSize")}</th>
                </tr>
              </thead>
              <tbody>
                {paperArtifacts.artifacts.map((artifact) => (
                  <tr key={artifact.path}>
                    <td>{artifact.name}</td>
                    <td>
                      <Badge tone="muted">{artifact.suffix}</Badge>
                    </td>
                    <td>{artifact.size_bytes} B</td>
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
