from copy import deepcopy

from django import forms
from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect
from django.templatetags.static import static
from django.urls import reverse
from django.utils import translation
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.generic import TemplateView, View

from api.models import ContactMessage

from .models import (
    Category,
    Expedition,
    HeroSection,
    Language,
    NavigationItem,
    Page,
    SiteSettings,
    SiteText,
    Story,
)


def _default_language_code() -> str:
    return (settings.LANGUAGE_CODE or "en").split("-")[0].lower()


def _active_language_code() -> str:
    code = translation.get_language() or _default_language_code()
    return str(code).split("-")[0].lower()


def _localize_text(default_value: str, translations: dict, lang_code: str, fallback_lang: str) -> str:
    if isinstance(translations, dict):
        translated = translations.get(lang_code)
        if isinstance(translated, str) and translated.strip():
            return translated

    if isinstance(default_value, str) and default_value.strip():
        return default_value

    if isinstance(translations, dict):
        fallback_value = translations.get(fallback_lang)
        if isinstance(fallback_value, str) and fallback_value.strip():
            return fallback_value
    return default_value if isinstance(default_value, str) else ""


def _localize_dict(default_payload: dict, translations: dict, lang_code: str, fallback_lang: str) -> dict:
    base = deepcopy(default_payload) if isinstance(default_payload, dict) else {}
    if not isinstance(translations, dict):
        return base

    fallback_payload = translations.get(fallback_lang)
    if isinstance(fallback_payload, dict):
        base.update(fallback_payload)

    if lang_code != fallback_lang:
        translated_payload = translations.get(lang_code)
        if isinstance(translated_payload, dict):
            base.update(translated_payload)
    return base


def _is_external(value: str) -> bool:
    lowered = str(value or "").lower()
    return lowered.startswith("http://") or lowered.startswith("https://") or lowered.startswith("mailto:")


def _site_text_map(lang_code: str, fallback_lang: str) -> dict[str, str]:
    values: dict[str, str] = {}
    queryset = SiteText.objects.filter(is_published=True).order_by("group", "order", "key")
    for site_text in queryset:
        values[site_text.key] = _localize_text(
            site_text.text,
            site_text.text_i18n,
            lang_code,
            fallback_lang,
        )
    return values


def _text(texts: dict[str, str], key: str, default: str = "") -> str:
    value = texts.get(key)
    if isinstance(value, str) and value.strip():
        return value
    return default


def _resolve_media_url(asset, fallback_static_path: str, legacy_url: str = "") -> str:
    if asset and asset.resolved_url:
        return asset.resolved_url
    if legacy_url and not _is_external(legacy_url):
        return legacy_url
    return static(fallback_static_path)


def _site_settings_payload(site_settings: SiteSettings, lang_code: str, fallback_lang: str) -> dict:
    return {
        "brand_name": _localize_text(
            site_settings.brand_name,
            site_settings.brand_name_i18n,
            lang_code,
            fallback_lang,
        ),
        "contact_email": site_settings.contact_email,
        "footer_title": _localize_text(
            site_settings.footer_title,
            site_settings.footer_title_i18n,
            lang_code,
            fallback_lang,
        ),
        "footer_description": _localize_text(
            site_settings.footer_description,
            site_settings.footer_description_i18n,
            lang_code,
            fallback_lang,
        ),
        "footer_explore_title": _localize_text(
            site_settings.footer_explore_title,
            site_settings.footer_explore_title_i18n,
            lang_code,
            fallback_lang,
        ),
        "footer_social_title": _localize_text(
            site_settings.footer_social_title,
            site_settings.footer_social_title_i18n,
            lang_code,
            fallback_lang,
        ),
        "footer_newsletter_title": _localize_text(
            site_settings.footer_newsletter_title,
            site_settings.footer_newsletter_title_i18n,
            lang_code,
            fallback_lang,
        ),
        "newsletter_note": _localize_text(
            site_settings.newsletter_note,
            site_settings.newsletter_note_i18n,
            lang_code,
            fallback_lang,
        ),
    }


