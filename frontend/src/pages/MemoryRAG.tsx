import { useState, type FormEvent } from "react";

import { Badge, MetricFamilyBadge } from "../components/Badge";
import { Card, EmptyState } from "../components/Card";
import { fetchMemory, fallbackMemory } from "../api/phase2";
import type { MemorySearchPayload } from "../api/phase2";
import { useLanguage } from "../i18n/LanguageContext";
import type { DashboardData } from "../hooks/useDashboardData";

function sourceBadge(type: string): "info" | "success" | "muted" {
  if (type === "experiment") return "info";
  if (type === "policy") return "success";
  return "muted";
}

export function MemoryRAG({ data }: { data: DashboardData }) {
  const { t } = useLanguage();
  const [query, setQuery] = useState(data.memory.query || "OOS baseline");
  const [results, setResults] = useState<MemorySearchPayload>(data.memory);
  const [loading, setLoading] = useState(false);

  async function handleSearch(event: FormEvent) {
    event.preventDefault();
    setLoading(true);
    try {
      setResults(await fetchMemory(query));
    } catch {
      setResults({ ...fallbackMemory, query });
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="page">
      <div className="page-banner">
        <MetricFamilyBadge family="oos" />
        <MetricFamilyBadge family="simulation" />
        <span className="muted">{t("memory.banner")}</span>
      </div>

      <Card title={t("memory.searchTitle")}>
        <form className="search-bar" onSubmit={(e) => void handleSearch(e)}>
          <input
            aria-label={t("memory.searchTitle")}
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder={t("memory.placeholder")}
          />
          <button type="submit" className="btn btn--primary" disabled={loading}>
            {loading ? t("common.searching") : t("common.search")}
          </button>
        </form>
        <p className="muted">
          {t("common.mode")}: {results.mode}
        </p>
      </Card>

      {results.results.length === 0 ? (
        <EmptyState title={t("memory.noResults")} description={t("memory.noResultsDesc")} />
      ) : (
        <div className="stack">
          {results.results.map((item) => (
            <Card key={item.id} title={item.title}>
              <p>{item.snippet}</p>
              <Badge tone={sourceBadge(item.type)}>{item.type}</Badge>
            </Card>
          ))}
        </div>
      )}

      <Card
        title={t("memory.ragDocuments")}
        subtitle={`${t("memory.store")}: ${data.ragDocuments.vector_store}`}
      >
        <div className="stack compact">
          {data.ragDocuments.documents.slice(0, 4).map((doc) => (
            <div className="list-card" key={doc.document_id}>
              <strong>{doc.title}</strong>
              <p>{doc.snippet}</p>
              <Badge tone="muted">{doc.type}</Badge>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}
