import { FormEvent, useEffect, useMemo, useState } from "react";
import { getCmsBootstrap, sendContactMessage } from "./api";
import "./index.css";
import type { CmsBootstrap, ContactMessagePayload, PageSection } from "./types";

type SubmitStatus = "idle" | "sending" | "success" | "error";

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

  useEffect(() => {
    const controller = new AbortController();

    async function fetchContent() {
      try {
        const bootstrap = await getCmsBootstrap(controller.signal);
        setCms(bootstrap);
        setLoadError("");
      } catch (error) {
        if (error instanceof DOMException && error.name === "AbortError") {
          return;
        }
        setLoadError("Could not load content from Django API.");
      } finally {
        setIsLoading(false);
      }
    }

    void fetchContent();

    return () => {
      controller.abort();
    };
  }, []);

  const handleContactSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setSubmitStatus("sending");
    setSubmitMessage("");

    try {
      await sendContactMessage(contactForm);
      setSubmitStatus("success");
      setSubmitMessage("Message sent. Thank you.");
      setContactForm({ name: "", email: "", message: "" });
    } catch (error) {
      setSubmitStatus("error");
      setSubmitMessage(
        error instanceof Error ? error.message : "Could not send message."
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

  if (!cms) {
    return (
      <div className="page">
        <section className="journal-intro">
          <p>{isLoading ? "Loading content..." : "Content is unavailable."}</p>
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
                ? "Loading..."
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
                  <p className="detail-label">Location</p>
                  <p>{payloadText(contactSection, "location", "-")}</p>
                </div>
                <div>
                  <p className="detail-label">Email</p>
                  <p>{payloadText(contactSection, "email", settings.contact_email)}</p>
                </div>
                <div>
                  <p className="detail-label">Socials</p>
                  <p>{contactSocials || "-"}</p>
                </div>
              </div>
            </div>
            <form className="contact-form" onSubmit={handleContactSubmit}>
              <label>
                Name
                <input
                  type="text"
                  placeholder="Your name"
                  value={contactForm.name}
                  onChange={(event) =>
                    setContactForm((prev) => ({ ...prev, name: event.target.value }))
                  }
                  required
                />
              </label>
              <label>
                Email
                <input
                  type="email"
                  placeholder="your@email.com"
                  value={contactForm.email}
                  onChange={(event) =>
                    setContactForm((prev) => ({ ...prev, email: event.target.value }))
                  }
                  required
                />
              </label>
              <label>
                Message
                <textarea
                  placeholder="Tell me about your project..."
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
                {submitStatus === "sending" ? "Sending..." : "Send message"}
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
              <input type="email" placeholder="Email address" />
              <button type="button">Join</button>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
