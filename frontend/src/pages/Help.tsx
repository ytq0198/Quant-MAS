import { useCallback, useState } from "react";

import { Badge } from "../components/Badge";
import { Card } from "../components/Card";
import { getHelpGuide, type HelpSection } from "../content/helpGuide";
import { useLanguage } from "../i18n/LanguageContext";
import type { PageId } from "../types/navigation";

function HelpSectionBlock({
  section,
  stepsLabel,
  notesLabel,
  commandsLabel,
  goToPage,
  onNavigate
}: {
  section: HelpSection;
  stepsLabel: string;
  notesLabel: string;
  commandsLabel: string;
  goToPage: string;
  onNavigate: (page: PageId) => void;
}) {
  return (
    <section id={`help-${section.id}`} className="help-section">
      <div className="help-section__head">
        <h2>{section.title}</h2>
        {section.pageId && (
          <button
            type="button"
            className="btn btn--secondary btn--sm"
            onClick={() => onNavigate(section.pageId!)}
          >
            {goToPage} →
          </button>
        )}
      </div>

      {section.intro && <p className="help-section__intro">{section.intro}</p>}

      {section.bullets && section.bullets.length > 0 && (
        <ul className="help-list">
          {section.bullets.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      )}

      {section.steps && section.steps.length > 0 && (
        <div className="help-block">
          <h3>{stepsLabel}</h3>
          <ol className="help-steps">
            {section.steps.map((step) => (
              <li key={step}>{step}</li>
            ))}
          </ol>
        </div>
      )}

      {section.table && (
        <div className="table-wrap">
          <table className="data-table help-table">
            <thead>
              <tr>
                {section.table.headers.map((header) => (
                  <th key={header}>{header}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {section.table.rows.map((row) => (
                <tr key={row.join("|")}>
                  {row.map((cell) => (
                    <td key={cell}>{cell}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {section.commands && section.commands.length > 0 && (
        <div className="help-block">
          <h3>{commandsLabel}</h3>
          <pre className="help-code">{section.commands.join("\n")}</pre>
        </div>
      )}

      {section.notes && section.notes.length > 0 && (
        <div className="help-block help-block--notes">
          <h3>{notesLabel}</h3>
          <ul className="help-list help-list--compact">
            {section.notes.map((note) => (
              <li key={note}>{note}</li>
            ))}
          </ul>
        </div>
      )}
    </section>
  );
}

export function Help({ onNavigate }: { onNavigate: (page: PageId) => void }) {
  const { locale, t } = useLanguage();
  const guide = getHelpGuide(locale);
  const [activeId, setActiveId] = useState(guide.sections[0]?.id ?? "");

  const scrollTo = useCallback((id: string) => {
    setActiveId(id);
    document.getElementById(`help-${id}`)?.scrollIntoView({ behavior: "smooth", block: "start" });
  }, []);

  return (
    <div className="page help-page">
      <div className="page-banner">
        <Badge tone="info">{t("help.badge")}</Badge>
        <span>{guide.lead}</span>
      </div>

      <div className="help-layout">
        <nav className="help-toc" aria-label={guide.tocTitle}>
          <Card title={guide.tocTitle} subtitle={guide.updated}>
            <ul className="help-toc__list">
              {guide.sections.map((section) => (
                <li key={section.id}>
                  <button
                    type="button"
                    className={`help-toc__link ${activeId === section.id ? "help-toc__link--active" : ""}`}
                    onClick={() => scrollTo(section.id)}
                  >
                    {section.title}
                  </button>
                </li>
              ))}
            </ul>
          </Card>
        </nav>

        <div className="help-content">
          {guide.sections.map((section) => (
            <Card key={section.id} className="help-card">
              <HelpSectionBlock
                section={section}
                stepsLabel={guide.stepsLabel}
                notesLabel={guide.notesLabel}
                commandsLabel={guide.commandsLabel}
                goToPage={guide.goToPage}
                onNavigate={onNavigate}
              />
            </Card>
          ))}
        </div>
      </div>
    </div>
  );
}
