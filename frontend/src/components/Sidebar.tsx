import { getNavGroupKey, getNavKey } from "../i18n/translations";
import { useLanguage } from "../i18n/LanguageContext";
import { LanguageToggle } from "./LanguageToggle";
import { NAV_ITEMS, type PageId } from "../types/navigation";

export function Sidebar({
  active,
  onNavigate,
  collapsed,
  onToggleCollapse
}: {
  active: PageId;
  onNavigate: (page: PageId) => void;
  collapsed: boolean;
  onToggleCollapse: () => void;
}) {
  const { t } = useLanguage();
  let lastGroup = "";

  return (
    <aside className={`sidebar ${collapsed ? "sidebar--collapsed" : ""}`}>
      <div className="sidebar__brand">
        <span className="sidebar__logo">Q</span>
        {!collapsed && (
          <div>
            <strong>Quant MAS</strong>
            <span>{t("brand.subtitle")}</span>
          </div>
        )}
      </div>
      <nav className="sidebar__nav">
        {NAV_ITEMS.map((item) => {
          const showGroup = !collapsed && item.group && item.group !== lastGroup;
          if (item.group) lastGroup = item.group;
          const label = t(getNavKey(item.id));
          return (
            <div key={item.id}>
              {showGroup && item.group && (
                <p className="sidebar__group">{t(getNavGroupKey(item.group))}</p>
              )}
              <button
                type="button"
                className={`sidebar__link ${active === item.id ? "sidebar__link--active" : ""}`}
                onClick={() => onNavigate(item.id)}
                title={label}
              >
                <span className="sidebar__icon">{item.icon}</span>
                {!collapsed && <span>{label}</span>}
              </button>
            </div>
          );
        })}
      </nav>
      <div className="sidebar__footer">
        <LanguageToggle compact />
        <button type="button" className="sidebar__toggle" onClick={onToggleCollapse}>
          {collapsed ? "»" : "«"}
        </button>
      </div>
    </aside>
  );
}
