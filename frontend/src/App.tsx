import {
  FormEvent,
  type MouseEvent,
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";
import { getNavigation, getPageBySlug, sendContactMessage } from "./api";
import { useI18n } from "./i18n";
import type {
  ContactMessagePayload,
  NavigationItem,
  PageData,
  PageSection,
} from "./types";

type SubmitStatus = "idle" | "sending" | "success" | "error";
type ThemeMode = "light" | "dark";

type ExpeditionCard = {
  title?: string;
  date_label?: string;
  description?: string;
  image_url?: string;
};

type GalleryItem = {
  title?: string;
  image_url?: string;
  size?: "large" | "small" | "wide";
};

type StoryItem = {
  title?: string;
  date_label?: string;
  description?: string;
  image_url?: string;
};

const THEME_STORAGE_KEY = "site.theme";

function readInitialTheme(): ThemeMode {
  if (typeof window === "undefined") {
    return "light";
  }
  const saved = window.localStorage.getItem(THEME_STORAGE_KEY);
  return saved === "dark" ? "dark" : "light";
}

function pathToSlug(pathname: string): string {
  const cleaned = pathname.replace(/^\/+|\/+$/g, "");
  return cleaned || "home";
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

export default function App() {
  const { lang, setLang, t, isLoading: isI18nLoading, content } = useI18n();

  const [theme, setTheme] = useState<ThemeMode>(readInitialTheme);
  const [currentSlug, setCurrentSlug] = useState<string>(() =>
    typeof window === "undefined" ? "home" : pathToSlug(window.location.pathname)
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
  const [contactForm, setContactForm] = useState<ContactMessagePayload>({
    name: "",
    email: "",
    message: "",
  });
  const [submitStatus, setSubmitStatus] = useState<SubmitStatus>("idle");
  const [submitMessage, setSubmitMessage] = useState<string>("");
  const pageRef = useRef<HTMLDivElement | null>(null);
  const headerRef = useRef<HTMLElement | null>(null);
  const heroRef = useRef<HTMLElement | null>(null);

  const navigateToSlug = useCallback(
    (slug: string, replace = false) => {
      if (typeof window === "undefined") {
        return;
      }
      const pageMeta = content?.pages.find((item) => item.slug === slug);
      const path = pageMeta?.is_home || slug === "home" ? "/" : `/${slug}/`;
      if (replace) {
        window.history.replaceState({}, "", `${path}${window.location.search}`);
      } else {
        window.history.pushState({}, "", `${path}${window.location.search}`);
      }
      setCurrentSlug(slug);
      window.scrollTo({ top: 0, behavior: "smooth" });
    },
    [content]
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
  }, [page]);

  useEffect(() => {
    if (typeof window === "undefined") {
      return;
    }
    const onPopState = () => {
      setCurrentSlug(pathToSlug(window.location.pathname));
    };
    window.addEventListener("popstate", onPopState);
    return () => window.removeEventListener("popstate", onPopState);
  }, []);

  useEffect(() => {
    if (!content?.pages?.length) {
      return;
    }
    const exists = content.pages.some((item) => item.slug === currentSlug);
    if (exists || currentSlug === "home") {
      return;
    }
    const homePage = content.pages.find((item) => item.is_home) || content.pages[0];
    if (homePage) {
      navigateToSlug(homePage.slug, true);
    }
  }, [content, currentSlug, navigateToSlug]);

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

    async function loadPage() {
      setIsPageLoading(true);
      setPageError("");
      try {
        const slug = currentSlug || "home";
        const data = await getPageBySlug(slug, lang);
        if (!cancelled) {
          setPage(data.page);
        }
      } catch (error) {
        if (!cancelled) {
          if (currentSlug !== "home") {
            navigateToSlug("home", true);
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
  }, [currentSlug, lang, navigateToSlug]);

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

  const isLoading =
    isI18nLoading || isPageLoading || isNavigationLoading || !content || !page;

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

      const isHomePath = currentSlug === "home" || window.location.pathname === "/";
      if (!isHomePath) {
        navigateToSlug("home");
        window.setTimeout(scrollToAnchor, 120);
      } else {
        scrollToAnchor();
      }
      return;
    }

    if (item.page_slug) {
      event.preventDefault();
      navigateToSlug(item.page_slug);
      return;
    }

    if (href.startsWith("/")) {
      event.preventDefault();
      navigateToSlug(pathToSlug(href));
    }
  };

  if (!content || !content.site || !page) {
    return (
      <div className="page">
        <section className="journal-intro">
          <p>{isLoading ? t("status.loading") : t("status.unavailable")}</p>
          {pageError ? <small className="load-warning">{pageError}</small> : null}
          {navigationError ? <small className="load-warning">{navigationError}</small> : null}
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

  return (
    <div className="page" ref={pageRef}>
      <header className="site-header" ref={headerRef}>
        <div className="brand">{brandName}</div>
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

      {heroSection ? (
        <section id={heroSection.anchor || "journey"} className="hero" ref={heroRef}>
          <div
            className="hero-media"
            style={heroImage ? { backgroundImage: `url(${heroImage})` } : undefined}
          />
          <div className="hero-overlay" />
          <div className="hero-content">
            <p className="hero-kicker">{payloadText(heroSection, "kicker")}</p>
            <h1>{heroSection.title}</h1>
            <p className="hero-subtitle">{heroSection.subtitle}</p>
            <div className="hero-scroll">
              {payloadText(heroSection, "scroll_label", t("section.hero.scroll_label"))}
            </div>
          </div>
        </section>
      ) : null}

      {introSection ? (
        <section id={introSection.anchor} className="journal-intro">
          <p>{introSection.body}</p>
          {pageError ? <small className="load-warning">{pageError}</small> : null}
          {navigationError ? <small className="load-warning">{navigationError}</small> : null}
        </section>
      ) : null}

      {expeditionsSection ? (
        <section id={expeditionsSection.anchor} className="section expeditions">
          <div className="section-heading">
            <div>
              <p className="section-eyebrow">{payloadText(expeditionsSection, "eyebrow")}</p>
              <h2>{payloadText(expeditionsSection, "title")}</h2>
              <p className="section-subtitle">{payloadText(expeditionsSection, "subtitle")}</p>
            </div>
            <button className="ghost-button" type="button">
              {payloadText(expeditionsSection, "action_label")}
            </button>
          </div>
          <div className="expedition-grid">
            {expeditionCards.map((item, index) => (
              <article
                key={`${item.title || index}-${index}`}
                className="expedition-card interactive-card"
                tabIndex={0}
              >
                <div
                  className="expedition-image"
                >
                  <div
                    className="expedition-image-media"
                    style={item.image_url ? { backgroundImage: `url(${item.image_url})` } : undefined}
                    aria-hidden="true"
                  />
                  <span>{item.date_label || ""}</span>
                </div>
                <div className="expedition-copy">
                  <h3>{item.title || ""}</h3>
                  <p>{item.description || ""}</p>
                </div>
              </article>
            ))}
          </div>
        </section>
      ) : null}

      {categoriesSection ? (
        <section id={categoriesSection.anchor} className="section categories">
          <div className="section-heading">
            <div>
              <p className="section-eyebrow">{payloadText(categoriesSection, "eyebrow")}</p>
              <h2>{payloadText(categoriesSection, "title")}</h2>
              <p className="section-subtitle">{payloadText(categoriesSection, "subtitle")}</p>
            </div>
          </div>
          <div className="category-grid">
            {categoryItems.map((item, index) => (
              <div
                key={`${item.title || index}-${index}`}
                className={`category-card interactive-card ${item.size || "small"}`}
                tabIndex={0}
              >
                <div
                  className="category-image-media"
                  style={item.image_url ? { backgroundImage: `url(${item.image_url})` } : undefined}
                  aria-hidden="true"
                />
                <div className="category-overlay">
                  <h3>{item.title || ""}</h3>
                </div>
              </div>
            ))}
          </div>
        </section>
      ) : null}

      {storiesSection ? (
        <section id={storiesSection.anchor} className="section stories">
          <div className="section-heading center">
            <div>
              <p className="section-eyebrow">{payloadText(storiesSection, "eyebrow")}</p>
              <h2>{payloadText(storiesSection, "title")}</h2>
            </div>
          </div>
          <div className="story-list">
            {storyItems.map((item, index) => (
              <article
                key={`${item.title || index}-${index}`}
                className={`story-item ${index % 2 === 0 ? "" : "reverse"}`}
              >
                <div
                  className="story-image interactive-card"
                  tabIndex={0}
                >
                  <div
                    className="story-image-media"
                    style={item.image_url ? { backgroundImage: `url(${item.image_url})` } : undefined}
                    aria-hidden="true"
                  />
                </div>
                <div className="story-copy">
                  <span>{item.date_label || ""}</span>
                  <h3>{item.title || ""}</h3>
                  <p>{item.description || ""}</p>
                  <button className="link-button" type="button">
                    {payloadText(storiesSection, "action_label")}
                  </button>
                </div>
              </article>
            ))}
          </div>
        </section>
      ) : null}

      {contactSection ? (
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
    </div>
  );
}
