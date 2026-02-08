import { FormEvent, useEffect, useMemo, useState } from "react";
import { getSiteStructure, sendContactMessage } from "./api";
import { useI18n } from "./i18n";
import type {
  ContactMessagePayload,
  SiteStructureResponse,
  StructureSection,
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

const BRAND_NAME = "Romanweiẞ";
const THEME_STORAGE_KEY = "site.theme";

function readInitialTheme(): ThemeMode {
  if (typeof window === "undefined") {
    return "light";
  }
  const saved = window.localStorage.getItem(THEME_STORAGE_KEY);
  return saved === "dark" ? "dark" : "light";
}

function sectionMap(data: SiteStructureResponse | null): Map<string, StructureSection> {
  const map = new Map<string, StructureSection>();
  for (const section of data?.sections ?? []) {
    map.set(section.key, section);
  }
  return map;
}

function sectionText(
  section: StructureSection | undefined,
  field: "title" | "subtitle" | "body",
  t: (key: string, fallback?: string) => string
): string {
  if (!section) {
    return "";
  }
  if (field === "title") {
    return t(section.title_key, section.title);
  }
  if (field === "subtitle") {
    return t(section.subtitle_key, section.subtitle);
  }
  return t(section.body_key, section.body);
}

function payloadText(
  section: StructureSection | undefined,
  field: string,
  t: (key: string, fallback?: string) => string,
  fallback = ""
): string {
  if (!section) {
    return fallback;
  }

  const value = section.payload[field];
  const asText = typeof value === "string" ? value : fallback;
  const key = section.payload_keys[field];
  return key ? t(key, asText) : asText;
}

function payloadItems<T>(section: StructureSection | undefined, key: string): T[] {
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

export default function App() {
  const { lang, setLang, t, isLoading: isI18nLoading } = useI18n();

  const [theme, setTheme] = useState<ThemeMode>(readInitialTheme);
  const [isHeaderSolid, setIsHeaderSolid] = useState<boolean>(false);
  const [structure, setStructure] = useState<SiteStructureResponse | null>(null);
  const [isStructureLoading, setIsStructureLoading] = useState<boolean>(true);
  const [structureError, setStructureError] = useState<string>("");
  const [contactForm, setContactForm] = useState<ContactMessagePayload>({
    name: "",
    email: "",
    message: "",
  });
  const [submitStatus, setSubmitStatus] = useState<SubmitStatus>("idle");
  const [submitMessage, setSubmitMessage] = useState<string>("");

  useEffect(() => {
    if (typeof document === "undefined") {
      return;
    }
    if (!structure?.site) {
      document.title = BRAND_NAME;
      return;
    }
    document.title = t(
      structure.site.brand_key,
      structure.site.brand_name || BRAND_NAME
    );
  }, [structure, t]);

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

    const onScroll = () => {
      setIsHeaderSolid(window.scrollY > 24);
    };

    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  useEffect(() => {
    let cancelled = false;

    async function loadStructure() {
      setIsStructureLoading(true);
      setStructureError("");
      try {
        const data = await getSiteStructure(lang);
        if (!cancelled) {
          setStructure(data);
        }
      } catch (error) {
        if (!cancelled) {
          setStructure(null);
          setStructureError(error instanceof Error ? error.message : "");
        }
      } finally {
        if (!cancelled) {
          setIsStructureLoading(false);
        }
      }
    }

    void loadStructure();
    return () => {
      cancelled = true;
    };
  }, [lang]);

  const sections = useMemo(() => sectionMap(structure), [structure]);
  const heroSection = sections.get("hero");
  const introSection = sections.get("journal-intro");
  const expeditionsSection = sections.get("expeditions");
  const categoriesSection = sections.get("categories");
  const storiesSection = sections.get("stories");
  const contactSection = sections.get("contact");

  const mainMenuItems = structure?.menus.main ?? [];
  const footerMenuItems = structure?.menus.footer ?? [];
  const socialMenuItems = structure?.menus.social ?? [];

  const languages = useMemo(() => {
    const list = [...(structure?.languages ?? [])];
    list.sort((a, b) => a.order - b.order || a.code.localeCompare(b.code));
    return list.length
      ? list
      : [{ code: lang, name: lang.toUpperCase(), is_default: true, order: 1 }];
  }, [structure, lang]);

  const expeditionCards = payloadItems<ExpeditionCard>(expeditionsSection, "cards");
  const categoryItems = payloadItems<GalleryItem>(categoriesSection, "items");
  const storyItems = payloadItems<StoryItem>(storiesSection, "items");
  const heroImage =
    heroSection?.images[0]?.image_url || payloadText(heroSection, "background_image_url", t);

  const isLoading = isI18nLoading || isStructureLoading;

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

  if (!structure || !structure.site) {
    return (
      <div className="page">
        <section className="journal-intro">
          <p>{isLoading ? t("status.loading") : t("status.unavailable")}</p>
          {structureError ? <small className="load-warning">{structureError}</small> : null}
        </section>
      </div>
    );
  }

  const site = structure.site;
  const brandName = t(site.brand_key, site.brand_name || BRAND_NAME);
  const footerTitle = t(site.footer_title_key, site.footer_title || BRAND_NAME);
  const footerDescription = t(site.footer_description_key, site.footer_description);
  const footerExploreTitle = t(site.footer_explore_title_key, site.footer_explore_title);
  const footerSocialTitle = t(site.footer_social_title_key, site.footer_social_title);
  const footerNewsletterTitle = t(
    site.footer_newsletter_title_key,
    site.footer_newsletter_title
  );
  const newsletterNote = t(site.newsletter_note_key, site.newsletter_note);

  return (
    <div className="page">
      <header className={`site-header ${isHeaderSolid || !heroSection ? "solid" : ""}`}>
        <div className="brand">{brandName}</div>
        <nav className="nav">
          {mainMenuItems.map((item) => (
            <a
              key={item.id}
              href={safeHref(item.href)}
              target={item.open_in_new_tab ? "_blank" : undefined}
              rel={item.open_in_new_tab ? "noreferrer" : undefined}
            >
              {t(item.label_key, item.label)}
            </a>
          ))}
        </nav>
        <div className="controls">
          <div className="lang-switch" role="group" aria-label={t("lang.switcher", "Language")}>
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
        <section id={heroSection.anchor || "journey"} className="hero">
          <div
            className="hero-media"
            style={heroImage ? { backgroundImage: `url(${heroImage})` } : undefined}
          />
          <div className="hero-overlay" />
          <div className="hero-content">
            <p className="hero-kicker">{payloadText(heroSection, "kicker", t)}</p>
            <h1>{sectionText(heroSection, "title", t)}</h1>
            <p className="hero-subtitle">{sectionText(heroSection, "subtitle", t)}</p>
            <div className="hero-scroll">
              {payloadText(heroSection, "scroll_label", t, t("section.hero.scroll_label"))}
            </div>
          </div>
        </section>
      ) : null}

      {introSection ? (
        <section id={introSection.anchor} className="journal-intro">
          <p>{sectionText(introSection, "body", t)}</p>
          {structureError ? <small className="load-warning">{structureError}</small> : null}
        </section>
      ) : null}

      {expeditionsSection ? (
        <section id={expeditionsSection.anchor} className="section expeditions">
          <div className="section-heading">
            <div>
              <p className="section-eyebrow">
                {payloadText(expeditionsSection, "eyebrow", t)}
              </p>
              <h2>{payloadText(expeditionsSection, "title", t)}</h2>
              <p className="section-subtitle">
                {payloadText(expeditionsSection, "subtitle", t)}
              </p>
            </div>
            <button className="ghost-button" type="button">
              {payloadText(expeditionsSection, "action_label", t)}
            </button>
          </div>
          <div className="expedition-grid">
            {expeditionCards.map((item, index) => (
              <article key={`${item.title || index}-${index}`} className="expedition-card">
                <div
                  className="expedition-image"
                  style={item.image_url ? { backgroundImage: `url(${item.image_url})` } : undefined}
                >
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
              <p className="section-eyebrow">{payloadText(categoriesSection, "eyebrow", t)}</p>
              <h2>{payloadText(categoriesSection, "title", t)}</h2>
              <p className="section-subtitle">{payloadText(categoriesSection, "subtitle", t)}</p>
            </div>
          </div>
          <div className="category-grid">
            {categoryItems.map((item, index) => (
              <div
                key={`${item.title || index}-${index}`}
                className={`category-card ${item.size || "small"}`}
                style={item.image_url ? { backgroundImage: `url(${item.image_url})` } : undefined}
              >
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
              <p className="section-eyebrow">{payloadText(storiesSection, "eyebrow", t)}</p>
              <h2>{payloadText(storiesSection, "title", t)}</h2>
            </div>
          </div>
          <div className="story-list">
            {storyItems.map((item, index) => (
              <article
                key={`${item.title || index}-${index}`}
                className={`story-item ${index % 2 === 0 ? "" : "reverse"}`}
              >
                <div
                  className="story-image"
                  style={item.image_url ? { backgroundImage: `url(${item.image_url})` } : undefined}
                />
                <div className="story-copy">
                  <span>{item.date_label || ""}</span>
                  <h3>{item.title || ""}</h3>
                  <p>{item.description || ""}</p>
                  <button className="link-button" type="button">
                    {payloadText(storiesSection, "action_label", t)}
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
              <h2>{sectionText(contactSection, "title", t)}</h2>
              <p>{sectionText(contactSection, "body", t)}</p>
              <div className="contact-details">
                <div>
                  <p className="detail-label">{t("detail.location")}</p>
                  <p>{payloadText(contactSection, "location", t, "-")}</p>
                </div>
                <div>
                  <p className="detail-label">{t("detail.email")}</p>
                  <p>{payloadText(contactSection, "email", t, site.contact_email)}</p>
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
