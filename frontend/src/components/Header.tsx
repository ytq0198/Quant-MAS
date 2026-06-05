import type { AuthMePayload } from "../api/auth";
import { getPageTitleKey } from "../i18n/translations";
import { useLanguage } from "../i18n/LanguageContext";
import { Badge } from "./Badge";
import { LanguageToggle } from "./LanguageToggle";
import type { PageId } from "../types/navigation";

export function Header({
  page,
  source,
  auth,
  onRefresh,
  loading
}: {
  page: PageId;
  source: "api" | "fallback";
  auth: AuthMePayload;
  onRefresh: () => void;
  loading: boolean;
}) {
  const { t } = useLanguage();

  return (
    <header className="app-header">
      <div>
        <p className="app-header__eyebrow">{t("header.eyebrow")}</p>
        <h1 className="app-header__title">{t(getPageTitleKey(page))}</h1>
      </div>
      <div className="app-header__meta">
        <LanguageToggle compact />
        <Badge tone={source === "api" ? "success" : "warning"}>
          {source === "api" ? t("header.serverConnected") : t("header.localFallback")}
        </Badge>
        <Badge tone="info">
          {t("header.auth")}: {auth.auth_mode}
        </Badge>
        {auth.role !== "anonymous" && (
          <Badge tone="muted">
            {t("header.role")}: {auth.role}
          </Badge>
        )}
        <Badge tone="danger">{t("safety.liveTradingDisabled")}</Badge>
        <button type="button" className="btn btn--secondary" onClick={onRefresh} disabled={loading}>
          {loading ? t("common.refreshing") : t("common.refresh")}
        </button>
      </div>
    </header>
  );
}
