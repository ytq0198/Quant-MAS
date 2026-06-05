import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useState,
  type ReactNode
} from "react";

import {
  API_STRING_KEYS,
  type Locale,
  type TranslationKey,
  translations
} from "./translations";

const STORAGE_KEY = "quant-mas-locale";

interface LanguageContextValue {
  locale: Locale;
  setLocale: (locale: Locale) => void;
  toggleLocale: () => void;
  t: (key: TranslationKey, params?: Record<string, string | number>) => string;
  tApi: (text: string) => string;
}

const LanguageContext = createContext<LanguageContextValue | null>(null);

function readStoredLocale(): Locale {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored === "zh" || stored === "en") return stored;
  } catch {
    /* ignore */
  }
  return "en";
}

export function LanguageProvider({ children }: { children: ReactNode }) {
  const [locale, setLocaleState] = useState<Locale>(() => {
    const initial = readStoredLocale();
    document.documentElement.lang = initial === "zh" ? "zh-CN" : "en";
    return initial;
  });

  const setLocale = useCallback((next: Locale) => {
    setLocaleState(next);
    try {
      localStorage.setItem(STORAGE_KEY, next);
    } catch {
      /* ignore */
    }
    document.documentElement.lang = next === "zh" ? "zh-CN" : "en";
  }, []);

  const toggleLocale = useCallback(() => {
    setLocale(locale === "en" ? "zh" : "en");
  }, [locale, setLocale]);

  const t = useCallback(
    (key: TranslationKey, params?: Record<string, string | number>) => {
      let text = translations[locale][key] ?? translations.en[key] ?? key;
      if (params) {
        for (const [name, value] of Object.entries(params)) {
          text = text.replace(`{${name}}`, String(value));
        }
      }
      return text;
    },
    [locale]
  );

  const tApi = useCallback(
    (text: string) => {
      const key = API_STRING_KEYS[text];
      return key ? t(key) : text;
    },
    [t]
  );

  const value = useMemo(
    () => ({ locale, setLocale, toggleLocale, t, tApi }),
    [locale, setLocale, toggleLocale, t, tApi]
  );

  return <LanguageContext.Provider value={value}>{children}</LanguageContext.Provider>;
}

export function useLanguage() {
  const ctx = useContext(LanguageContext);
  if (!ctx) {
    throw new Error("useLanguage must be used within LanguageProvider");
  }
  return ctx;
}
