import { useLanguage } from "../i18n/LanguageContext";

export function LanguageToggle({ compact = false }: { compact?: boolean }) {
  const { locale, toggleLocale, t } = useLanguage();
  const nextLocale = locale === "en" ? "zh" : "en";
  const nextLabel = nextLocale === "zh" ? t("lang.zh") : t("lang.en");
  const currentLabel = locale === "zh" ? t("lang.zh") : t("lang.en");

  return (
    <button
      type="button"
      className={`lang-toggle ${compact ? "lang-toggle--compact" : ""}`}
      onClick={toggleLocale}
      title={t("lang.switchTo", { lang: nextLabel })}
      aria-label={t("lang.switchTo", { lang: nextLabel })}
    >
      <span className="lang-toggle__icon" aria-hidden>
        🌐
      </span>
      {!compact && <span className="lang-toggle__label">{currentLabel}</span>}
      <span className="lang-toggle__arrow" aria-hidden>
        → {nextLabel}
      </span>
    </button>
  );
}
