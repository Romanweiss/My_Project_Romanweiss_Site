import type {
  CmsBootstrap,
  ContactMessagePayload,
  Locale,
  Menu,
  Page,
  SiteSettings,
} from "./types";

const API_BASE = (import.meta.env.VITE_API_BASE_URL || "/api/v1").replace(/\/$/, "");

async function requestJson<T>(path: string, init?: RequestInit): Promise<T> {
  const requestPath = path.startsWith("/") ? path : `/${path}`;
  const response = await fetch(`${API_BASE}${requestPath}`, init);
  if (!response.ok) {
    const body = (await response.json().catch(() => null)) as
      | { detail?: string }
      | null;
    throw new Error(body?.detail || `Request failed (${response.status})`);
  }
  return (await response.json()) as T;
}

function withLang(path: string, lang: Locale): string {
  const separator = path.includes("?") ? "&" : "?";
  return `${path}${separator}lang=${encodeURIComponent(lang)}`;
}

export const getCmsBootstrap = (lang: Locale, signal?: AbortSignal) =>
  requestJson<CmsBootstrap>(withLang("/bootstrap/", lang), { signal });

export const getSiteSettings = (lang: Locale, signal?: AbortSignal) =>
  requestJson<SiteSettings>(withLang("/site/", lang), { signal });

export const getPageBySlug = (slug: string, lang: Locale, signal?: AbortSignal) =>
  requestJson<Page>(withLang(`/pages/${slug}/`, lang), { signal });

export const getMenuByCode = (code: string, lang: Locale, signal?: AbortSignal) =>
  requestJson<Menu>(withLang(`/menus/${code}/`, lang), { signal });

export const sendContactMessage = (payload: ContactMessagePayload) =>
  requestJson<{ status: string; id: number }>("/contact-messages/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });
