import type {
  CategoryData,
  ContactMessagePayload,
  ContentResponse,
  ExpeditionData,
  Locale,
  NavigationResponse,
  PageResponse,
  StoryData,
} from "./types";

const API_BASE = (import.meta.env.VITE_API_BASE_URL || "/api").replace(/\/$/, "");
const ABSOLUTE_BASE_RE = /^https?:\/\//i;

function buildApiUrl(path: string, params?: Record<string, string | undefined>): string {
  const normalizedPath = path.startsWith("/") ? path : `/${path}`;
  const url = new URL(`${API_BASE}${normalizedPath}`, window.location.origin);
  if (params) {
    for (const [key, value] of Object.entries(params)) {
      if (!value) {
        continue;
      }
      url.searchParams.set(key, value);
    }
  }
  if (ABSOLUTE_BASE_RE.test(API_BASE)) {
    return url.toString();
  }
  return `${url.pathname}${url.search}`;
}

async function requestJson<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(path, {
    credentials: "include",
    ...init,
  });
  if (!response.ok) {
    const body = (await response.json().catch(() => null)) as
      | { detail?: string }
      | null;
    throw new Error(body?.detail || `Request failed (${response.status})`);
  }
  return (await response.json()) as T;
}

export async function setLanguageCookie(lang: Locale): Promise<void> {
  await requestJson<{ lang: string }>(buildApiUrl("/i18n/set-language/"), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ lang }),
  });
}

export async function getContent(lang: Locale): Promise<ContentResponse> {
  return requestJson<ContentResponse>(buildApiUrl("/content/", { lang }));
}

export async function getNavigation(
  lang: Locale,
  menu?: string
): Promise<NavigationResponse> {
  return requestJson<NavigationResponse>(
    buildApiUrl("/navigation/", { lang, menu: menu || undefined })
  );
}

export async function getPageBySlug(
  slug: string,
  lang: Locale
): Promise<PageResponse> {
  return requestJson<PageResponse>(
    buildApiUrl(`/pages/${encodeURIComponent(slug)}/`, { lang })
  );
}

export async function getExpeditions(lang: Locale): Promise<ExpeditionData[]> {
  return requestJson<ExpeditionData[]>(buildApiUrl("/expeditions/", { lang }));
}

export async function getCategories(lang: Locale): Promise<CategoryData[]> {
  return requestJson<CategoryData[]>(buildApiUrl("/categories/", { lang }));
}

export async function getStories(lang: Locale): Promise<StoryData[]> {
  return requestJson<StoryData[]>(buildApiUrl("/stories/", { lang }));
}

export async function sendContactMessage(
  payload: ContactMessagePayload
): Promise<{ status: string; id: number }> {
  return requestJson<{ status: string; id: number }>(buildApiUrl("/contact-messages/"), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}
