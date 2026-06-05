import type { ReactNode } from "react";

export function Card({
  title,
  subtitle,
  children,
  className = "",
  accent
}: {
  title?: string;
  subtitle?: string;
  children: ReactNode;
  className?: string;
  accent?: "safety" | "none";
}) {
  return (
    <article className={`card ${accent === "safety" ? "card--safety" : ""} ${className}`.trim()}>
      {(title || subtitle) && (
        <header className="card__header">
          {title && <h3 className="card__title">{title}</h3>}
          {subtitle && <p className="card__subtitle">{subtitle}</p>}
        </header>
      )}
      <div className="card__body">{children}</div>
    </article>
  );
}

export function StatCard({
  label,
  value,
  hint,
  tone = "default"
}: {
  label: string;
  value: string;
  hint?: string;
  tone?: "default" | "success" | "danger";
}) {
  return (
    <div className={`stat-card stat-card--${tone}`}>
      <span className="stat-card__label">{label}</span>
      <strong className="stat-card__value">{value}</strong>
      {hint && <span className="stat-card__hint">{hint}</span>}
    </div>
  );
}

export function EmptyState({
  title,
  description,
  action
}: {
  title: string;
  description: string;
  action?: ReactNode;
}) {
  return (
    <div className="empty-state">
      <div className="empty-state__icon" aria-hidden>
        ◌
      </div>
      <h3>{title}</h3>
      <p>{description}</p>
      {action}
    </div>
  );
}