def _navigation_label_key(item) -> str:
    token = (item.url_key or item.slug or f"item-{item.id}").replace("-", "_")
    if item.menu == "social":
        return f"social.{token}"
    if item.menu == "footer":
        return f"footer.nav.{token}"
    return f"nav.{token}"


def _navigation_href(item) -> str:
    if item.external_url:
        return item.external_url
    if item.page:
        if item.page.is_home:
            return reverse("content:home")
        return reverse("content:page", kwargs={"slug": item.page.slug})
    if item.url_key:
        return f"{reverse('content:home')}#{item.url_key}"

    href = str(item.href or "").strip()
    if href.startswith("/#"):
        return f"{reverse('content:home')}#{href.replace('/#', '', 1)}"
    if href.startswith("#"):
        return f"{reverse('content:home')}#{href.replace('#', '', 1)}"
    if href.startswith("/"):
        return href
    return href or "#"


def _navigation_payload(
    lang_code: str,
    fallback_lang: str,
    texts: dict[str, str],
) -> dict[str, list[dict]]:
    payload: dict[str, list[dict]] = {"main": [], "footer": [], "social": []}
    queryset = (
        NavigationItem.objects.filter(is_published=True)
        .select_related("page")
        .order_by("menu", "order", "id")
    )
    for item in queryset:
        label_default = _localize_text(item.title, item.title_i18n, lang_code, fallback_lang)
        label = _text(texts, _navigation_label_key(item), label_default)
        payload.setdefault(item.menu, []).append(
            {
                "id": item.id,
                "label": label,
                "href": _navigation_href(item),
                "open_in_new_tab": item.open_in_new_tab,
                "is_external": _is_external(item.external_url or item.href),
            }
        )
    return payload


def _localized_sections(page: Page, lang_code: str, fallback_lang: str) -> dict[str, dict]:
    sections: dict[str, dict] = {}
    for section in page.sections.filter(is_published=True).prefetch_related("images").order_by("order", "id"):
        payload = _localize_dict(section.payload, section.payload_i18n, lang_code, fallback_lang)
        sections[section.key] = {
            "id": section.id,
            "key": section.key,
            "title": _localize_text(section.title, section.title_i18n, lang_code, fallback_lang),
            "subtitle": _localize_text(section.subtitle, section.subtitle_i18n, lang_code, fallback_lang),
            "body": _localize_text(section.body, section.body_i18n, lang_code, fallback_lang),
            "payload": payload,
            "anchor": payload.get("anchor") or ("journey" if section.key == "hero" else section.key),
            "images": [image for image in section.images.all() if image.is_published],
        }
    return sections


def _hero_payload(
    page: Page,
    sections: dict[str, dict],
    texts: dict[str, str],
    site_brand_name: str,
) -> dict:
    hero_model = HeroSection.objects.filter(is_published=True, page=page).select_related("media").first()
    if hero_model is not None:
        return {
            "anchor": hero_model.key or "journey",
            "kicker": _text(texts, "section.hero.kicker", hero_model.kicker),
            "title": _text(texts, "section.hero.title", hero_model.title),
            "subtitle": _text(texts, "section.hero.subtitle", hero_model.subtitle),
            "cta_label": _text(texts, "section.hero.cta_label", hero_model.cta_label),
            "cta_url": hero_model.cta_url or "#expeditions",
            "scroll_label": _text(texts, "section.hero.scroll_label", hero_model.scroll_label),
            "image_url": _resolve_media_url(hero_model.media, "content/images/hero-default.svg"),
        }

    section = sections.get("hero")
    if section:
        section_images = section.get("images") or []
        first_image = section_images[0].image_url if section_images else ""
        return {
            "anchor": section.get("anchor") or "journey",
            "kicker": _text(texts, "section.hero.kicker", section["payload"].get("kicker", "")),
            "title": _text(texts, "section.hero.title", section.get("title", site_brand_name)),
            "subtitle": _text(texts, "section.hero.subtitle", section.get("subtitle", "")),
            "cta_label": _text(texts, "section.hero.cta_label", section["payload"].get("cta_label", "")),
            "cta_url": section["payload"].get("cta_url") or "#expeditions",
            "scroll_label": _text(
                texts,
                "section.hero.scroll_label",
                section["payload"].get("scroll_label", ""),
            ),
            "image_url": _resolve_media_url(None, "content/images/hero-default.svg", first_image),
        }

    return {
        "anchor": "journey",
        "kicker": _text(texts, "section.hero.kicker", ""),
        "title": _text(texts, "section.hero.title", site_brand_name),
        "subtitle": _text(texts, "section.hero.subtitle", ""),
        "cta_label": _text(texts, "section.hero.cta_label", ""),
        "cta_url": "#expeditions",
        "scroll_label": _text(texts, "section.hero.scroll_label", ""),
        "image_url": static("content/images/hero-default.svg"),
    }


