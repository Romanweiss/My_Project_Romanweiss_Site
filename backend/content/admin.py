from django import forms
from django.conf import settings
from django.contrib import admin
from django.db import models
from django.utils.html import format_html

from .models import (
    Category,
    CategoryGalleryItem,
    Expedition,
    ExpeditionMedia,
    HeroSection,
    Language,
    MediaAsset,
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
    Translation,
    TranslationKey,
)


def _translation_languages() -> list[tuple[str, str]]:
    default_lang = (settings.LANGUAGE_CODE or "en").split("-")[0].lower()
    try:
        rows = (
            Language.objects.filter(is_active=True)
            .exclude(code=default_lang)
            .order_by("order", "id")
            .values_list("code", "name")
        )
        data = [(str(code).lower(), str(name)) for code, name in rows if code]
        if data:
            return data
    except Exception:
        pass

    fallback = []
    for code, name in getattr(settings, "LANGUAGES", ()):
        normalized = str(code).lower()
        if normalized != default_lang:
            fallback.append((normalized, str(name)))
    return fallback


def _asset_preview_html(asset: MediaAsset | None, legacy_url: str = "") -> str:
    if asset and asset.resolved_url:
        return format_html(
            '<img src="{}" alt="preview" style="max-height: 80px; border-radius: 6px;" />',
            asset.resolved_url,
        )
    if legacy_url:
        return format_html(
            '<img src="{}" alt="preview" style="max-height: 80px; border-radius: 6px;" />',
            legacy_url,
        )
    return "-"


class LocalizedJSONModelForm(forms.ModelForm):
    translated_fields: tuple[str, ...] = ()

    class Meta:
        model = None
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._language_codes = [code for code, _ in _translation_languages()]

        for field_name in self.translated_fields:
            i18n_field_name = f"{field_name}_i18n"
            current_translations = getattr(self.instance, i18n_field_name, {}) or {}
            model_field = self._meta.model._meta.get_field(field_name)
            is_long_text = isinstance(model_field, models.TextField)

            for lang_code, lang_label in _translation_languages():
                dynamic_name = f"{field_name}_{lang_code}"
                base_label = self.fields[field_name].label or field_name
                widget = forms.Textarea(attrs={"rows": 3}) if is_long_text else forms.TextInput()
                self.fields[dynamic_name] = forms.CharField(
                    required=False,
                    label=f"{base_label} ({lang_label})",
                    widget=widget,
                )
                value = current_translations.get(lang_code, "")
                self.initial[dynamic_name] = value if isinstance(value, str) else ""

    def save(self, commit=True):
        instance = super().save(commit=False)
        for field_name in self.translated_fields:
            i18n_field_name = f"{field_name}_i18n"
            updated_translations = dict(getattr(instance, i18n_field_name, {}) or {})
            for lang_code in self._language_codes:
                dynamic_name = f"{field_name}_{lang_code}"
                raw_value = self.cleaned_data.get(dynamic_name, "")
                value = raw_value.strip() if isinstance(raw_value, str) else ""
                if value:
                    updated_translations[lang_code] = value
                else:
                    updated_translations.pop(lang_code, None)
            setattr(instance, i18n_field_name, updated_translations)

        if commit:
            instance.save()
            self.save_m2m()
        return instance


class SiteSettingsAdminForm(LocalizedJSONModelForm):
    translated_fields = (
        "brand_name",
        "footer_title",
        "footer_description",
        "footer_explore_title",
        "footer_social_title",
        "footer_newsletter_title",
        "newsletter_note",
    )

    class Meta(LocalizedJSONModelForm.Meta):
        model = SiteSettings


class SiteTextAdminForm(LocalizedJSONModelForm):
    translated_fields = ("text",)

    class Meta(LocalizedJSONModelForm.Meta):
        model = SiteText


class PageAdminForm(LocalizedJSONModelForm):
    translated_fields = ("title", "seo_title", "seo_description")

    class Meta(LocalizedJSONModelForm.Meta):
        model = Page


class PageSectionAdminForm(LocalizedJSONModelForm):
    translated_fields = ("title", "subtitle", "body")

    class Meta(LocalizedJSONModelForm.Meta):
        model = PageSection


class NavigationItemAdminForm(LocalizedJSONModelForm):
    translated_fields = ("title",)

    class Meta(LocalizedJSONModelForm.Meta):
        model = NavigationItem


class StoryAdminForm(LocalizedJSONModelForm):
    translated_fields = ("title", "date_label", "description")

    class Meta(LocalizedJSONModelForm.Meta):
        model = Story


class CategoryGalleryItemAdminForm(LocalizedJSONModelForm):
    translated_fields = ("title", "description")

    class Meta(LocalizedJSONModelForm.Meta):
        model = CategoryGalleryItem


class ExpeditionMediaAdminForm(LocalizedJSONModelForm):
    translated_fields = ("title", "body")

    class Meta(LocalizedJSONModelForm.Meta):
        model = ExpeditionMedia


class MenuAdminForm(LocalizedJSONModelForm):
    translated_fields = ("title",)

    class Meta(LocalizedJSONModelForm.Meta):
        model = Menu


class MenuItemAdminForm(LocalizedJSONModelForm):
    translated_fields = ("label",)

    class Meta(LocalizedJSONModelForm.Meta):
        model = MenuItem


class HeroSectionAdminForm(LocalizedJSONModelForm):
    translated_fields = ("kicker", "title", "subtitle", "cta_label", "scroll_label")

    class Meta(LocalizedJSONModelForm.Meta):
        model = HeroSection


class ImagePreviewAdmin(admin.ModelAdmin):
    readonly_fields = ("image_preview", "created_at", "updated_at")

    def image_preview(self, obj):
        legacy = getattr(obj, "image_url", "")
        cover = getattr(obj, "cover", None)
        return _asset_preview_html(cover, legacy)

    image_preview.short_description = "Preview"


class SectionImageInline(admin.TabularInline):
    model = SectionImage
    extra = 0
    fields = ("order", "is_published", "image_url", "alt_text", "caption", "image_preview")
    readonly_fields = ("image_preview",)

    def image_preview(self, obj):
        if not obj or not obj.image_url:
            return "-"
        return format_html(
            '<img src="{}" alt="preview" style="max-height: 70px; border-radius: 6px;" />',
            obj.image_url,
        )

    image_preview.short_description = "Preview"


class PageSectionInline(admin.StackedInline):
    model = PageSection
    form = PageSectionAdminForm
    extra = 0
    fields = (
        "key",
        "section_type",
        "title",
        "subtitle",
        "body",
        "payload",
        "payload_i18n",
        "order",
        "is_published",
    )
    show_change_link = True


class MenuItemInline(admin.TabularInline):
    model = MenuItem
    form = MenuItemAdminForm
    extra = 0
    fields = (
        "label",
        "page",
        "href",
        "open_in_new_tab",
        "order",
        "is_published",
    )


class ExpeditionMediaInline(admin.StackedInline):
    model = ExpeditionMedia
    form = ExpeditionMediaAdminForm
    extra = 0
    fields = (
        "kind",
        "title",
        "body",
        "media",
        "image_url",
        "video_url",
        "alt_text",
        "order",
        "is_published",
    )


class CategoryGalleryItemInline(admin.StackedInline):
    model = CategoryGalleryItem
    form = CategoryGalleryItemAdminForm
    extra = 0
    fields = (
        "title",
        "description",
        "media",
        "image_url",
        "alt_text",
        "image_preview",
        "order",
        "is_published",
    )
    readonly_fields = ("image_preview",)

    def image_preview(self, obj):
        if not obj:
            return "-"
        return _asset_preview_html(getattr(obj, "media", None), getattr(obj, "image_url", ""))

    image_preview.short_description = "Preview"


class TranslationInline(admin.TabularInline):
    model = Translation
    extra = 0
    fields = ("language", "text", "updated_at")
    readonly_fields = ("updated_at",)


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    form = SiteSettingsAdminForm
    list_display = ("brand_name", "contact_email", "updated_at")
    search_fields = ("brand_name", "contact_email")
    ordering = ("-updated_at",)
    readonly_fields = ("created_at", "updated_at")

    def has_add_permission(self, request):
        if SiteSettings.objects.exists():
            return False
        return super().has_add_permission(request)


