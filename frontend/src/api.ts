import type {
  CmsBootstrap,
  ContactMessagePayload,
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

export const getCmsBootstrap = (signal?: AbortSignal) =>
  requestJson<CmsBootstrap>("/bootstrap/", { signal });

export const getSiteSettings = (signal?: AbortSignal) =>
  requestJson<SiteSettings>("/site/", { signal });

export const getPageBySlug = (slug: string, signal?: AbortSignal) =>
  requestJson<Page>(`/pages/${slug}/`, { signal });

export const getMenuByCode = (code: string, signal?: AbortSignal) =>
  requestJson<Menu>(`/menus/${code}/`, { signal });

export const sendContactMessage = (payload: ContactMessagePayload) =>
  requestJson<{ status: string; id: number }>("/contact-messages/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });
