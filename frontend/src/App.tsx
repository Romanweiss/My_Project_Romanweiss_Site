import {
  FormEvent,
  type KeyboardEvent as ReactKeyboardEvent,
  type MouseEvent,
  type TouchEvent as ReactTouchEvent,
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";
import {
  getCategories,
  getExpeditions,
  getNavigation,
  getPageBySlug,
  getStories,
  sendContactMessage,
} from "./api";
import { useI18n } from "./i18n";
import type {
  CategoryData,
  ContactMessagePayload,
  ExpeditionData,
  ExpeditionMediaItem,
  NavigationItem,
  PageData,
  PageSection,
  StoryData,
} from "./types";

type SubmitStatus = "idle" | "sending" | "success" | "error";
type ThemeMode = "light" | "dark";
type TranslateFn = (key: string, fallback?: string) => string;

type AppRoute =
  | { kind: "page"; slug: string }
  | { kind: "expeditions-index" }
  | { kind: "expedition-detail"; slug: string }
  | { kind: "category-detail"; slug: string }
  | { kind: "story-detail"; slug: string };

type ExpeditionCard = {
  title?: string;
  subtitle?: string;
  slug?: string;
  date_label?: string;
  description?: string;
  image_url?: string;
};

type GalleryItem = {
  title?: string;
  slug?: string;
  description?: string;
  image_url?: string;
  size?: "large" | "small" | "wide";
};

type StoryItem = {
  title?: string;
  slug?: string;
  date_label?: string;
  description?: string;
  image_url?: string;
};

type ResolvedStory = {
  slug: string;
  title: string;
  dateLabel: string;
  description: string;
  imageUrl: string;
};

type ResolvedCategoryGalleryItem = {
  title: string;
  description: string;
  imageUrl: string;
  altText: string;
  lightboxIndex: number;
};

type ResolvedCategory = {
  slug: string;
  title: string;
  description: string;
  size: "large" | "small" | "wide";
  imageUrl: string;
  galleryItems: ResolvedCategoryGalleryItem[];
};

type ResolvedMediaBlock =
  | {
      kind: "image";
      title: string;
      body: string;
      imageUrl: string;
      altText: string;
    }
  | {
      kind: "video";
      title: string;
      body: string;
      videoUrl: string;
    }
  | {
      kind: "story";
      title: string;
      body: string;
    };

type ResolvedExpedition = {
  slug: string;
  title: string;
  subtitle: string;
  dateLabel: string;
  description: string;
  imageUrl: string;
  mediaBlocks: ResolvedMediaBlock[];
};

const THEME_STORAGE_KEY = "site.theme";
const HOME_HEADER_REVEAL_DELAY_MS = 1000;

function readInitialTheme(): ThemeMode {
  if (typeof window === "undefined") {
    return "light";
  }
  const saved = window.localStorage.getItem(THEME_STORAGE_KEY);
  return saved === "dark" ? "dark" : "light";
}

function slugifyToken(value: string, fallback = "item"): string {
  const slug = value
    .toLowerCase()
    .trim()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
  return slug || fallback;
}

function parseRoute(pathname: string): AppRoute {
  const cleaned = pathname.replace(/^\/+|\/+$/g, "");
  if (!cleaned) {
    return { kind: "page", slug: "home" };
  }

  const parts = cleaned.split("/");
  if (parts[0] === "expeditions") {
    if (parts.length === 1 || !parts[1]) {
      return { kind: "expeditions-index" };
    }
    return { kind: "expedition-detail", slug: parts[1] };
  }
  if (parts[0] === "focus" && parts[1]) {
    return { kind: "category-detail", slug: parts[1] };
  }
  if (parts[0] === "stories" && parts[1]) {
    return { kind: "story-detail", slug: parts[1] };
  }

  return { kind: "page", slug: cleaned };
}

function routeToPath(route: AppRoute, pageSlugs: string[]): string {
  if (route.kind === "expeditions-index") {
    return "/expeditions/";
  }
  if (route.kind === "expedition-detail") {
    return `/expeditions/${route.slug}/`;
  }
  if (route.kind === "category-detail") {
    return `/focus/${route.slug}/`;
  }
  if (route.kind === "story-detail") {
    return `/stories/${route.slug}/`;
  }
  if (route.slug === "home") {
    return "/";
  }
  return pageSlugs.includes(route.slug) ? `/${route.slug}/` : "/";
}

function sectionMap(page: PageData | null): Map<string, PageSection> {
  const map = new Map<string, PageSection>();
  for (const section of page?.sections ?? []) {
    map.set(section.key, section);
  }
  return map;
}

function payloadText(section: PageSection | undefined, field: string, fallback = ""): string {
  if (!section) {
    return fallback;
  }
  const value = section.payload[field];
  return typeof value === "string" ? value : fallback;
}

function payloadItems<T>(section: PageSection | undefined, key: string): T[] {
  if (!section) {
    return [];
  }
  const value = section.payload[key];
  return Array.isArray(value) ? (value as T[]) : [];
}

function safeHref(href: string): string {
  if (!href) {
    return "#";
  }
  return href;
}

function isExternalHref(href: string): boolean {
  return /^https?:\/\//i.test(href) || href.startsWith("mailto:");
}

function nonEmpty(value: unknown): string {
  return typeof value === "string" ? value.trim() : "";
}

function fallbackMediaBlocks(
  expedition: Omit<ResolvedExpedition, "mediaBlocks">,
  t: TranslateFn
): ResolvedMediaBlock[] {
  return [
    {
      kind: "image",
      title: expedition.title,
      body: "",
      imageUrl: expedition.imageUrl,
      altText: expedition.title,
    },
    {
      kind: "story",
      title: t("expedition.detail.story_title", "Field notes"),
      body: expedition.description,
    },
    {
      kind: "video",
      title: t("expedition.detail.video_title", "Video diary"),
      body: "",
      videoUrl: "",
    },
  ];
}

function fromApiMedia(
  mediaItems: ExpeditionMediaItem[],
  base: Omit<ResolvedExpedition, "mediaBlocks">,
  t: TranslateFn
): ResolvedMediaBlock[] {
  const blocks: ResolvedMediaBlock[] = [];

  for (const media of mediaItems ?? []) {
    if (media.kind === "image") {
      const imageUrl = nonEmpty(media.media_url) || base.imageUrl;
      if (!imageUrl) {
        continue;
      }
      blocks.push({
        kind: "image",
        title: nonEmpty(media.title) || base.title,
        body: nonEmpty(media.body),
        imageUrl,
        altText: nonEmpty(media.alt_text) || nonEmpty(media.title) || base.title,
      });
      continue;
    }

    if (media.kind === "video") {
      blocks.push({
        kind: "video",
        title: nonEmpty(media.title) || t("expedition.detail.video_title", "Video diary"),
        body: nonEmpty(media.body),
        videoUrl: nonEmpty(media.video_url),
      });
      continue;
    }

    if (media.kind === "story") {
      blocks.push({
        kind: "story",
        title: nonEmpty(media.title) || t("expedition.detail.story_title", "Field notes"),
        body: nonEmpty(media.body) || base.description,
      });
    }
  }

  if (!blocks.some((block) => block.kind === "image") && base.imageUrl) {
    blocks.unshift({
      kind: "image",
      title: base.title,
      body: "",
      imageUrl: base.imageUrl,
      altText: base.title,
    });
  }

  if (!blocks.some((block) => block.kind === "story")) {
    const storyBlock: ResolvedMediaBlock = {
      kind: "story",
      title: t("expedition.detail.story_title", "Field notes"),
      body: base.description,
    };
    const firstImageIndex = blocks.findIndex((block) => block.kind === "image");
    if (firstImageIndex >= 0) {
      blocks.splice(firstImageIndex + 1, 0, storyBlock);
    } else {
      blocks.push(storyBlock);
    }
  }

  if (!blocks.some((block) => block.kind === "video")) {
    blocks.push({
      kind: "video",
      title: t("expedition.detail.video_title", "Video diary"),
      body: "",
      videoUrl: "",
    });
  }

  return blocks;
}

function resolveExpeditions(
  apiExpeditions: ExpeditionData[],
  sectionCards: ExpeditionCard[],
  t: TranslateFn
): ResolvedExpedition[] {
  if (apiExpeditions.length) {
    return apiExpeditions.map((expedition, index) => {
      const fallbackTitle = nonEmpty(expedition.title) || `Expedition ${index + 1}`;
      const slug = nonEmpty(expedition.slug) || slugifyToken(fallbackTitle, `expedition-${index + 1}`);
      const title = t(`expedition.${slug}.title`, fallbackTitle);
      const subtitleFallback = nonEmpty(expedition.subtitle) || nonEmpty(expedition.description);
      const subtitle = t(`expedition.${slug}.subtitle`, subtitleFallback);
      const description = t(
        `expedition.${slug}.description`,
        nonEmpty(expedition.description) || subtitle
      );
      const dateLabel = t(`expedition.${slug}.date_label`, nonEmpty(expedition.date_label));
      const imageUrl = nonEmpty(expedition.cover_url) || nonEmpty(expedition.image_url);

      const base = {
        slug,
        title,
        subtitle,
        dateLabel,
        description,
        imageUrl,
      };

      return {
        ...base,
        mediaBlocks: fromApiMedia(expedition.media_items || [], base, t),
      };
    });
  }

  return sectionCards.map((item, index) => {
    const fallbackTitle = nonEmpty(item.title) || `Expedition ${index + 1}`;
    const slug = nonEmpty(item.slug) || slugifyToken(fallbackTitle, `expedition-${index + 1}`);
    const title = t(`expedition.${slug}.title`, fallbackTitle);
    const subtitle = t(
      `expedition.${slug}.subtitle`,
      nonEmpty(item.subtitle) || nonEmpty(item.description)
    );
    const description = t(`expedition.${slug}.description`, nonEmpty(item.description) || subtitle);
    const dateLabel = t(`expedition.${slug}.date_label`, nonEmpty(item.date_label));
    const imageUrl = nonEmpty(item.image_url);
    const base = { slug, title, subtitle, dateLabel, description, imageUrl };

    return {
      ...base,
      mediaBlocks: fallbackMediaBlocks(base, t),
    };
  });
}

function resolveStories(
  apiStories: StoryData[],
  sectionStories: StoryItem[],
  t: TranslateFn
): ResolvedStory[] {
  if (apiStories.length) {
    return apiStories.map((story, index) => {
      const fallbackTitle = nonEmpty(story.title) || `Story ${index + 1}`;
      const slug = nonEmpty(story.slug) || slugifyToken(fallbackTitle, `story-${index + 1}`);
      return {
        slug,
        title: t(`story.${slug}.title`, fallbackTitle),
        dateLabel: t(`story.${slug}.date_label`, nonEmpty(story.date_label)),
        description: t(`story.${slug}.description`, nonEmpty(story.description)),
        imageUrl: nonEmpty(story.cover_url) || nonEmpty(story.image_url),
      };
    });
  }

  return sectionStories.map((story, index) => {
    const fallbackTitle = nonEmpty(story.title) || `Story ${index + 1}`;
    const slug = nonEmpty(story.slug) || slugifyToken(fallbackTitle, `story-${index + 1}`);
    return {
      slug,
      title: t(`story.${slug}.title`, fallbackTitle),
      dateLabel: t(`story.${slug}.date_label`, nonEmpty(story.date_label)),
      description: t(`story.${slug}.description`, nonEmpty(story.description)),
      imageUrl: nonEmpty(story.image_url),
    };
  });
}

function normalizeCategorySize(value: unknown): "large" | "small" | "wide" {
  return value === "large" || value === "small" || value === "wide" ? value : "small";
}

function resolveCategories(
  apiCategories: CategoryData[],
  sectionItems: GalleryItem[],
  t: TranslateFn
): ResolvedCategory[] {
  if (apiCategories.length) {
    return apiCategories.map((category, index) => {
      const fallbackTitle = nonEmpty(category.title) || `Focus area ${index + 1}`;
      const slug = nonEmpty(category.slug) || slugifyToken(fallbackTitle, `focus-${index + 1}`);
      const imageUrl = nonEmpty(category.cover_url) || nonEmpty(category.image_url);
      const galleryItems = (category.gallery_items || [])
        .map((item) => {
          const itemImageUrl = nonEmpty(item.media_url) || nonEmpty(item.image_url) || imageUrl;
          if (!itemImageUrl) {
            return null;
          }
          return {
            title: nonEmpty(item.title) || fallbackTitle,
            description: nonEmpty(item.description),
            imageUrl: itemImageUrl,
            altText: nonEmpty(item.alt_text) || nonEmpty(item.title) || fallbackTitle,
          };
        })
        .filter((item): item is Omit<ResolvedCategoryGalleryItem, "lightboxIndex"> => item !== null)
        .map((item, itemIndex) => ({ ...item, lightboxIndex: itemIndex }));

      return {
        slug,
        title: t(`category.${slug}.title`, fallbackTitle),
        description: t(`category.${slug}.description`, galleryItems[0]?.description || ""),
        size: normalizeCategorySize(category.size),
        imageUrl,
        galleryItems:
          galleryItems.length > 0
            ? galleryItems
            : imageUrl
              ? [
                  {
                    title: fallbackTitle,
                    description: t(`category.${slug}.description`, ""),
                    imageUrl,
                    altText: fallbackTitle,
                    lightboxIndex: 0,
                  },
                ]
              : [],
      };
    });
  }

  return sectionItems.map((item, index) => {
    const fallbackTitle = nonEmpty(item.title) || `Focus area ${index + 1}`;
    const slug = nonEmpty(item.slug) || slugifyToken(fallbackTitle, `focus-${index + 1}`);
    const imageUrl = nonEmpty(item.image_url);
    return {
      slug,
      title: t(`category.${slug}.title`, fallbackTitle),
      description: t(`category.${slug}.description`, nonEmpty(item.description)),
      size: normalizeCategorySize(item.size),
      imageUrl,
      galleryItems: imageUrl
        ? [
            {
              title: fallbackTitle,
              description: t(`category.${slug}.description`, nonEmpty(item.description)),
              imageUrl,
              altText: fallbackTitle,
              lightboxIndex: 0,
            },
          ]
        : [],
    };
  });
}

export default function App() {
  const { lang, setLang, t, isLoading: isI18nLoading, content } = useI18n();

  const [theme, setTheme] = useState<ThemeMode>(readInitialTheme);
  const [route, setRoute] = useState<AppRoute>(() =>
    typeof window === "undefined" ? { kind: "page", slug: "home" } : parseRoute(window.location.pathname)
  );
  const [page, setPage] = useState<PageData | null>(null);
  const [isPageLoading, setIsPageLoading] = useState<boolean>(true);
  const [pageError, setPageError] = useState<string>("");
  const [menus, setMenus] = useState<Record<string, NavigationItem[]>>({
    main: [],
    footer: [],
    social: [],
  });
  const [isNavigationLoading, setIsNavigationLoading] = useState<boolean>(true);
  const [navigationError, setNavigationError] = useState<string>("");
  const [expeditionsData, setExpeditionsData] = useState<ExpeditionData[]>([]);
  const [isExpeditionsLoading, setIsExpeditionsLoading] = useState<boolean>(true);
  const [expeditionsError, setExpeditionsError] = useState<string>("");
  const [categoriesData, setCategoriesData] = useState<CategoryData[]>([]);
  const [isCategoriesLoading, setIsCategoriesLoading] = useState<boolean>(true);
  const [categoriesError, setCategoriesError] = useState<string>("");
  const [storiesData, setStoriesData] = useState<StoryData[]>([]);
  const [isStoriesLoading, setIsStoriesLoading] = useState<boolean>(true);
  const [storiesError, setStoriesError] = useState<string>("");
  const [contactForm, setContactForm] = useState<ContactMessagePayload>({
    name: "",
    email: "",
    message: "",
  });
  const [submitStatus, setSubmitStatus] = useState<SubmitStatus>("idle");
  const [submitMessage, setSubmitMessage] = useState<string>("");
  const [lightboxIndex, setLightboxIndex] = useState<number | null>(null);
  const [isHeaderVisible, setIsHeaderVisible] = useState<boolean>(() => {
    if (typeof window === "undefined") {
      return true;
    }
    const initialRoute = parseRoute(window.location.pathname);
    if (initialRoute.kind !== "page" || initialRoute.slug !== "home") {
      return true;
    }
    return window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  });
  const pageRef = useRef<HTMLDivElement | null>(null);
  const headerRef = useRef<HTMLElement | null>(null);
  const heroRef = useRef<HTMLElement | null>(null);
  const lightboxTouchStartX = useRef<number | null>(null);
  const lightboxTouchStartY = useRef<number | null>(null);
  const hasPlayedHomeIntroRef = useRef<boolean>(false);

  const navigateToRoute = useCallback(
    (nextRoute: AppRoute, replace = false) => {
      if (typeof window === "undefined") {
        return;
      }
      const knownSlugs = (content?.pages ?? []).map((item) => item.slug);
      const path = routeToPath(nextRoute, knownSlugs);
      if (replace) {
        window.history.replaceState({}, "", `${path}${window.location.search}`);
      } else {
        window.history.pushState({}, "", `${path}${window.location.search}`);
      }
      setRoute(nextRoute);
      window.scrollTo({ top: 0, behavior: "smooth" });
    },
    [content]
  );

  const navigateToSlug = useCallback(
    (slug: string, replace = false) => {
      navigateToRoute({ kind: "page", slug }, replace);
    },
    [navigateToRoute]
  );

  useEffect(() => {
    if (typeof document === "undefined") {
      return;
    }
    if (!content?.site) {
      return;
    }
    document.title = t("brand.name", content.site.brand_name);
  }, [content, t]);

  useEffect(() => {
    if (typeof document === "undefined") {
      return;
    }
    document.documentElement.dataset.theme = theme;
    window.localStorage.setItem(THEME_STORAGE_KEY, theme);
  }, [theme]);

  useEffect(() => {
    if (typeof window === "undefined") {
      return;
    }

    const pageElement = pageRef.current;
    const headerElement = headerRef.current;
    const heroElement = heroRef.current;

    if (!pageElement || !headerElement) {
      return;
    }

    const motionMediaQuery = window.matchMedia("(prefers-reduced-motion: reduce)");
    let prefersReducedMotion = motionMediaQuery.matches;
    let heroTop = 0;
    let heroHeight = Math.max(window.innerHeight, 1);
    let rafId = 0;
    let lastZoom = Number.NaN;
    let lastOverlayStrength = Number.NaN;
    let lastHeaderStrength = Number.NaN;

    const clamp01 = (value: number) => Math.min(1, Math.max(0, value));

    const setCssVariable = (
      element: HTMLElement,
      variableName: string,
      value: number,
      lastValue: number
    ): number => {
      if (Math.abs(value - lastValue) < 0.0005) {
        return lastValue;
      }
      element.style.setProperty(variableName, value.toFixed(4));
      return value;
    };

    const measure = () => {
      if (!heroElement) {
        heroTop = 0;
        heroHeight = Math.max(window.innerHeight, 1);
        return;
      }
      heroTop = heroElement.offsetTop;
      heroHeight = Math.max(heroElement.offsetHeight, window.innerHeight, 1);
    };

    const renderFrame = () => {
      rafId = 0;

      if (!heroElement) {
        lastZoom = setCssVariable(pageElement, "--hero-zoom", 1, lastZoom);
        lastOverlayStrength = setCssVariable(
          pageElement,
          "--hero-overlay-strength",
          0,
          lastOverlayStrength
        );
        lastHeaderStrength = setCssVariable(
          headerElement,
          "--header-overlay-strength",
          1,
          lastHeaderStrength
        );
        return;
      }

      const progress = clamp01((window.scrollY - heroTop) / heroHeight);
      const heroZoom = prefersReducedMotion ? 1 : 1 + progress * 0.12;
      const headerStrength = clamp01(progress * 1.05);

      lastZoom = setCssVariable(pageElement, "--hero-zoom", heroZoom, lastZoom);
      lastOverlayStrength = setCssVariable(
        pageElement,
        "--hero-overlay-strength",
        progress,
        lastOverlayStrength
      );
      lastHeaderStrength = setCssVariable(
        headerElement,
        "--header-overlay-strength",
        headerStrength,
        lastHeaderStrength
      );
    };

    const scheduleFrame = () => {
      if (rafId) {
        return;
      }
      rafId = window.requestAnimationFrame(renderFrame);
    };

    const handleResize = () => {
      measure();
      scheduleFrame();
    };

    const handleMotionPreferenceChange = (event: MediaQueryListEvent) => {
      prefersReducedMotion = event.matches;
      scheduleFrame();
    };

    window.addEventListener("scroll", scheduleFrame, { passive: true });
    window.addEventListener("resize", handleResize, { passive: true });

    let resizeObserver: ResizeObserver | null = null;
    if (heroElement && "ResizeObserver" in window) {
      resizeObserver = new ResizeObserver(() => {
        measure();
        scheduleFrame();
      });
      resizeObserver.observe(heroElement);
    }

    if (typeof motionMediaQuery.addEventListener === "function") {
      motionMediaQuery.addEventListener("change", handleMotionPreferenceChange);
    } else {
      motionMediaQuery.addListener(handleMotionPreferenceChange);
    }

    measure();
    scheduleFrame();

    return () => {
      if (rafId) {
        window.cancelAnimationFrame(rafId);
      }
      window.removeEventListener("scroll", scheduleFrame);
      window.removeEventListener("resize", handleResize);
      resizeObserver?.disconnect();
      if (typeof motionMediaQuery.removeEventListener === "function") {
        motionMediaQuery.removeEventListener("change", handleMotionPreferenceChange);
      } else {
        motionMediaQuery.removeListener(handleMotionPreferenceChange);
      }
    };
  }, [page, route.kind]);

  useEffect(() => {
    if (typeof window === "undefined") {
      return;
    }
    const onPopState = () => {
      setRoute(parseRoute(window.location.pathname));
    };
    window.addEventListener("popstate", onPopState);
    return () => window.removeEventListener("popstate", onPopState);
  }, []);

  useEffect(() => {
    setLightboxIndex(null);
  }, [route.kind, "slug" in route ? route.slug : ""]);

  useEffect(() => {
    if (route.kind !== "page") {
      return;
    }
    if (!content?.pages?.length) {
      return;
    }
    const exists = content.pages.some((item) => item.slug === route.slug);
    if (exists || route.slug === "home") {
      return;
    }
    const homePage = content.pages.find((item) => item.is_home) || content.pages[0];
    if (homePage) {
      navigateToSlug(homePage.slug, true);
    }
  }, [content, route, navigateToSlug]);

  useEffect(() => {
    let cancelled = false;

    async function loadNavigation() {
      setIsNavigationLoading(true);
      setNavigationError("");
      try {
        const data = await getNavigation(lang);
        if (!cancelled) {
          setMenus({
            main: data.menus.main || [],
            footer: data.menus.footer || [],
            social: data.menus.social || [],
          });
        }
      } catch (error) {
        if (!cancelled) {
          setMenus({ main: [], footer: [], social: [] });
          setNavigationError(error instanceof Error ? error.message : "");
        }
      } finally {
        if (!cancelled) {
          setIsNavigationLoading(false);
        }
      }
    }

    void loadNavigation();
    return () => {
      cancelled = true;
    };
  }, [lang]);

  useEffect(() => {
    let cancelled = false;

    async function loadExpeditions() {
      setIsExpeditionsLoading(true);
      setExpeditionsError("");
      try {
        const data = await getExpeditions(lang);
        if (!cancelled) {
          setExpeditionsData(data || []);
        }
      } catch (error) {
        if (!cancelled) {
          setExpeditionsData([]);
          setExpeditionsError(error instanceof Error ? error.message : "");
        }
      } finally {
        if (!cancelled) {
          setIsExpeditionsLoading(false);
        }
      }
    }

    void loadExpeditions();
    return () => {
      cancelled = true;
    };
  }, [lang]);

  useEffect(() => {
    let cancelled = false;

    async function loadCategories() {
      setIsCategoriesLoading(true);
      setCategoriesError("");
      try {
        const data = await getCategories(lang);
        if (!cancelled) {
          setCategoriesData(data || []);
        }
      } catch (error) {
        if (!cancelled) {
          setCategoriesData([]);
          setCategoriesError(error instanceof Error ? error.message : "");
        }
      } finally {
        if (!cancelled) {
          setIsCategoriesLoading(false);
        }
      }
    }

    void loadCategories();
    return () => {
      cancelled = true;
    };
  }, [lang]);

  useEffect(() => {
    let cancelled = false;

    async function loadStories() {
      setIsStoriesLoading(true);
      setStoriesError("");
      try {
        const data = await getStories(lang);
        if (!cancelled) {
          setStoriesData(data || []);
        }
      } catch (error) {
        if (!cancelled) {
          setStoriesData([]);
          setStoriesError(error instanceof Error ? error.message : "");
        }
      } finally {
        if (!cancelled) {
          setIsStoriesLoading(false);
        }
      }
    }

    void loadStories();
    return () => {
      cancelled = true;
    };
  }, [lang]);

  useEffect(() => {
    let cancelled = false;

    async function loadPage() {
      setIsPageLoading(true);
      setPageError("");
      try {
        const slug = route.kind === "page" ? route.slug || "home" : "home";
        const data = await getPageBySlug(slug, lang);
        if (!cancelled) {
          setPage(data.page);
        }
      } catch (error) {
        if (!cancelled) {
          if (route.kind === "page" && route.slug !== "home") {
            navigateToRoute({ kind: "page", slug: "home" }, true);
            return;
          }
          setPage(null);
          setPageError(error instanceof Error ? error.message : "");
        }
      } finally {
        if (!cancelled) {
          setIsPageLoading(false);
        }
      }
    }

    void loadPage();
    return () => {
      cancelled = true;
    };
  }, [route, lang, navigateToRoute]);

  const sections = useMemo(() => sectionMap(page), [page]);
  const heroSection = sections.get("hero");
  const introSection = sections.get("journal-intro");
  const expeditionsSection = sections.get("expeditions");
  const categoriesSection = sections.get("categories");
  const storiesSection = sections.get("stories");
  const contactSection = sections.get("contact");

  const mainMenuItems = menus.main ?? [];
  const footerMenuItems = menus.footer ?? [];
  const socialMenuItems = menus.social ?? [];

  const languages = useMemo(() => {
    const list = [...(content?.languages ?? [])];
    list.sort((a, b) => a.order - b.order || a.code.localeCompare(b.code));
    return list.length
      ? list
      : [{ code: lang, name: lang.toUpperCase(), is_default: true, order: 1 }];
  }, [content, lang]);

  const expeditionCards = payloadItems<ExpeditionCard>(expeditionsSection, "cards");
  const categoryItems = payloadItems<GalleryItem>(categoriesSection, "items");
  const storyItems = payloadItems<StoryItem>(storiesSection, "items");
  const heroImage =
    heroSection?.images[0]?.image_url || payloadText(heroSection, "background_image_url");

  useEffect(() => {
    const isHomeRoute = route.kind === "page" && route.slug === "home";
    if (!isHomeRoute) {
      setIsHeaderVisible(true);
      return;
    }

    if (hasPlayedHomeIntroRef.current) {
      setIsHeaderVisible(true);
      return;
    }

    if (typeof window === "undefined") {
      setIsHeaderVisible(true);
      return;
    }

    const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (prefersReducedMotion) {
      setIsHeaderVisible(true);
      hasPlayedHomeIntroRef.current = true;
      return;
    }

    if (isPageLoading) {
      setIsHeaderVisible(false);
      return;
    }

    if (!heroSection) {
      setIsHeaderVisible(true);
      hasPlayedHomeIntroRef.current = true;
      return;
    }

    setIsHeaderVisible(false);
    const timerId = window.setTimeout(() => {
      setIsHeaderVisible(true);
      hasPlayedHomeIntroRef.current = true;
    }, HOME_HEADER_REVEAL_DELAY_MS);

    return () => window.clearTimeout(timerId);
  }, [heroSection, isPageLoading, route]);

  const expeditions = useMemo(
    () => resolveExpeditions(expeditionsData, expeditionCards, t),
    [expeditionsData, expeditionCards, t]
  );

  const stories = useMemo(
    () => resolveStories(storiesData, storyItems, t),
    [storiesData, storyItems, t]
  );

  const categories = useMemo(
    () => resolveCategories(categoriesData, categoryItems, t),
    [categoriesData, categoryItems, t]
  );

  const activeExpedition = useMemo(() => {
    if (route.kind !== "expedition-detail") {
      return null;
    }
    return expeditions.find((item) => item.slug === route.slug) || null;
  }, [route, expeditions]);

  const activeCategory = useMemo(() => {
    if (route.kind !== "category-detail") {
      return null;
    }
    return categories.find((item) => item.slug === route.slug) || null;
  }, [route, categories]);

  const activeStory = useMemo(() => {
    if (route.kind !== "story-detail") {
      return null;
    }
    return stories.find((item) => item.slug === route.slug) || null;
  }, [route, stories]);

  const detailBlocks = useMemo(() => {
    if (!activeExpedition) {
      return [] as Array<ResolvedMediaBlock & { lightboxIndex?: number }>;
    }
    let imageIndex = 0;
    return activeExpedition.mediaBlocks.map((block) => {
      if (block.kind === "image") {
        const value = { ...block, lightboxIndex: imageIndex };
        imageIndex += 1;
        return value;
      }
      return block;
    });
  }, [activeExpedition]);

  const categoryDetailItems = useMemo(() => {
    if (!activeCategory) {
      return [] as ResolvedCategoryGalleryItem[];
    }
    if (activeCategory.galleryItems.length) {
      return activeCategory.galleryItems;
    }
    if (!activeCategory.imageUrl) {
      return [] as ResolvedCategoryGalleryItem[];
    }
    return [
      {
        title: activeCategory.title,
        description: activeCategory.description,
        imageUrl: activeCategory.imageUrl,
        altText: activeCategory.title,
        lightboxIndex: 0,
      },
    ];
  }, [activeCategory]);

  const lightboxImages = useMemo(() => {
    if (route.kind === "category-detail") {
      return categoryDetailItems.map((item) => ({
        src: item.imageUrl,
        alt: item.altText,
      }));
    }
    return detailBlocks
      .filter((block): block is Extract<typeof block, { kind: "image" }> => block.kind === "image")
      .map((block) => ({
        src: block.imageUrl,
        alt: block.altText,
      }));
  }, [categoryDetailItems, detailBlocks, route.kind]);

  const currentLightboxImage =
    lightboxIndex !== null && lightboxIndex >= 0 ? lightboxImages[lightboxIndex] : undefined;

  const isLoading =
    isI18nLoading ||
    isPageLoading ||
    isNavigationLoading ||
    isExpeditionsLoading ||
    isCategoriesLoading ||
    isStoriesLoading ||
    !content ||
    !page;

  const handleContactSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setSubmitStatus("sending");
    setSubmitMessage("");

    try {
      await sendContactMessage(contactForm);
      setSubmitStatus("success");
      setSubmitMessage(t("form.success"));
      setContactForm({ name: "", email: "", message: "" });
    } catch (error) {
      setSubmitStatus("error");
      setSubmitMessage(
        error instanceof Error && error.message ? error.message : t("form.error")
      );
    }
  };

  const handleNavClick = (event: MouseEvent<HTMLAnchorElement>, item: NavigationItem) => {
    const href = safeHref(item.href);
    if (isExternalHref(href) || item.kind === "external") {
      return;
    }

    if (item.kind === "anchor" || href.startsWith("#") || href.startsWith("/#")) {
      event.preventDefault();
      const anchor = href.replace(/^\/?#/, "");
      if (!anchor) {
        return;
      }
      const scrollToAnchor = () => {
        const target = document.getElementById(anchor);
        if (target) {
          target.scrollIntoView({ behavior: "smooth", block: "start" });
        }
      };

      const isHomePath = route.kind === "page" && route.slug === "home";
      if (!isHomePath) {
        navigateToRoute({ kind: "page", slug: "home" });
        window.setTimeout(scrollToAnchor, 120);
      } else {
        scrollToAnchor();
      }
      return;
    }

    if (item.page_slug) {
      event.preventDefault();
      if (item.page_slug === "expeditions") {
        navigateToRoute({ kind: "expeditions-index" });
      } else {
        navigateToRoute({ kind: "page", slug: item.page_slug });
      }
      return;
    }

    if (href.startsWith("/")) {
      event.preventDefault();
      navigateToRoute(parseRoute(href));
      return;
    }

    if (/^expeditions\/?$/.test(href)) {
      event.preventDefault();
      navigateToRoute({ kind: "expeditions-index" });
    }
  };

  const handleBrandClick = useCallback(() => {
    if (route.kind === "page" && route.slug === "home") {
      window.scrollTo({ top: 0, behavior: "smooth" });
      return;
    }
    navigateToRoute({ kind: "page", slug: "home" });
  }, [navigateToRoute, route]);

  const openExpeditionDetail = useCallback(
    (slug: string) => {
      navigateToRoute({ kind: "expedition-detail", slug });
    },
    [navigateToRoute]
  );

  const openCategoryDetail = useCallback(
    (slug: string) => {
      navigateToRoute({ kind: "category-detail", slug });
    },
    [navigateToRoute]
  );

  const openStoryDetail = useCallback(
    (slug: string) => {
      navigateToRoute({ kind: "story-detail", slug });
    },
    [navigateToRoute]
  );

  const handleExpeditionCardKey = useCallback(
    (event: ReactKeyboardEvent<HTMLElement>, slug: string) => {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        openExpeditionDetail(slug);
      }
    },
    [openExpeditionDetail]
  );

  const handleCategoryCardKey = useCallback(
    (event: ReactKeyboardEvent<HTMLElement>, slug: string) => {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        openCategoryDetail(slug);
      }
    },
    [openCategoryDetail]
  );

  const handleStoryCardKey = useCallback(
    (event: ReactKeyboardEvent<HTMLElement>, slug: string) => {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        openStoryDetail(slug);
      }
    },
    [openStoryDetail]
  );

  const handleLightboxNext = useCallback(() => {
    if (!lightboxImages.length || lightboxIndex === null) {
      return;
    }
    setLightboxIndex((lightboxIndex + 1) % lightboxImages.length);
  }, [lightboxImages.length, lightboxIndex]);

  const handleLightboxPrev = useCallback(() => {
    if (!lightboxImages.length || lightboxIndex === null) {
      return;
    }
    setLightboxIndex((lightboxIndex - 1 + lightboxImages.length) % lightboxImages.length);
  }, [lightboxImages.length, lightboxIndex]);

  const handleLightboxTouchStart = useCallback((event: ReactTouchEvent<HTMLDivElement>) => {
    const touch = event.changedTouches[0];
    lightboxTouchStartX.current = touch.clientX;
    lightboxTouchStartY.current = touch.clientY;
  }, []);

  const handleLightboxTouchEnd = useCallback(
    (event: ReactTouchEvent<HTMLDivElement>) => {
      const touch = event.changedTouches[0];
      const startX = lightboxTouchStartX.current;
      const startY = lightboxTouchStartY.current;
      if (startX === null || startY === null) {
        return;
      }
      const diffX = touch.clientX - startX;
      const diffY = touch.clientY - startY;
      if (Math.abs(diffX) < 50 || Math.abs(diffX) < Math.abs(diffY)) {
        return;
      }
      if (diffX < 0) {
        handleLightboxNext();
      } else {
        handleLightboxPrev();
      }
    },
    [handleLightboxNext, handleLightboxPrev]
  );

  useEffect(() => {
    if (typeof document === "undefined" || lightboxIndex === null) {
      return;
    }
    const originalOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => {
      document.body.style.overflow = originalOverflow;
    };
  }, [lightboxIndex]);

  useEffect(() => {
    if (lightboxIndex === null) {
      return;
    }
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        setLightboxIndex(null);
      } else if (event.key === "ArrowRight") {
        handleLightboxNext();
      } else if (event.key === "ArrowLeft") {
        handleLightboxPrev();
      }
    };
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [lightboxIndex, handleLightboxNext, handleLightboxPrev]);

  if (!content || !content.site || !page) {
    return (
      <div className="page">
        <section className="journal-intro">
          <p>{isLoading ? t("status.loading") : t("status.unavailable")}</p>
          {pageError ? <small className="load-warning">{pageError}</small> : null}
          {navigationError ? <small className="load-warning">{navigationError}</small> : null}
          {expeditionsError ? <small className="load-warning">{expeditionsError}</small> : null}
          {categoriesError ? <small className="load-warning">{categoriesError}</small> : null}
        </section>
      </div>
    );
  }

  const site = content.site;
  const brandName = t("brand.name", site.brand_name);
  const footerTitle = t("footer.title", site.footer_title);
  const footerDescription = t("footer.description", site.footer_description);
  const footerExploreTitle = t("footer.explore", site.footer_explore_title);
  const footerSocialTitle = t("footer.social", site.footer_social_title);
  const footerNewsletterTitle = t("footer.newsletter", site.footer_newsletter_title);
  const newsletterNote = t("footer.newsletter_note", site.newsletter_note);
  const expeditionsTitle = payloadText(
    expeditionsSection,
    "title",
    t("expeditions.index.title", "Recent expeditions")
  );
  const expeditionsSubtitle = payloadText(
    expeditionsSection,
    "subtitle",
    t("expeditions.index.subtitle", "Journeys into the remote.")
  );

  return (
    <div className="page" ref={pageRef}>
      <header
        className="site-header"
        data-nav-visibility={isHeaderVisible ? "visible" : "hidden"}
        ref={headerRef}
      >
        <button
          type="button"
          className="brand brand-link"
          onClick={handleBrandClick}
          aria-label={t("nav.home", "Go to home")}
        >
          {brandName}
        </button>
        <nav className="nav">
          {mainMenuItems.map((item) => (
            <a
              key={item.id}
              href={safeHref(item.href)}
              target={item.open_in_new_tab ? "_blank" : undefined}
              rel={item.open_in_new_tab ? "noreferrer" : undefined}
              onClick={(event) => handleNavClick(event, item)}
            >
              {t(item.label_key, item.label)}
            </a>
          ))}
        </nav>
        <div className="controls">
          <div className="lang-switch" role="group" aria-label={t("lang.switcher")}>
            {languages.map((option) => (
              <button
                key={option.code}
                type="button"
                className={lang === option.code ? "active" : ""}
                onClick={() => {
                  void setLang(option.code);
                }}
              >
                {t(`lang.${option.code}`, option.name)}
              </button>
            ))}
          </div>
          <button
            className="theme-switch"
            type="button"
            onClick={() => setTheme(theme === "light" ? "dark" : "light")}
          >
            {theme === "light" ? t("theme.dark") : t("theme.light")}
          </button>
        </div>
      </header>

      {route.kind === "page" && heroSection ? (
        <section id={heroSection.anchor || "journey"} className="hero" ref={heroRef}>
          <div
            className="hero-media"
            style={heroImage ? { backgroundImage: `url(${heroImage})` } : undefined}
          />
          <div className="hero-overlay" />
          <div className="hero-content">
            <p className="hero-kicker">{payloadText(heroSection, "kicker")}</p>
            <div className="hero-title-wrap">
              <h1>{heroSection.title}</h1>
              <span className="hero-title-line" aria-hidden="true" />
            </div>
            <p className="hero-subtitle">{heroSection.subtitle}</p>
            <div className="hero-scroll-wrap">
              <div className="hero-scroll">
                {payloadText(heroSection, "scroll_label", t("section.hero.scroll_label"))}
              </div>
            </div>
          </div>
        </section>
      ) : null}

      {route.kind === "page" && introSection ? (
        <section id={introSection.anchor} className="journal-intro">
          <p>{introSection.body}</p>
          {pageError ? <small className="load-warning">{pageError}</small> : null}
          {navigationError ? <small className="load-warning">{navigationError}</small> : null}
          {expeditionsError ? <small className="load-warning">{expeditionsError}</small> : null}
          {categoriesError ? <small className="load-warning">{categoriesError}</small> : null}
          {storiesError ? <small className="load-warning">{storiesError}</small> : null}
        </section>
      ) : null}

      {route.kind === "page" && expeditionsSection ? (
        <section id={expeditionsSection.anchor} className="section expeditions">
          <div className="section-heading">
            <div>
              <p className="section-eyebrow">{payloadText(expeditionsSection, "eyebrow")}</p>
              <h2>{payloadText(expeditionsSection, "title")}</h2>
              <p className="section-subtitle">{payloadText(expeditionsSection, "subtitle")}</p>
            </div>
            <button
              className="ghost-button"
              type="button"
              onClick={() => navigateToRoute({ kind: "expeditions-index" })}
            >
              {payloadText(expeditionsSection, "action_label")}
            </button>
          </div>
          <div className="expedition-grid">
            {expeditions.map((item, index) => (
              <article
                key={`${item.slug || index}-${index}`}
                className="expedition-card interactive-card"
                tabIndex={0}
                role="button"
                onClick={() => openExpeditionDetail(item.slug)}
                onKeyDown={(event) => handleExpeditionCardKey(event, item.slug)}
                aria-label={`${t("expeditions.index.card_cta", "Open expedition")}: ${
                  item.title
                }`}
              >
                <div className="expedition-image">
                  <div
                    className="expedition-image-media"
                    style={item.imageUrl ? { backgroundImage: `url(${item.imageUrl})` } : undefined}
                    aria-hidden="true"
                  />
                  <span>{item.dateLabel || ""}</span>
                </div>
                <div className="expedition-copy">
                  <h3>{item.title || ""}</h3>
                  <p>{item.subtitle || ""}</p>
                </div>
              </article>
            ))}
          </div>
        </section>
      ) : null}

      {route.kind === "page" && categoriesSection ? (
        <section id={categoriesSection.anchor} className="section categories">
          <div className="section-heading">
            <div>
              <p className="section-eyebrow">{payloadText(categoriesSection, "eyebrow")}</p>
              <h2>{payloadText(categoriesSection, "title")}</h2>
              <p className="section-subtitle">{payloadText(categoriesSection, "subtitle")}</p>
            </div>
          </div>
          <div className="category-grid">
            {categories.map((item, index) => (
              <article
                key={`${item.slug || index}-${index}`}
                className={`category-card interactive-card ${item.size || "small"}`}
                tabIndex={0}
                role="button"
                onClick={() => openCategoryDetail(item.slug)}
                onKeyDown={(event) => handleCategoryCardKey(event, item.slug)}
                aria-label={`${t("category.card.cta", "Open focus area")}: ${item.title || ""}`}
              >
                <div
                  className="category-image-media"
                  style={item.imageUrl ? { backgroundImage: `url(${item.imageUrl})` } : undefined}
                  aria-hidden="true"
                />
                <div className="category-overlay">
                  <h3>{item.title || ""}</h3>
                </div>
              </article>
            ))}
          </div>
        </section>
      ) : null}

      {route.kind === "page" && storiesSection ? (
        <section id={storiesSection.anchor} className="section stories">
          <div className="section-heading center">
            <div>
              <p className="section-eyebrow">{payloadText(storiesSection, "eyebrow")}</p>
              <h2>{payloadText(storiesSection, "title")}</h2>
            </div>
          </div>
          <div className="story-list">
            {stories.map((item, index) => (
              <article
                key={`${item.slug || index}-${index}`}
                className={`story-item ${index % 2 === 0 ? "" : "reverse"}`}
                role="button"
                tabIndex={0}
                onClick={() => openStoryDetail(item.slug)}
                onKeyDown={(event) => handleStoryCardKey(event, item.slug)}
                aria-label={`${t("stories.index.card_cta", "Open story")}: ${item.title || ""}`}
              >
                <div
                  className="story-image interactive-card"
                >
                  <div
                    className="story-image-media"
                    style={item.imageUrl ? { backgroundImage: `url(${item.imageUrl})` } : undefined}
                    aria-hidden="true"
                  />
                </div>
                <div className="story-copy">
                  <span>{item.dateLabel || ""}</span>
                  <h3>{item.title || ""}</h3>
                  <p>{item.description || ""}</p>
                  <button className="link-button" type="button" onClick={() => openStoryDetail(item.slug)}>
                    {payloadText(storiesSection, "action_label")}
                  </button>
                </div>
              </article>
            ))}
          </div>
        </section>
      ) : null}

      {route.kind === "page" && contactSection ? (
        <section id={contactSection.anchor} className="section contact">
          <div className="contact-inner">
            <div className="contact-copy">
              <h2>{contactSection.title}</h2>
              <p>{contactSection.body}</p>
              <div className="contact-details">
                <div>
                  <p className="detail-label">{t("detail.location")}</p>
                  <p>{payloadText(contactSection, "location", "-")}</p>
                </div>
                <div>
                  <p className="detail-label">{t("detail.email")}</p>
                  <p>{payloadText(contactSection, "email", site.contact_email)}</p>
                </div>
                <div>
                  <p className="detail-label">{t("detail.socials")}</p>
                  <p>
                    {socialMenuItems.length
                      ? socialMenuItems.map((item) => t(item.label_key, item.label)).join(" | ")
                      : "-"}
                  </p>
                </div>
              </div>
            </div>
            <form className="contact-form" onSubmit={handleContactSubmit}>
              <label>
                {t("form.name.label")}
                <input
                  type="text"
                  placeholder={t("form.name.placeholder")}
                  value={contactForm.name}
                  onChange={(event) =>
                    setContactForm((prev) => ({ ...prev, name: event.target.value }))
                  }
                  required
                />
              </label>
              <label>
                {t("form.email.label")}
                <input
                  type="email"
                  placeholder={t("form.email.placeholder")}
                  value={contactForm.email}
                  onChange={(event) =>
                    setContactForm((prev) => ({ ...prev, email: event.target.value }))
                  }
                  required
                />
              </label>
              <label>
                {t("form.message.label")}
                <textarea
                  rows={4}
                  placeholder={t("form.message.placeholder")}
                  value={contactForm.message}
                  onChange={(event) =>
                    setContactForm((prev) => ({ ...prev, message: event.target.value }))
                  }
                  required
                />
              </label>
              <button type="submit" disabled={submitStatus === "sending"}>
                {submitStatus === "sending" ? t("form.sending") : t("form.submit")}
              </button>
              {submitMessage ? (
                <small
                  className={
                    submitStatus === "error" ? "status-line error" : "status-line success"
                  }
                >
                  {submitMessage}
                </small>
              ) : null}
            </form>
          </div>
        </section>
      ) : null}

      {route.kind === "expeditions-index" ? (
        <section className="section expeditions-index">
          <div className="section-heading">
            <div>
              <p className="section-eyebrow">{expeditionsSubtitle}</p>
              <h2>{expeditionsTitle}</h2>
            </div>
          </div>
          {expeditionsError ? <small className="load-warning">{expeditionsError}</small> : null}
          <div className="expedition-grid">
            {expeditions.map((item, index) => (
              <article
                key={`${item.slug || index}-${index}`}
                className="expedition-card interactive-card expedition-card-index"
                tabIndex={0}
                role="button"
                onClick={() => openExpeditionDetail(item.slug)}
                onKeyDown={(event) => handleExpeditionCardKey(event, item.slug)}
                aria-label={`${t("expeditions.index.card_cta", "Open expedition")}: ${
                  item.title
                }`}
              >
                <div className="expedition-image">
                  <div
                    className="expedition-image-media"
                    style={item.imageUrl ? { backgroundImage: `url(${item.imageUrl})` } : undefined}
                    aria-hidden="true"
                  />
                  <span>{item.dateLabel || ""}</span>
                </div>
                <div className="expedition-copy">
                  <h3>{item.title || ""}</h3>
                  <p>{item.subtitle || ""}</p>
                </div>
              </article>
            ))}
          </div>
        </section>
      ) : null}

      {route.kind === "expedition-detail" ? (
        <section className="section expedition-detail">
          <button
            type="button"
            className="link-button expedition-back"
            onClick={() => navigateToRoute({ kind: "expeditions-index" })}
          >
            {t("expedition.detail.back", "Back to expeditions")}
          </button>

          {!activeExpedition ? (
            <p className="section-subtitle">{t("status.unavailable", "Content is unavailable.")}</p>
          ) : (
            <>
              <header className="expedition-detail-header">
                <p className="section-eyebrow">{activeExpedition.dateLabel}</p>
                <h2>{activeExpedition.title}</h2>
                <p className="section-subtitle expedition-detail-lead">
                  {activeExpedition.description}
                </p>
              </header>

              <div className="expedition-detail-grid">
                {detailBlocks.map((block, index) => {
                  if (block.kind === "story") {
                    return (
                      <article key={`story-${index}`} className="expedition-rich-story">
                        <h3>{block.title}</h3>
                        <p>{block.body}</p>
                      </article>
                    );
                  }

                  if (block.kind === "video") {
                    return (
                      <article key={`video-${index}`} className="expedition-media-card video">
                        {block.videoUrl ? (
                          <video controls preload="metadata" src={block.videoUrl} />
                        ) : (
                          <div className="video-placeholder">
                            <span>
                              {t(
                                "expedition.detail.video_placeholder",
                                "Video placeholder"
                              )}
                            </span>
                          </div>
                        )}
                        <h4>{block.title}</h4>
                      </article>
                    );
                  }

                  return (
                    <button
                      key={`image-${index}`}
                      type="button"
                      className="expedition-media-card image"
                      onClick={() => setLightboxIndex(block.lightboxIndex ?? 0)}
                      aria-label={`${t("lightbox.open_image", "Open image")}: ${block.altText}`}
                    >
                      <img src={block.imageUrl} alt={block.altText} />
                      <h4>{block.title}</h4>
                    </button>
                  );
                })}
              </div>
            </>
          )}
        </section>
      ) : null}

      {route.kind === "category-detail" ? (
        <section className="section expedition-detail category-detail">
          <button
            type="button"
            className="link-button expedition-back"
            onClick={() => {
              navigateToRoute({ kind: "page", slug: "home" });
              window.setTimeout(() => {
                const anchorId = categoriesSection?.anchor || "categories";
                const target = document.getElementById(anchorId);
                if (target) {
                  target.scrollIntoView({ behavior: "smooth", block: "start" });
                }
              }, 120);
            }}
          >
            {t("category.detail.back", "Back to focus areas")}
          </button>

          {!activeCategory ? (
            <p className="section-subtitle">{t("status.unavailable", "Content is unavailable.")}</p>
          ) : (
            <>
              <header className="expedition-detail-header">
                <p className="section-eyebrow">{t("category.detail.gallery_title", "Gallery")}</p>
                <h2>{activeCategory.title}</h2>
                <p className="section-subtitle expedition-detail-lead">{activeCategory.description}</p>
              </header>
              <div className="category-detail-grid">
                {categoryDetailItems.map((item, index) => (
                  <button
                    key={`${item.title || index}-${index}`}
                    type="button"
                    className="category-gallery-card"
                    onClick={() => setLightboxIndex(item.lightboxIndex)}
                    aria-label={`${t("lightbox.open_image", "Open image")}: ${item.altText}`}
                  >
                    <img src={item.imageUrl} alt={item.altText} />
                    <div className="category-gallery-copy">
                      <h4>{item.title}</h4>
                      {item.description ? <p>{item.description}</p> : null}
                    </div>
                  </button>
                ))}
              </div>
            </>
          )}
        </section>
      ) : null}

      {route.kind === "story-detail" ? (
        <section className="section expedition-detail">
          <button
            type="button"
            className="link-button expedition-back"
            onClick={() => {
              navigateToRoute({ kind: "page", slug: "home" });
              window.setTimeout(() => {
                const anchorId = storiesSection?.anchor || "stories";
                const target = document.getElementById(anchorId);
                if (target) {
                  target.scrollIntoView({ behavior: "smooth", block: "start" });
                }
              }, 120);
            }}
          >
            {t("story.detail.back", "Back to stories")}
          </button>

          {!activeStory ? (
            <p className="section-subtitle">{t("status.unavailable", "Content is unavailable.")}</p>
          ) : (
            <>
              <header className="expedition-detail-header">
                <p className="section-eyebrow">{activeStory.dateLabel}</p>
                <h2>{activeStory.title}</h2>
                <p className="section-subtitle expedition-detail-lead">{activeStory.description}</p>
              </header>
              {activeStory.imageUrl ? (
                <article className="expedition-media-card image">
                  <img src={activeStory.imageUrl} alt={activeStory.title} />
                </article>
              ) : null}
            </>
          )}
        </section>
      ) : null}

      <footer className="footer">
        <div>
          <h3>{footerTitle}</h3>
          <p>{footerDescription}</p>
        </div>
        <div className="footer-links">
          <div>
            <p className="detail-label">{footerExploreTitle}</p>
            {footerMenuItems.map((item) => (
              <p key={item.id}>
                <a
                  href={safeHref(item.href)}
                  target={item.open_in_new_tab ? "_blank" : undefined}
                  rel={item.open_in_new_tab ? "noreferrer" : undefined}
                  onClick={(event) => handleNavClick(event, item)}
                >
                  {t(item.label_key, item.label)}
                </a>
              </p>
            ))}
          </div>
          <div>
            <p className="detail-label">{footerSocialTitle}</p>
            <div className="socials">
              {socialMenuItems.map((item) => (
                <a
                  key={item.id}
                  href={safeHref(item.href)}
                  title={t(item.label_key, item.label)}
                  target={item.open_in_new_tab ? "_blank" : undefined}
                  rel={item.open_in_new_tab ? "noreferrer" : undefined}
                >
                  {t(item.label_key, item.label)}
                </a>
              ))}
            </div>
          </div>
          <div>
            <p className="detail-label">{footerNewsletterTitle}</p>
            <p>{newsletterNote}</p>
            <div className="newsletter">
              <input type="email" placeholder={t("newsletter.placeholder")} />
              <button type="button">{t("newsletter.button")}</button>
            </div>
          </div>
        </div>
      </footer>

      {currentLightboxImage ? (
        <div
          className="lightbox"
          role="dialog"
          aria-modal="true"
          aria-label={t("lightbox.open_image", "Open image")}
        >
          <button
            type="button"
            className="lightbox-backdrop"
            aria-label={t("lightbox.close", "Close")}
            onClick={() => setLightboxIndex(null)}
          />
          <div
            className="lightbox-panel"
            onTouchStart={handleLightboxTouchStart}
            onTouchEnd={handleLightboxTouchEnd}
          >
            <button
              type="button"
              className="lightbox-close"
              onClick={() => setLightboxIndex(null)}
              aria-label={t("lightbox.close", "Close")}
            >
              {t("lightbox.close", "Close")}
            </button>
            <button
              type="button"
              className="lightbox-nav prev"
              onClick={handleLightboxPrev}
              aria-label={t("lightbox.prev", "Previous")}
            >
              {t("lightbox.prev", "Previous")}
            </button>
            <figure className="lightbox-figure">
              <img
                src={currentLightboxImage.src}
                alt={currentLightboxImage.alt}
                className="lightbox-image"
              />
            </figure>
            <button
              type="button"
              className="lightbox-nav next"
              onClick={handleLightboxNext}
              aria-label={t("lightbox.next", "Next")}
            >
              {t("lightbox.next", "Next")}
            </button>
          </div>
        </div>
      ) : null}
    </div>
  );
}
