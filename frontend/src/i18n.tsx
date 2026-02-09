import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import { getContent, setLanguageCookie } from "./api";
import type { ContentResponse, I18nDictionary, Locale } from "./types";

type I18nContextValue = {
  lang: Locale;
  setLang: (lang: Locale) => Promise<void>;
  t: (key: string, fallback?: string) => string;
  isLoading: boolean;
  content: ContentResponse | null;
};

const LANG_STORAGE_KEY = "site.locale";

const I18nContext = createContext<I18nContextValue | null>(null);

function normalizeLocale(value: string | null | undefined): Locale | null {
  if (!value) {
    return null;
  }
  const normalized = value.trim().toLowerCase();
  if (!normalized) {
    return null;
  }
  if (!/^[a-z0-9-]{2,12}$/.test(normalized)) {
    return null;
  }
  return normalized;
}

function initialLocale(): Locale {
  if (typeof window === "undefined") {
    return "en";
  }

  const queryLang = normalizeLocale(
    new URLSearchParams(window.location.search).get("lang")
  );
  if (queryLang) {
    return queryLang;
  }

  const saved = normalizeLocale(window.localStorage.getItem(LANG_STORAGE_KEY));
  if (saved) {
    return saved;
  }

  return "en";
}

export function I18nProvider({ children }: { children: ReactNode }) {
  const [lang, setLangState] = useState<Locale>(initialLocale);
  const [dictionary, setDictionary] = useState<I18nDictionary>({});
  const [content, setContent] = useState<ContentResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    let cancelled = false;

    async function loadContent() {
      setIsLoading(true);
      try {
        const data = await getContent(lang);
        if (!cancelled) {
          setContent(data);
          setDictionary(data.texts || {});
        }
      } catch {
        if (!cancelled) {
          setContent(null);
          setDictionary({});
        }
      } finally {
        if (!cancelled) {
          setIsLoading(false);
        }
      }
    }

    void loadContent();
    return () => {
      cancelled = true;
    };
  }, [lang]);

  useEffect(() => {
    if (typeof document === "undefined") {
      return;
    }
    document.documentElement.lang = lang || "en";
  }, [lang]);

  const setLang = useCallback(async (nextLang: Locale) => {
    const normalized = normalizeLocale(nextLang);
    if (!normalized) {
      return;
    }

    await setLanguageCookie(normalized).catch(() => undefined);
    setLangState(normalized);

    if (typeof window !== "undefined") {
      window.localStorage.setItem(LANG_STORAGE_KEY, normalized);
      const url = new URL(window.location.href);
      url.searchParams.set("lang", normalized);
      window.history.replaceState({}, "", `${url.pathname}${url.search}`);
    }
  }, []);

  const t = useCallback(
    (key: string, fallback?: string) => dictionary[key] || fallback || key,
    [dictionary]
  );

  const value = useMemo<I18nContextValue>(
    () => ({ lang, setLang, t, isLoading, content }),
    [lang, setLang, t, isLoading, content]
  );

  return <I18nContext.Provider value={value}>{children}</I18nContext.Provider>;
}

export function useI18n() {
  const context = useContext(I18nContext);
  if (!context) {
    throw new Error("useI18n must be used within I18nProvider");
  }
  return context;
}