@admin.register(SiteText)
class SiteTextAdmin(admin.ModelAdmin):
    form = SiteTextAdminForm
    list_display = ("key", "group", "order", "is_published", "updated_at")
    list_editable = ("order", "is_published")
    list_filter = ("group", "is_published")
    search_fields = ("key", "group", "description", "text")
    ordering = ("group", "order", "key")
    readonly_fields = ("created_at", "updated_at")


@admin.register(MediaAsset)
class MediaAssetAdmin(admin.ModelAdmin):
    list_display = ("title", "order", "is_published", "updated_at", "image_preview")
    list_editable = ("order", "is_published")
    search_fields = ("title", "alt_text", "static_path")
    ordering = ("order", "id")
    readonly_fields = ("image_preview", "created_at", "updated_at")

    def image_preview(self, obj):
        return _asset_preview_html(obj)

    image_preview.short_description = "Preview"


@admin.register(HeroSection)
class HeroSectionAdmin(admin.ModelAdmin):
    form = HeroSectionAdminForm
    list_display = ("title", "page", "key", "order", "is_published", "updated_at")
    list_editable = ("order", "is_published")
    list_filter = ("is_published",)
    search_fields = ("title", "kicker", "subtitle", "key", "page__slug")
    ordering = ("order", "id")
    prepopulated_fields = {"key": ("title",)}
    readonly_fields = ("created_at", "updated_at", "image_preview")

    def image_preview(self, obj):
        return _asset_preview_html(obj.media)

    image_preview.short_description = "Preview"


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "is_default", "is_active", "order", "updated_at")
    list_editable = ("is_default", "is_active", "order")
    list_filter = ("is_default", "is_active")
    search_fields = ("name", "code")
    ordering = ("order", "id")
    readonly_fields = ("created_at", "updated_at")


@admin.register(TranslationKey)
class TranslationKeyAdmin(admin.ModelAdmin):
    list_display = ("key", "namespace", "is_active", "updated_at")
    list_editable = ("is_active",)
    list_filter = ("namespace", "is_active")
    search_fields = ("key", "namespace", "description")
    ordering = ("namespace", "key")
    readonly_fields = ("created_at", "updated_at")
    inlines = (TranslationInline,)


@admin.register(Translation)
class TranslationAdmin(admin.ModelAdmin):
    list_display = ("key", "language", "updated_at")
    list_filter = ("language", "key__namespace")
    search_fields = ("key__key", "text")
    ordering = ("language__order", "key__key")
    readonly_fields = ("created_at", "updated_at")


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    form = PageAdminForm
    list_display = (
        "title",
        "slug",
        "is_active",
        "is_home",
        "order",
        "is_published",
        "updated_at",
    )
    list_editable = ("is_active", "is_home", "order", "is_published")
    list_filter = ("is_active", "is_home", "is_published")
    search_fields = ("title", "slug", "seo_title", "seo_description")
    ordering = ("order", "id")
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("created_at", "updated_at")
    inlines = (PageSectionInline,)


@admin.register(PageSection)
class PageSectionAdmin(admin.ModelAdmin):
    form = PageSectionAdminForm
    list_display = (
        "page",
        "key",
        "section_type",
        "order",
        "is_published",
        "updated_at",
    )
    list_editable = ("order", "is_published")
    list_filter = ("section_type", "is_published")
    search_fields = ("page__title", "key", "title")
    ordering = ("page_id", "order", "id")
    readonly_fields = ("created_at", "updated_at")
    inlines = (SectionImageInline,)


