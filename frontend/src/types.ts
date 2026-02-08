export type Locale = "en" | "ru" | "zh";

export type UiTexts = {
  loading_content: string;
  content_unavailable: string;
  detail_location: string;
  detail_email: string;
  detail_socials: string;
  contact_name_label: string;
  contact_name_placeholder: string;
  contact_email_label: string;
  contact_email_placeholder: string;
  contact_message_label: string;
  contact_message_placeholder: string;
  contact_submit: string;
  contact_sending: string;
  contact_success: string;
  contact_error_default: string;
  newsletter_placeholder: string;
  newsletter_button: string;
  theme_light?: string;
  theme_dark?: string;
  lang_en?: string;
  lang_ru?: string;
  lang_zh?: string;
};

export type SiteSettings = {
  id: number;
  brand_name: string;
  contact_email: string;
  footer_title: string;
  footer_description: string;
  footer_explore_title: string;
  footer_social_title: string;
  footer_newsletter_title: string;
  newsletter_note: string;
  seo_title: string;
  seo_description: string;
  seo_image: string;
  ui: UiTexts;
  created_at: string;
  updated_at: string;
};

export type SectionImage = {
  id: number;
  image_url: string;
  alt_text: string;
  caption: string;
  order: number;
  is_published: boolean;
};

export type PageSection = {
  id: number;
  key: string;
  section_type:
    | "hero"
    | "rich_text"
    | "cards"
    | "gallery"
    | "stories"
    | "contact";
  title: string;
  subtitle: string;
  body: string;
  payload: Record<string, unknown>;
  order: number;
  is_published: boolean;
  images: SectionImage[];
};

export type Page = {
  id: number;
  title: string;
  slug: string;
  is_home: boolean;
  order: number;
  is_published: boolean;
  seo_title: string;
  seo_description: string;
  seo_image: string;
  sections: PageSection[];
  created_at: string;
  updated_at: string;
};

export type MenuItem = {
  id: number;
  label: string;
  href: string;
  page_slug: string | null;
  open_in_new_tab: boolean;
  order: number;
  is_published: boolean;
};

export type Menu = {
  id: number;
  code: string;
  title: string;
  location: "main" | "footer" | "social";
  items: MenuItem[];
};

export type CmsBootstrap = {
  lang: Locale;
  site: SiteSettings;
  page: Page;
  menus: Menu[];
};

export type ContactMessagePayload = {
  name: string;
  email: string;
  message: string;
};
