from copy import deepcopy

from rest_framework import serializers

from .models import (
    Category,
    Expedition,
    Menu,
    MenuItem,
    NavigationItem,
    Page,
    PageSection,
    SectionImage,
    SiteSettings,
    SiteText,
    SocialLink,
    Story,
)


def _request_lang(serializer: serializers.Serializer) -> str:
    explicit_lang = serializer.context.get("lang_code")
    if isinstance(explicit_lang, str) and explicit_lang.strip():
        return explicit_lang.strip().lower()
    request = serializer.context.get("request")
    raw = ""
    if request is not None:
        raw = str(request.query_params.get("lang", "")).strip().lower()
    return raw or "en"


def _fallback_lang(serializer: serializers.Serializer) -> str:
    fallback = serializer.context.get("fallback_lang")
    if isinstance(fallback, str) and fallback.strip():
        return fallback.strip().lower()
    return "en"


def _localized_text(
    default_value: str,
    translations: dict,
    lang: str,
    fallback_lang: str = "en",
) -> str:
    base = default_value if isinstance(default_value, str) else ""

    if isinstance(translations, dict):
        translated = translations.get(lang)
        if isinstance(translated, str) and translated.strip():
            return translated

    if base.strip():
        return base

    if isinstance(translations, dict):
        fallback_value = translations.get(fallback_lang)
        if isinstance(fallback_value, str) and fallback_value.strip():
            return fallback_value

    return base


def _localized_dict(default_value: dict, translations: dict, lang: str, fallback_lang: str) -> dict:
    base = deepcopy(default_value) if isinstance(default_value, dict) else {}
    if not isinstance(translations, dict):
        return base

    fallback_payload = translations.get(fallback_lang)
    if isinstance(fallback_payload, dict):
        base = {**fallback_payload, **base}

    if lang != fallback_lang:
        translated = translations.get(lang)
        if isinstance(translated, dict):
            base.update(translated)
    return base


def _menu_item_href_from_parts(href: str, page, url_key: str, external_url: str) -> str:
    if external_url:
        return external_url
    if page:
        return "/" if page.is_home else f"/{page.slug}/"
    if url_key:
        return f"/#{url_key}"
    if href:
        return href
    return "#"


def _menu_item_kind(href: str, page, url_key: str, external_url: str) -> str:
    if external_url:
        return "external"
    if page:
        return "page"
    if url_key:
        return "anchor"
    if href.startswith("#"):
        return "anchor"
    if href.startswith("/"):
        return "page"
    return "external"


def _menu_item_label_key(menu_code: str, url_key: str, slug: str) -> str:
    token = (url_key or slug or "item").replace("-", "_")
    if menu_code == "social":
        return f"social.{token}"
    if menu_code == "footer":
        return f"footer.nav.{token}"
    return f"nav.{token}"


class SiteTextSerializer(serializers.ModelSerializer):
    value = serializers.SerializerMethodField()

    class Meta:
        model = SiteText
        fields = ("key", "group", "value")

    def get_value(self, obj):
        lang = _request_lang(self)
        fallback = _fallback_lang(self)
        return _localized_text(obj.text, obj.text_i18n, lang, fallback)


class SiteSettingsSerializer(serializers.ModelSerializer):
    brand_name = serializers.SerializerMethodField()
    footer_title = serializers.SerializerMethodField()
    footer_description = serializers.SerializerMethodField()
    footer_explore_title = serializers.SerializerMethodField()
    footer_social_title = serializers.SerializerMethodField()
    footer_newsletter_title = serializers.SerializerMethodField()
    newsletter_note = serializers.SerializerMethodField()
    ui = serializers.SerializerMethodField()

    class Meta:
        model = SiteSettings
        fields = (
            "id",
            "brand_name",
            "contact_email",
            "footer_title",
            "footer_description",
            "footer_explore_title",
            "footer_social_title",
            "footer_newsletter_title",
            "newsletter_note",
            "seo_title",
            "seo_description",
            "seo_image",
            "ui",
            "created_at",
            "updated_at",
        )

    def get_brand_name(self, obj):
        return _localized_text(
            obj.brand_name,
            obj.brand_name_i18n,
            _request_lang(self),
            _fallback_lang(self),
        )

    def get_footer_title(self, obj):
        return _localized_text(
            obj.footer_title,
            obj.footer_title_i18n,
            _request_lang(self),
            _fallback_lang(self),
        )

    def get_footer_description(self, obj):
        return _localized_text(
            obj.footer_description,
            obj.footer_description_i18n,
            _request_lang(self),
            _fallback_lang(self),
        )

    def get_footer_explore_title(self, obj):
        return _localized_text(
            obj.footer_explore_title,
            obj.footer_explore_title_i18n,
            _request_lang(self),
            _fallback_lang(self),
        )

    def get_footer_social_title(self, obj):
        return _localized_text(
            obj.footer_social_title,
            obj.footer_social_title_i18n,
            _request_lang(self),
            _fallback_lang(self),
        )

    def get_footer_newsletter_title(self, obj):
        return _localized_text(
            obj.footer_newsletter_title,
            obj.footer_newsletter_title_i18n,
            _request_lang(self),
            _fallback_lang(self),
        )

    def get_newsletter_note(self, obj):
        return _localized_text(
            obj.newsletter_note,
            obj.newsletter_note_i18n,
            _request_lang(self),
            _fallback_lang(self),
        )

    def get_ui(self, obj):
        lang = _request_lang(self)
        fallback = _fallback_lang(self)
        ui_map = obj.ui_i18n if isinstance(obj.ui_i18n, dict) else {}
        base = {}
        fallback_ui = ui_map.get(fallback)
        if isinstance(fallback_ui, dict):
            base.update(fallback_ui)
        if lang != fallback:
            current_ui = ui_map.get(lang)
            if isinstance(current_ui, dict):
                base.update(current_ui)
        return base


class SectionImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = SectionImage
        fields = (
            "id",
            "image_url",
            "alt_text",
            "caption",
            "order",
            "is_published",
        )


class PageSectionSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    subtitle = serializers.SerializerMethodField()
    body = serializers.SerializerMethodField()
    payload = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()
    anchor = serializers.SerializerMethodField()

    class Meta:
        model = PageSection
        fields = (
            "id",
            "key",
            "anchor",
            "section_type",
            "title",
            "subtitle",
            "body",
            "payload",
            "order",
            "is_published",
            "images",
        )

    def get_images(self, obj):
        images = [image for image in obj.images.all() if image.is_published]
        images.sort(key=lambda image: (image.order, image.id))
        return SectionImageSerializer(images, many=True).data

    def get_title(self, obj):
        return _localized_text(
            obj.title,
            obj.title_i18n,
            _request_lang(self),
            _fallback_lang(self),
        )

    def get_subtitle(self, obj):
        return _localized_text(
            obj.subtitle,
            obj.subtitle_i18n,
            _request_lang(self),
            _fallback_lang(self),
        )

    def get_body(self, obj):
        return _localized_text(
            obj.body,
            obj.body_i18n,
            _request_lang(self),
            _fallback_lang(self),
        )

    def get_payload(self, obj):
        return _localized_dict(
            obj.payload,
            obj.payload_i18n,
            _request_lang(self),
            _fallback_lang(self),
        )

    def get_anchor(self, obj):
        payload = self.get_payload(obj)
        if isinstance(payload, dict):
            payload_anchor = payload.get("anchor")
            if isinstance(payload_anchor, str) and payload_anchor.strip():
                return payload_anchor.strip()
        if obj.key == "hero":
            return "journey"
        return obj.key


class PageSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    seo_title = serializers.SerializerMethodField()
    seo_description = serializers.SerializerMethodField()
    sections = serializers.SerializerMethodField()

    class Meta:
        model = Page
        fields = (
            "id",
            "title",
            "slug",
            "is_home",
            "order",
            "is_published",
            "seo_title",
            "seo_description",
            "seo_image",
            "sections",
            "created_at",
            "updated_at",
        )

    def get_sections(self, obj):
        sections = [section for section in obj.sections.all() if section.is_published]
        sections.sort(key=lambda section: (section.order, section.id))
        return PageSectionSerializer(sections, many=True, context=self.context).data

    def get_title(self, obj):
        return _localized_text(
            obj.title,
            obj.title_i18n,
            _request_lang(self),
            _fallback_lang(self),
        )

    def get_seo_title(self, obj):
        return _localized_text(
            obj.seo_title,
            obj.seo_title_i18n,
            _request_lang(self),
            _fallback_lang(self),
        )

    def get_seo_description(self, obj):
        return _localized_text(
            obj.seo_description,
            obj.seo_description_i18n,
            _request_lang(self),
            _fallback_lang(self),
        )


class MenuItemSerializer(serializers.ModelSerializer):
    label = serializers.SerializerMethodField()
    href = serializers.SerializerMethodField()
    page_slug = serializers.CharField(source="page.slug", read_only=True)

    class Meta:
        model = MenuItem
        fields = (
            "id",
            "label",
            "href",
            "page_slug",
            "open_in_new_tab",
            "order",
            "is_published",
        )

    def get_href(self, obj):
        return _menu_item_href_from_parts(obj.href, obj.page, "", "")

    def get_label(self, obj):
        return _localized_text(
            obj.label,
            obj.label_i18n,
            _request_lang(self),
            _fallback_lang(self),
        )


class MenuSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    items = serializers.SerializerMethodField()

    class Meta:
        model = Menu
        fields = ("id", "code", "title", "location", "items")

    def get_items(self, obj):
        items = [item for item in obj.items.all() if item.is_published]
        items.sort(key=lambda item: (item.order, item.id))
        return MenuItemSerializer(items, many=True, context=self.context).data

    def get_title(self, obj):
        return _localized_text(
            obj.title,
            obj.title_i18n,
            _request_lang(self),
            _fallback_lang(self),
        )


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


class ExpeditionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expedition
        fields = "__all__"


class StorySerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    date_label = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()

    class Meta:
        model = Story
        fields = (
            "id",
            "title",
            "slug",
            "date_label",
            "description",
            "image_url",
            "order",
            "is_published",
            "created_at",
            "updated_at",
        )

    def get_title(self, obj):
        return _localized_text(
            obj.title,
            obj.title_i18n,
            _request_lang(self),
            _fallback_lang(self),
        )

    def get_date_label(self, obj):
        return _localized_text(
            obj.date_label,
            obj.date_label_i18n,
            _request_lang(self),
            _fallback_lang(self),
        )

    def get_description(self, obj):
        return _localized_text(
            obj.description,
            obj.description_i18n,
            _request_lang(self),
            _fallback_lang(self),
        )


class NavigationItemSerializer(serializers.ModelSerializer):
    label = serializers.SerializerMethodField()
    label_key = serializers.SerializerMethodField()
    href = serializers.SerializerMethodField()
    kind = serializers.SerializerMethodField()
    page_slug = serializers.CharField(source="page.slug", read_only=True)

    class Meta:
        model = NavigationItem
        fields = (
            "id",
            "menu",
            "section",
            "slug",
            "url_key",
            "label",
            "label_key",
            "kind",
            "href",
            "page_slug",
            "open_in_new_tab",
            "order",
            "is_published",
        )

    def get_label(self, obj):
        return _localized_text(
            obj.title,
            obj.title_i18n,
            _request_lang(self),
            _fallback_lang(self),
        )

    def get_label_key(self, obj):
        return _menu_item_label_key(obj.menu, obj.url_key, obj.slug)

    def get_href(self, obj):
        return _menu_item_href_from_parts(obj.href, obj.page, obj.url_key, obj.external_url)

    def get_kind(self, obj):
        return _menu_item_kind(obj.href, obj.page, obj.url_key, obj.external_url)


class SocialLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialLink
        fields = "__all__"