@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    form = MenuAdminForm
    list_display = ("title", "code", "location", "order", "is_published", "updated_at")
    list_editable = ("order", "is_published")
    list_filter = ("location", "is_published")
    search_fields = ("title", "code")
    ordering = ("order", "id")
    prepopulated_fields = {"code": ("title",)}
    readonly_fields = ("created_at", "updated_at")
    inlines = (MenuItemInline,)


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    form = MenuItemAdminForm
    list_display = (
        "label",
        "menu",
        "href",
        "open_in_new_tab",
        "order",
        "is_published",
        "updated_at",
    )
    list_editable = ("open_in_new_tab", "order", "is_published")
    list_filter = ("menu", "is_published", "open_in_new_tab")
    search_fields = ("label", "href", "menu__title")
    ordering = ("menu_id", "order", "id")
    readonly_fields = ("created_at", "updated_at")


@admin.register(Category)
class CategoryAdmin(ImagePreviewAdmin):
    list_display = ("title", "slug", "size", "order", "is_published", "updated_at")
    list_editable = ("order", "is_published")
    list_filter = ("size", "is_published")
    search_fields = ("title", "slug")
    ordering = ("order", "id")
    prepopulated_fields = {"slug": ("title",)}
    inlines = (CategoryGalleryItemInline,)


@admin.register(CategoryGalleryItem)
class CategoryGalleryItemAdmin(admin.ModelAdmin):
    form = CategoryGalleryItemAdminForm
    list_display = ("category", "title", "order", "is_published", "updated_at")
    list_editable = ("order", "is_published")
    list_filter = ("is_published", "category")
    search_fields = ("category__title", "title", "description", "image_url", "alt_text")
    ordering = ("category_id", "order", "id")
    readonly_fields = ("created_at", "updated_at", "image_preview")

    def image_preview(self, obj):
        return _asset_preview_html(getattr(obj, "media", None), getattr(obj, "image_url", ""))

    image_preview.short_description = "Preview"


@admin.register(Expedition)
class ExpeditionAdmin(ImagePreviewAdmin):
    list_display = (
        "title",
        "slug",
        "date_label",
        "order",
        "is_published",
        "updated_at",
    )
    list_editable = ("order", "is_published")
    list_filter = ("is_published",)
    search_fields = ("title", "slug", "subtitle", "description")
    ordering = ("order", "id")
    prepopulated_fields = {"slug": ("title",)}
    inlines = (ExpeditionMediaInline,)


@admin.register(ExpeditionMedia)
class ExpeditionMediaAdmin(admin.ModelAdmin):
    form = ExpeditionMediaAdminForm
    list_display = ("expedition", "kind", "title", "order", "is_published", "updated_at")
    list_editable = ("order", "is_published")
    list_filter = ("kind", "is_published")
    search_fields = ("expedition__title", "title", "body", "video_url", "image_url")
    ordering = ("expedition_id", "order", "id")
    readonly_fields = ("created_at", "updated_at")


@admin.register(Story)
class StoryAdmin(ImagePreviewAdmin):
    form = StoryAdminForm
    list_display = (
        "title",
        "slug",
        "date_label",
        "order",
        "is_published",
        "updated_at",
    )
    list_editable = ("order", "is_published")
    list_filter = ("is_published",)
    search_fields = ("title", "slug", "description")
    ordering = ("order", "id")
    prepopulated_fields = {"slug": ("title",)}


@admin.register(NavigationItem)
class NavigationItemAdmin(admin.ModelAdmin):
    form = NavigationItemAdminForm
    list_display = (
        "title",
        "menu",
        "section",
        "url_key",
        "page",
        "href",
        "external_url",
        "order",
        "is_published",
        "updated_at",
    )
    list_editable = ("order", "is_published")
    list_filter = ("menu", "section", "is_published", "open_in_new_tab")
    search_fields = ("title", "slug", "url_key", "href", "external_url")
    ordering = ("menu", "order", "id")
    prepopulated_fields = {"slug": ("title",), "url_key": ("title",)}
    readonly_fields = ("created_at", "updated_at")


@admin.register(SocialLink)
class SocialLinkAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "slug",
        "short_label",
        "url",
        "order",
        "is_published",
        "updated_at",
    )
    list_editable = ("order", "is_published")
    list_filter = ("is_published",)
    search_fields = ("title", "slug", "url")
    ordering = ("order", "id")
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("created_at", "updated_at")
