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

export type StructureMenuItem = {
  id: number;
  href: string;
  label: string;
  label_key: string;
  open_in_new_tab: boolean;
};

export type StructureSection = {
  id: number;
  key: string;
  anchor: string;
  section_type: "hero" | "rich_text" | "cards" | "gallery" | "stories" | "contact";
  title: string;
  title_key: string;
  subtitle: string;
  subtitle_key: string;
  body: string;
  body_key: string;
  payload: Record<string, unknown>;
  payload_keys: Record<string, string>;
  images: SectionImage[];
};

export type SiteStructureResponse = {
  lang: Locale;
  languages: LanguageOption[];
  site: {
    brand_name: string;
    brand_key: string;
    footer_title: string;
    footer_title_key: string;
    footer_description: string;
    footer_description_key: string;
    footer_explore_title: string;
    footer_explore_title_key: string;
    footer_social_title: string;
    footer_social_title_key: string;
    footer_newsletter_title: string;
    footer_newsletter_title_key: string;
    newsletter_note: string;
    newsletter_note_key: string;
    contact_email: string;
  };
  pages: Array<{
    slug: string;
    is_active: boolean;
    order: number;
  }>;
  menus: Record<string, StructureMenuItem[]>;
  sections: StructureSection[];
};
