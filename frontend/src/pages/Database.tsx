import { Badge } from "../components/Badge";
import { Card } from "../components/Card";
import { useLanguage } from "../i18n/LanguageContext";
import type { DashboardData } from "../hooks/useDashboardData";

export function Database({ data }: { data: DashboardData }) {
  const { database, databaseTables, graph, deployment } = data;
  const { t } = useLanguage();

  return (
    <div className="page">
      <div className="status-grid">
        <Card title={t("database.backendMode")}>
          <p className="metric-highlight">{database.mode}</p>
          <p className="muted">
            {t("common.default")}: {database.default_backend}
          </p>
        </Card>
        <Card title={t("database.vectorStore")}>
          <p className="metric-highlight">{data.ragDocuments.vector_store}</p>
          <Badge tone="muted">{t("database.vectorHint")}</Badge>
        </Card>
        <Card title={t("database.graph")}>
          <p className="metric-highlight">{graph.source}</p>
          <Badge tone="muted">{t("database.graphHint")}</Badge>
        </Card>
      </div>

      <Card title={t("database.backends")}>
        <div className="chip-grid">
          {database.backends.map((backend) => (
            <span className="chip" key={backend.name}>
              {backend.name}: {backend.status}
            </span>
          ))}
        </div>
      </Card>

      <Card
        title={t("database.tables")}
        subtitle={`${t("common.mode")}: ${databaseTables.mode} · ${databaseTables.status}`}
      >
        <div className="chip-grid">
          {databaseTables.tables.map((table) => (
            <span className="chip" key={table}>
              {table}
            </span>
          ))}
        </div>
      </Card>

      <Card title={t("database.relationships")} subtitle={`${t("common.source")}: ${graph.source}`}>
        <div className="stack compact">
          {graph.relationships.slice(0, 6).map((rel) => (
            <div className="list-card" key={`${rel.source}-${rel.relation}-${rel.target}`}>
              <strong>{rel.source}</strong>
              <p>{rel.relation}</p>
              <span className="muted">{rel.target}</span>
            </div>
          ))}
        </div>
      </Card>

      <Card title={t("database.deployment")} subtitle={`${deployment.frontend.stack} · ${deployment.backend.stack}`}>
        <div className="chip-grid">
          {deployment.artifacts.map((artifact) => (
            <span className="chip" key={artifact}>
              {artifact}
            </span>
          ))}
        </div>
      </Card>
    </div>
  );
}
