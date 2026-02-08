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
    SocialLink,
    Story,
)

SUPPORTED_LANGS = {"en", "ru", "zh"}

DEFAULT_UI_TEXTS = {
    "en": {
        "loading_content": "Loading content...",
        "content_unavailable": "Content is unavailable.",
        "detail_location": "Location",
        "detail_email": "Email",
        "detail_socials": "Socials",
        "contact_name_label": "Name",
        "contact_name_placeholder": "Your name",
        "contact_email_label": "Email",
        "contact_email_placeholder": "your@email.com",
        "contact_message_label": "Message",
        "contact_message_placeholder": "Tell me about your project...",
        "contact_submit": "Send message",
        "contact_sending": "Sending...",
        "contact_success": "Message sent. Thank you.",
        "contact_error_default": "Could not send message.",
        "newsletter_placeholder": "Email address",
        "newsletter_button": "Join",
        "theme_light": "Light",
        "theme_dark": "Dark",
        "lang_en": "EN",
        "lang_ru": "RU",
        "lang_zh": "中文",
    },
    "ru": {
        "loading_content": "Загрузка контента...",
        "content_unavailable": "Контент недоступен.",
        "detail_location": "Локация",
        "detail_email": "Email",
        "detail_socials": "Соцсети",
        "contact_name_label": "Имя",
        "contact_name_placeholder": "Ваше имя",
        "contact_email_label": "Email",
        "contact_email_placeholder": "your@email.com",
        "contact_message_label": "Сообщение",
        "contact_message_placeholder": "Расскажите о вашем проекте...",
        "contact_submit": "Отправить",
        "contact_sending": "Отправка...",
        "contact_success": "Сообщение отправлено. Спасибо.",
        "contact_error_default": "Не удалось отправить сообщение.",
        "newsletter_placeholder": "Email адрес",
        "newsletter_button": "Подписаться",
        "theme_light": "Светлая",
        "theme_dark": "Тёмная",
        "lang_en": "EN",
        "lang_ru": "RU",
        "lang_zh": "中文",
    },
    "zh": {
        "loading_content": "正在加载内容...",
        "content_unavailable": "内容不可用。",
        "detail_location": "地点",
        "detail_email": "邮箱",
        "detail_socials": "社交",
        "contact_name_label": "姓名",
        "contact_name_placeholder": "你的姓名",
        "contact_email_label": "邮箱",
        "contact_email_placeholder": "your@email.com",
        "contact_message_label": "留言",
        "contact_message_placeholder": "请介绍一下你的项目...",
        "contact_submit": "发送消息",
        "contact_sending": "发送中...",
        "contact_success": "消息已发送。谢谢。",
        "contact_error_default": "发送失败。",
        "newsletter_placeholder": "邮箱地址",
        "newsletter_button": "订阅",
        "theme_light": "浅色",
        "theme_dark": "深色",
        "lang_en": "EN",
        "lang_ru": "RU",
        "lang_zh": "中文",
    },
}


def _request_lang(serializer: serializers.Serializer) -> str:
    request = serializer.context.get("request")
    raw = ""
    if request is not None:
        raw = str(request.query_params.get("lang", "")).strip().lower()
    return raw if raw in SUPPORTED_LANGS else "en"


def _localized_text(default_value: str, translations: dict, lang: str) -> str:
    if lang == "en":
        return default_value
    if isinstance(translations, dict):
        translated = translations.get(lang)
        if isinstance(translated, str) and translated.strip():
            return translated
    return default_value


def _localized_dict(default_value: dict, translations: dict, lang: str) -> dict:
    base = deepcopy(default_value) if isinstance(default_value, dict) else {}
    if lang == "en":
        return base
    if isinstance(translations, dict):
        translated = translations.get(lang)
        if isinstance(translated, dict):
            base.update(translated)
    return base


def _localized_ui_texts(translations: dict, lang: str) -> dict:
    texts = deepcopy(DEFAULT_UI_TEXTS["en"])
    if isinstance(translations, dict):
        english_override = translations.get("en")
        if isinstance(english_override, dict):
            texts.update(english_override)
    if lang != "en":
        texts.update(deepcopy(DEFAULT_UI_TEXTS.get(lang, {})))
        if isinstance(translations, dict):
            lang_override = translations.get(lang)
            if isinstance(lang_override, dict):
                texts.update(lang_override)
    return texts


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
        return _localized_text(obj.brand_name, obj.brand_name_i18n, _request_lang(self))

    def get_footer_title(self, obj):
        return _localized_text(obj.footer_title, obj.footer_title_i18n, _request_lang(self))

    def get_footer_description(self, obj):
        return _localized_text(
            obj.footer_description, obj.footer_description_i18n, _request_lang(self)
        )

    def get_footer_explore_title(self, obj):
        return _localized_text(
            obj.footer_explore_title, obj.footer_explore_title_i18n, _request_lang(self)
        )

    def get_footer_social_title(self, obj):
        return _localized_text(
            obj.footer_social_title, obj.footer_social_title_i18n, _request_lang(self)
        )

    def get_footer_newsletter_title(self, obj):
        return _localized_text(
            obj.footer_newsletter_title,
            obj.footer_newsletter_title_i18n,
            _request_lang(self),
        )

    def get_newsletter_note(self, obj):
        return _localized_text(
            obj.newsletter_note,
            obj.newsletter_note_i18n,
            _request_lang(self),
        )

    def get_ui(self, obj):
        return _localized_ui_texts(obj.ui_i18n, _request_lang(self))


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

    class Meta:
        model = PageSection
        fields = (
            "id",
            "key",
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
        return _localized_text(obj.title, obj.title_i18n, _request_lang(self))

    def get_subtitle(self, obj):
        return _localized_text(obj.subtitle, obj.subtitle_i18n, _request_lang(self))

    def get_body(self, obj):
        return _localized_text(obj.body, obj.body_i18n, _request_lang(self))

    def get_payload(self, obj):
        return _localized_dict(obj.payload, obj.payload_i18n, _request_lang(self))


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
        return PageSectionSerializer(sections, many=True).data

    def get_title(self, obj):
        return _localized_text(obj.title, obj.title_i18n, _request_lang(self))

    def get_seo_title(self, obj):
        return _localized_text(obj.seo_title, obj.seo_title_i18n, _request_lang(self))

    def get_seo_description(self, obj):
        return _localized_text(
            obj.seo_description, obj.seo_description_i18n, _request_lang(self)
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
        if obj.href:
            return obj.href
        if obj.page:
            return "/" if obj.page.is_home else f"/{obj.page.slug}/"
        return "#"

    def get_label(self, obj):
        return _localized_text(obj.label, obj.label_i18n, _request_lang(self))


class MenuSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    items = serializers.SerializerMethodField()

    class Meta:
        model = Menu
        fields = ("id", "code", "title", "location", "items")

    def get_items(self, obj):
        items = [item for item in obj.items.all() if item.is_published]
        items.sort(key=lambda item: (item.order, item.id))
        return MenuItemSerializer(items, many=True).data

    def get_title(self, obj):
        return _localized_text(obj.title, obj.title_i18n, _request_lang(self))


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


class ExpeditionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expedition
        fields = "__all__"


class StorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Story
        fields = "__all__"


class NavigationItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = NavigationItem
        fields = "__all__"


class SocialLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialLink
        fields = "__all__"
