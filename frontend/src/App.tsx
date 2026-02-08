import { FormEvent, useEffect, useMemo, useState } from "react";
import { getCmsBootstrap, sendContactMessage } from "./api";
import "./index.css";
import type {
  CmsBootstrap,
  ContactMessagePayload,
  Locale,
  PageSection,
  UiTexts,
} from "./types";

type SubmitStatus = "idle" | "sending" | "success" | "error";
type ThemeMode = "light" | "dark";

type SectionHeadingProps = {
  eyebrow: string;
  title: string;
  subtitle?: string;
  centered?: boolean;
  actionLabel?: string;
};

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

const LOCALE_STORAGE_KEY = "romanweiss.locale";
const THEME_STORAGE_KEY = "romanweiss.theme";

const FALLBACK_UI: Record<Locale, UiTexts> = {
  en: {
    loading_content: "Loading content...",
    content_unavailable: "Content is unavailable.",
    detail_location: "Location",
    detail_email: "Email",
    detail_socials: "Socials",
    contact_name_label: "Name",
    contact_name_placeholder: "Your name",
    contact_email_label: "Email",
    contact_email_placeholder: "your@email.com",
    contact_message_label: "Message",
    contact_message_placeholder: "Tell me about your project...",
    contact_submit: "Send message",
    contact_sending: "Sending...",
    contact_success: "Message sent. Thank you.",
    contact_error_default: "Could not send message.",
    newsletter_placeholder: "Email address",
    newsletter_button: "Join",
    theme_light: "Light",
    theme_dark: "Dark",
    lang_en: "EN",
    lang_ru: "RU",
    lang_zh: "中文",
  },
  ru: {
    loading_content: "Загрузка контента...",
    content_unavailable: "Контент недоступен.",
    detail_location: "Локация",
    detail_email: "Email",
    detail_socials: "Соцсети",
    contact_name_label: "Имя",
    contact_name_placeholder: "Ваше имя",
    contact_email_label: "Email",
    contact_email_placeholder: "your@email.com",
    contact_message_label: "Сообщение",
    contact_message_placeholder: "Расскажите о вашем проекте...",
    contact_submit: "Отправить",
    contact_sending: "Отправка...",
    contact_success: "Сообщение отправлено. Спасибо.",
    contact_error_default: "Не удалось отправить сообщение.",
    newsletter_placeholder: "Email адрес",
    newsletter_button: "Подписаться",
    theme_light: "Светлая",
    theme_dark: "Тёмная",
    lang_en: "EN",
    lang_ru: "RU",
    lang_zh: "中文",
  },
  zh: {
    loading_content: "正在加载内容...",
    content_unavailable: "内容不可用。",
    detail_location: "地点",
    detail_email: "邮箱",
    detail_socials: "社交",
    contact_name_label: "姓名",
    contact_name_placeholder: "你的姓名",
    contact_email_label: "邮箱",
    contact_email_placeholder: "your@email.com",
    contact_message_label: "留言",
    contact_message_placeholder: "请介绍一下你的项目...",
    contact_submit: "发送消息",
    contact_sending: "发送中...",
    contact_success: "消息已发送。谢谢。",
    contact_error_default: "发送失败。",
    newsletter_placeholder: "邮箱地址",
    newsletter_button: "订阅",
    theme_light: "浅色",
    theme_dark: "深色",
    lang_en: "EN",
    lang_ru: "RU",
    lang_zh: "中文",
  },
};

function getInitialLocale(): Locale {
  if (typeof window === "undefined") {
    return "en";
  }
  const stored = window.localStorage.getItem(LOCALE_STORAGE_KEY);
  return stored === "ru" || stored === "zh" || stored === "en" ? stored : "en";
}

function getInitialTheme(): ThemeMode {
  if (typeof window === "undefined") {
    return "light";
  }
  const stored = window.localStorage.getItem(THEME_STORAGE_KEY);
  return stored === "dark" || stored === "light" ? stored : "light";
}

