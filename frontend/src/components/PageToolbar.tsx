import { LanguageToggle } from "./LanguageToggle";

/** Shown at the top of each page content area for quick language switching. */
export function PageToolbar() {
  return (
    <div className="page-toolbar">
      <LanguageToggle />
    </div>
  );
}
