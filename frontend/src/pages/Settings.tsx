import { useState } from "react";

import { Badge } from "../components/Badge";
import { Card } from "../components/Card";
import { getStoredApiKey, setStoredApiKey } from "../api/client";
import { useLanguage } from "../i18n/LanguageContext";
import type { DashboardData } from "../hooks/useDashboardData";

export function Settings({
  data,
  onRefresh
}: {
  data: DashboardData;
  onRefresh: () => void;
}) {
  const { auth, effectiveConfig, source } = data;
  const { t } = useLanguage();
  const [apiKeyDraft, setApiKeyDraft] = useState(() => getStoredApiKey());

  function saveApiKey() {
    setStoredApiKey(apiKeyDraft);
    void onRefresh();
  }

  function clearApiKey() {
    setApiKeyDraft("");
    setStoredApiKey("");
    void onRefresh();
  }

  return (
    <div className="page">
      <Card title={t("settings.apiAccess")} subtitle={t("settings.apiSubtitle")}>
        <p className="muted">
          {t("common.mode")}: {auth.auth_mode} · {t("header.role")}: {auth.role}
          {auth.key_fingerprint ? ` · ${auth.key_fingerprint}` : ""}
        </p>
        <div className="form-row">
          <input
            aria-label={t("settings.apiKeyLabel")}
            placeholder="X-Quant-MAS-Key"
            type="password"
            value={apiKeyDraft}
            onChange={(event) => setApiKeyDraft(event.target.value)}
          />
          <button type="button" className="btn btn--primary" onClick={saveApiKey}>
            {t("common.save")}
          </button>
          <button type="button" className="btn btn--secondary" onClick={clearApiKey}>
            {t("common.clear")}
          </button>
        </div>
      </Card>

      <Card title={t("settings.backendUrl")}>
        <p className="mono">{t("settings.backendPath")}</p>
        <Badge tone={source === "api" ? "success" : "warning"}>
          {source === "api" ? t("settings.connected") : t("settings.fallbackMode")}
        </Badge>
      </Card>

      <Card title={t("settings.environment")}>
        <div className="chip-grid">
          {Object.entries(effectiveConfig.env ?? {}).map(([key, value]) => (
            <span className="chip" key={key}>
              {key}: {value || t("common.unset")}
            </span>
          ))}
        </div>
      </Card>

      <Card title={t("settings.disclaimer")} accent="safety">
        <ul className="check-list">
          <li>{t("settings.disclaimer1")}</li>
          <li>{t("settings.disclaimer2")}</li>
          <li>{t("settings.disclaimer3")}</li>
          <li>{t("settings.disclaimer4")}</li>
          <li>{t("settings.disclaimer5")}</li>
        </ul>
      </Card>
    </div>
  );
}