function SectionHeading({
  eyebrow,
  title,
  subtitle,
  centered = false,
  actionLabel,
}: SectionHeadingProps) {
  return (
    <div className={centered ? "section-heading center" : "section-heading"}>
      <div>
        <p className="section-eyebrow">{eyebrow}</p>
        <h2>{title}</h2>
        {subtitle ? <p className="section-subtitle">{subtitle}</p> : null}
      </div>
      {actionLabel ? (
        <button className="ghost-button" type="button">
          {actionLabel}
        </button>
      ) : null}
    </div>
  );
}

function payloadText(
  section: PageSection | undefined,
  key: string,
  fallback = ""
): string {
  if (!section) {
    return fallback;
  }
  const value = section.payload[key];
  return typeof value === "string" ? value : fallback;
}

function payloadItems<T>(section: PageSection | undefined, key: string): T[] {
  if (!section) {
    return [];
  }
  const value = section.payload[key];
  return Array.isArray(value) ? (value as T[]) : [];
}

export default function App() {
  const [language, setLanguage] = useState<Locale>(getInitialLocale);
  const [theme, setTheme] = useState<ThemeMode>(getInitialTheme);
  const [cms, setCms] = useState<CmsBootstrap | null>(null);
  const [loadError, setLoadError] = useState<string>("");
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [contactForm, setContactForm] = useState<ContactMessagePayload>({
    name: "",
    email: "",
    message: "",
  });
  const [submitStatus, setSubmitStatus] = useState<SubmitStatus>("idle");
  const [submitMessage, setSubmitMessage] = useState<string>("");

  const fallbackUi = FALLBACK_UI[language];
  const ui = cms?.site.ui ?? fallbackUi;

  useEffect(() => {
    if (typeof document === "undefined") {
      return;
    }
    document.documentElement.lang = language;
    window.localStorage.setItem(LOCALE_STORAGE_KEY, language);
  }, [language]);

  useEffect(() => {
    if (typeof document === "undefined") {
      return;
    }
    document.documentElement.dataset.theme = theme;
    window.localStorage.setItem(THEME_STORAGE_KEY, theme);
  }, [theme]);

  useEffect(() => {
    const controller = new AbortController();
    setIsLoading(true);
    setLoadError("");

    async function fetchContent() {
      try {
        const bootstrap = await getCmsBootstrap(language, controller.signal);
        setCms(bootstrap);
      } catch (error) {
        if (error instanceof DOMException && error.name === "AbortError") {
          return;
        }
        setLoadError(
          error instanceof Error
            ? error.message
            : FALLBACK_UI[language].content_unavailable
        );
      } finally {
        setIsLoading(false);
      }
    }

    void fetchContent();

    return () => {
      controller.abort();
    };
  }, [language]);

  const handleContactSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setSubmitStatus("sending");
    setSubmitMessage("");

    try {
      await sendContactMessage(contactForm);
      setSubmitStatus("success");
      setSubmitMessage(ui.contact_success || fallbackUi.contact_success);
      setContactForm({ name: "", email: "", message: "" });
    } catch (error) {
      setSubmitStatus("error");
      setSubmitMessage(
        error instanceof Error
          ? error.message
          : ui.contact_error_default || fallbackUi.contact_error_default
      );
    }
  };

  const sectionsByKey = useMemo(() => {
    const map = new Map<string, PageSection>();
    for (const section of cms?.page.sections ?? []) {
      map.set(section.key, section);
    }
    return map;
  }, [cms]);

  const menusByCode = useMemo(() => {
    const map = new Map<string, CmsBootstrap["menus"][number]>();
    for (const menu of cms?.menus ?? []) {
      map.set(menu.code, menu);
    }
    return map;
  }, [cms]);

  const languageLabels: Record<Locale, string> = {
    en: ui.lang_en || "EN",
    ru: ui.lang_ru || "RU",
    zh: ui.lang_zh || "中文",
  };

  if (!cms) {
    return (
      <div className="page">
        <section className="journal-intro">
          <p>{isLoading ? ui.loading_content : ui.content_unavailable}</p>
          {loadError ? <small className="load-warning">{loadError}</small> : null}
        </section>
      </div>
    );
  }

  const settings = cms.site;
  const heroSection =
    sectionsByKey.get("hero") ??
    cms.page.sections.find((section) => section.section_type === "hero");
  const introSection = sectionsByKey.get("journal-intro");
  const expeditionSection = sectionsByKey.get("expeditions");
  const categoriesSection = sectionsByKey.get("categories");
  const storiesSection = sectionsByKey.get("stories");
  const contactSection = sectionsByKey.get("contact");

  const mainMenuItems = menusByCode.get("main")?.items ?? [];
  const footerMenuItems = menusByCode.get("footer")?.items ?? [];
  const socialMenuItems = menusByCode.get("social")?.items ?? [];

  const heroImage =
    heroSection?.images[0]?.image_url ||
    payloadText(heroSection, "background_image_url", settings.seo_image);
  const expeditionCards = payloadItems<ExpeditionCard>(expeditionSection, "cards");
  const categoryItems = payloadItems<GalleryItem>(categoriesSection, "items");
  const storyItems = payloadItems<StoryItem>(storiesSection, "items");
  const contactSocials = socialMenuItems.map((item) => item.label).join(" | ");

  return (
    <div className="page">
      <header className="site-header">
        <div className="brand">{settings.brand_name}</div>
        <nav className="nav">
          {mainMenuItems.map((item) => (
            <a
              key={item.id}
              href={item.href}
              target={item.open_in_new_tab ? "_blank" : undefined}
              rel={item.open_in_new_tab ? "noreferrer" : undefined}
            >
              {item.label}
            </a>
          ))}
        </nav>
        <div className="controls">
          <div className="lang-switch" role="group" aria-label="Language switch">
            {(["en", "ru", "zh"] as Locale[]).map((code) => (
              <button
                key={code}
                type="button"
                className={language === code ? "active" : ""}
                onClick={() => setLanguage(code)}
              >
                {languageLabels[code]}
              </button>
            ))}
          </div>
          <button
            className="theme-switch"
            type="button"
            onClick={() => setTheme(theme === "light" ? "dark" : "light")}
          >
            {theme === "light"
              ? ui.theme_dark || fallbackUi.theme_dark
              : ui.theme_light || fallbackUi.theme_light}
          </button>
        </div>
      </header>

      {heroSection ? (
        <section id="journey" className="hero">
          <div
            className="hero-media"
            style={{ backgroundImage: `url(${heroImage})` }}
          />
          <div className="hero-overlay" />
          <div className="hero-content">
            <p className="hero-kicker">{payloadText(heroSection, "kicker")}</p>
            <h1>{heroSection.title}</h1>
            <p className="hero-subtitle">{heroSection.subtitle}</p>
            <div className="hero-scroll">
              {isLoading
                ? ui.loading_content
                : payloadText(heroSection, "scroll_label", "Scroll to begin")}
            </div>
          </div>
        </section>
      ) : null}

      {introSection ? (
        <section className="journal-intro">
          <p>{introSection.body}</p>
          {loadError ? <small className="load-warning">{loadError}</small> : null}
        </section>
      ) : null}

      {expeditionSection ? (
        <section id="expeditions" className="section expeditions">
          <SectionHeading
            eyebrow={payloadText(expeditionSection, "eyebrow")}
            title={payloadText(expeditionSection, "title")}
            subtitle={payloadText(expeditionSection, "subtitle")}
            actionLabel={payloadText(expeditionSection, "action_label")}
          />
          <div className="expedition-grid">
            {expeditionCards.map((expedition, index) => (
              <article key={`${expedition.title}-${index}`} className="expedition-card">
                <div
                  className="expedition-image"
                  style={{
                    backgroundImage: expedition.image_url
                      ? `url(${expedition.image_url})`
                      : "none",
                  }}
                >
                  <span>{expedition.date_label || ""}</span>
                </div>
                <div className="expedition-copy">
                  <h3>{expedition.title || ""}</h3>
                  <p>{expedition.description || ""}</p>
                </div>
              </article>
            ))}
          </div>
        </section>
      ) : null}

      {categoriesSection ? (
        <section className="section categories">
          <SectionHeading
            eyebrow={payloadText(categoriesSection, "eyebrow")}
            title={payloadText(categoriesSection, "title")}
            subtitle={payloadText(categoriesSection, "subtitle")}
          />
          <div className="category-grid">
            {categoryItems.map((category, index) => (
              <div
                key={`${category.title}-${index}`}
                className={`category-card ${category.size || "small"}`}
                style={{
                  backgroundImage: category.image_url
                    ? `url(${category.image_url})`
                    : "none",
                }}
              >
                <div className="category-overlay">
                  <h3>{category.title || ""}</h3>
                </div>
              </div>
            ))}
          </div>
        </section>
      ) : null}

      {storiesSection ? (
        <section id="stories" className="section stories">
          <SectionHeading
            eyebrow={payloadText(storiesSection, "eyebrow")}
            title={payloadText(storiesSection, "title")}
            centered
          />
          <div className="story-list">
            {storyItems.map((story, index) => (
              <article
                key={`${story.title}-${index}`}
                className={`story-item ${index % 2 === 0 ? "" : "reverse"}`}
              >
                <div
                  className="story-image"
                  style={{
                    backgroundImage: story.image_url ? `url(${story.image_url})` : "none",
                  }}
                />
                <div className="story-copy">
                  <span>{story.date_label || ""}</span>
                  <h3>{story.title || ""}</h3>
                  <p>{story.description || ""}</p>
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
        <section id="contact" className="section contact">
          <div className="contact-inner">
            <div className="contact-copy">
              <h2>{contactSection.title}</h2>
              <p>{contactSection.body}</p>
              <div className="contact-details">
                <div>
                  <p className="detail-label">{ui.detail_location}</p>
                  <p>{payloadText(contactSection, "location", "-")}</p>
                </div>
                <div>
                  <p className="detail-label">{ui.detail_email}</p>
                  <p>{payloadText(contactSection, "email", settings.contact_email)}</p>
                </div>
                <div>
                  <p className="detail-label">{ui.detail_socials}</p>
                  <p>{contactSocials || "-"}</p>
                </div>
              </div>
            </div>
            <form className="contact-form" onSubmit={handleContactSubmit}>
              <label>
                {ui.contact_name_label}
                <input
                  type="text"
                  placeholder={ui.contact_name_placeholder}
                  value={contactForm.name}
                  onChange={(event) =>
                    setContactForm((prev) => ({ ...prev, name: event.target.value }))
                  }
                  required
                />
              </label>
              <label>
                {ui.contact_email_label}
                <input
                  type="email"
                  placeholder={ui.contact_email_placeholder}
                  value={contactForm.email}
                  onChange={(event) =>
                    setContactForm((prev) => ({ ...prev, email: event.target.value }))
                  }
                  required
                />
              </label>
              <label>
                {ui.contact_message_label}
                <textarea
                  placeholder={ui.contact_message_placeholder}
                  rows={4}
                  value={contactForm.message}
                  onChange={(event) =>
                    setContactForm((prev) => ({
                      ...prev,
                      message: event.target.value,
                    }))
                  }
                  required
                />
              </label>
              <button type="submit" disabled={submitStatus === "sending"}>
                {submitStatus === "sending" ? ui.contact_sending : ui.contact_submit}
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
          <h3>{settings.footer_title}</h3>
          <p>{settings.footer_description}</p>
        </div>
        <div className="footer-links">
          <div>
            <p className="detail-label">{settings.footer_explore_title}</p>
            {footerMenuItems.map((item) => (
              <p key={item.id}>
                <a
                  href={item.href}
                  target={item.open_in_new_tab ? "_blank" : undefined}
                  rel={item.open_in_new_tab ? "noreferrer" : undefined}
                >
                  {item.label}
                </a>
              </p>
            ))}
          </div>
          <div>
            <p className="detail-label">{settings.footer_social_title}</p>
            <div className="socials">
              {socialMenuItems.map((item) => (
                <a
                  key={item.id}
                  href={item.href || "#"}
                  title={item.label}
                  target={item.open_in_new_tab ? "_blank" : undefined}
                  rel={item.open_in_new_tab ? "noreferrer" : undefined}
                >
                  {item.label}
                </a>
              ))}
            </div>
          </div>
          <div>
            <p className="detail-label">{settings.footer_newsletter_title}</p>
            <p>{settings.newsletter_note}</p>
            <div className="newsletter">
              <input type="email" placeholder={ui.newsletter_placeholder} />
              <button type="button">{ui.newsletter_button}</button>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
