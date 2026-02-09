export type Locale = string;

export type I18nDictionary = Record<string, string>;

export type LanguageOption = {
  code: Locale;
  name: string;
  is_default: boolean;
  order: number;
};

export type ContactMessagePayload = {
  name: string;
  email: string;
  message: string;
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
  anchor: string;
  section_type: "hero" | "rich_text" | "cards" | "gallery" | "stories" | "contact";
  title: string;
  subtitle: string;
  body: string;
  payload: Record<string, unknown>;
  order: number;
  is_published: boolean;
  images: SectionImage[];
};

export type PageData = {
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

export type ContentResponse = {
  lang: Locale;
  default_lang: Locale;
  languages: LanguageOption[];
  site: {
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
    ui: Record<string, string>;
    created_at: string;
    updated_at: string;
  };
  texts: I18nDictionary;
  pages: Array<{
    slug: string;
    title: string;
    is_home: boolean;
    order: number;
  }>;
};

export type NavigationItem = {
  id: number;
  menu: string;
  section: string;
  slug: string;
  url_key: string;
  label: string;
  label_key: string;
  kind: "page" | "anchor" | "external";
  href: string;
  page_slug: string | null;
  open_in_new_tab: boolean;
  order: number;
  is_published: boolean;
};

export type NavigationResponse = {
  lang: Locale;
  menus: Record<string, NavigationItem[]>;
};

export type PageResponse = {
  lang: Locale;
  page: PageData;
};