def _language_switches(page: Page, lang_code: str, texts: dict[str, str]) -> list[dict]:
    default_code = _default_language_code()
    queryset = Language.objects.filter(is_active=True).order_by("order", "id")
    if not queryset.exists():
        fallback = []
        for index, (code, label) in enumerate(getattr(settings, "LANGUAGES", (("en", "English"),)), start=1):
            normalized = str(code).split("-")[0].lower()
            fallback.append(
                {
                    "code": normalized,
                    "label": _text(texts, f"lang.{normalized}", str(label)),
                    "url": reverse("content:home") if page.is_home else reverse("content:page", kwargs={"slug": page.slug}),
                    "is_active": normalized == lang_code,
                    "order": index if normalized != default_code else 0,
                }
            )
        return fallback

    switches = []
    for language in queryset:
        with translation.override(language.code):
            if page.is_home:
                url = reverse("content:home")
            else:
                url = reverse("content:page", kwargs={"slug": page.slug})
        switches.append(
            {
                "code": language.code,
                "label": _text(texts, f"lang.{language.code}", language.name),
                "url": url,
                "is_active": language.code == lang_code,
                "order": language.order,
            }
        )
    return switches


class ContactMessageForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ("name", "email", "message")


class BaseContentPageView(TemplateView):
    template_name = "content/page.html"

    def _resolve_page(self):
        slug = self.kwargs.get("slug")
        queryset = (
            Page.objects.filter(is_active=True, is_published=True)
            .prefetch_related("sections__images")
            .order_by("order", "id")
        )
        if slug:
            if slug == "home":
                return queryset.filter(is_home=True).first() or queryset.first()
            page = queryset.filter(slug=slug).first()
            if page:
                return page
        return queryset.filter(is_home=True).first() or queryset.first()

    def _base_context(self):
        page = self._resolve_page()
        if page is None:
            return {
                "page_obj": None,
                "site": {},
                "ui": {},
                "main_menu": [],
                "footer_menu": [],
                "social_menu": [],
                "language_switches": [],
                "journal_intro_section": {},
                "expeditions_section": {},
                "categories_section": {},
                "stories_section": {},
                "contact_section": {},
                "hero": {},
                "expeditions": [],
                "categories": [],
                "stories": [],
                "form": ContactMessageForm(),
            }

        lang_code = _active_language_code()
        fallback_lang = _default_language_code()

        site_settings = SiteSettings.objects.order_by("-updated_at").first()
        if site_settings is None:
            site_settings = SiteSettings.objects.create(brand_name="Romanweiẞ", footer_title="Romanweiẞ")

        texts = _site_text_map(lang_code, fallback_lang)
        site_payload = _site_settings_payload(site_settings, lang_code, fallback_lang)
        sections = _localized_sections(page, lang_code, fallback_lang)

        expeditions = []
        for expedition in Expedition.objects.filter(is_published=True).select_related("cover").order_by("order", "id"):
            key_prefix = f"expedition.{expedition.slug}"
            title = _text(texts, f"{key_prefix}.title", expedition.title)
            subtitle_default = expedition.subtitle or expedition.description
            expeditions.append(
                {
                    "title": title,
                    "subtitle": _text(texts, f"{key_prefix}.subtitle", subtitle_default),
                    "date_label": _text(texts, f"{key_prefix}.date_label", expedition.date_label),
                    "slug": expedition.slug,
                    "cover_url": _resolve_media_url(
                        expedition.cover,
                        "content/images/expedition-default.svg",
                        expedition.image_url,
                    ),
                }
            )

        categories = []
        for category in Category.objects.filter(is_published=True).select_related("cover").order_by("order", "id"):
            key_prefix = f"category.{category.slug}"
            categories.append(
                {
                    "title": _text(texts, f"{key_prefix}.title", category.title),
                    "slug": category.slug,
                    "size": category.size,
                    "cover_url": _resolve_media_url(
                        category.cover,
                        "content/images/category-default.svg",
                        category.image_url,
                    ),
                }
            )

        stories = []
        for story in Story.objects.filter(is_published=True).select_related("cover").order_by("order", "id"):
            key_prefix = f"story.{story.slug}"
            default_title = _localize_text(story.title, story.title_i18n, lang_code, fallback_lang)
            default_date = _localize_text(story.date_label, story.date_label_i18n, lang_code, fallback_lang)
            default_description = _localize_text(
                story.description,
                story.description_i18n,
                lang_code,
                fallback_lang,
            )
            stories.append(
                {
                    "title": _text(texts, f"{key_prefix}.title", default_title),
                    "date_label": _text(texts, f"{key_prefix}.date_label", default_date),
                    "description": _text(texts, f"{key_prefix}.description", default_description),
                    "slug": story.slug,
                    "cover_url": _resolve_media_url(
                        story.cover,
                        "content/images/story-default.svg",
                        story.image_url,
                    ),
                }
            )

        nav_payload = _navigation_payload(lang_code, fallback_lang, texts)
        hero = _hero_payload(page, sections, texts, site_payload["brand_name"])
        language_switches = _language_switches(page, lang_code, texts)

        ui = {
            "detail_location": _text(texts, "detail.location", "Location"),
            "detail_email": _text(texts, "detail.email", "Email"),
            "detail_socials": _text(texts, "detail.socials", "Socials"),
            "form_name_label": _text(texts, "form.name.label", "Name"),
            "form_name_placeholder": _text(texts, "form.name.placeholder", "Your name"),
            "form_email_label": _text(texts, "form.email.label", "Email"),
            "form_email_placeholder": _text(texts, "form.email.placeholder", "your@email.com"),
            "form_message_label": _text(texts, "form.message.label", "Message"),
            "form_message_placeholder": _text(texts, "form.message.placeholder", "Tell me about your project..."),
            "form_submit": _text(texts, "form.submit", "Send message"),
            "newsletter_placeholder": _text(texts, "newsletter.placeholder", "Email address"),
            "newsletter_button": _text(texts, "newsletter.button", "Join"),
        }

        context = {
            "page_obj": page,
            "site": site_payload,
            "ui": ui,
            "hero": hero,
            "main_menu": nav_payload.get("main", []),
            "footer_menu": nav_payload.get("footer", []),
            "social_menu": nav_payload.get("social", []),
            "language_switches": language_switches,
            "journal_intro_section": sections.get("journal-intro", {}),
            "expeditions_section": sections.get("expeditions", {}),
            "categories_section": sections.get("categories", {}),
            "stories_section": sections.get("stories", {}),
            "contact_section": sections.get("contact", {}),
            "expeditions": expeditions,
            "categories": categories,
            "stories": stories,
            "form": ContactMessageForm(),
            "page_title": site_payload["brand_name"],
        }
        return context

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self._base_context())
        return context


class HomePageView(BaseContentPageView):
    pass


class ContentPageView(BaseContentPageView):
    pass


class ContactSubmitView(View):
    def post(self, request, *args, **kwargs):
        lang_code = _active_language_code()
        fallback_lang = _default_language_code()
        texts = _site_text_map(lang_code, fallback_lang)

        form = ContactMessageForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, _text(texts, "form.success", "Message sent. Thank you."))
        else:
            messages.error(request, _text(texts, "form.error", "Could not send message."))

        next_url = str(request.POST.get("next", "")).strip()
        if not next_url:
            next_url = reverse("content:home")
        if not url_has_allowed_host_and_scheme(
            next_url,
            allowed_hosts={request.get_host()},
            require_https=request.is_secure(),
        ):
            next_url = reverse("content:home")
        return redirect(next_url)
