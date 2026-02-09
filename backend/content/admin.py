from django import forms
from django.contrib import admin
from django.db import models
from django.utils.html import format_html

from .models import (
    Category,
    Expedition,
    Language,
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


TRANSLATION_LANGUAGES = (("ru", "RU"), ("zh", "ZH"))


class LocalizedJSONModelForm(forms.ModelForm):
    translated_fields: tuple[str, ...] = ()

    class Meta:
        model = None
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in self.translated_fields:
            i18n_field_name = f"{field_name}_i18n"
            current_translations = getattr(self.instance, i18n_field_name, {}) or {}
            model_field = self._meta.model._meta.get_field(field_name)
            is_long_text = isinstance(model_field, models.TextField)

            for lang_code, lang_label in TRANSLATION_LANGUAGES:
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
            for lang_code, _ in TRANSLATION_LANGUAGES:
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


class MenuAdminForm(LocalizedJSONModelForm):
    translated_fields = ("title",)

    class Meta(LocalizedJSONModelForm.Meta):
        model = Menu


class MenuItemAdminForm(LocalizedJSONModelForm):
    translated_fields = ("label",)

    class Meta(LocalizedJSONModelForm.Meta):
        model = MenuItem


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    form = SiteSettingsAdminForm
    list_display = ("brand_name", "contact_email", "updated_at")
    search_fields = ("brand_name", "contact_email")
    ordering = ("-updated_at",)
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        (
            "Brand",
            {"fields": ("brand_name", "brand_name_ru", "brand_name_zh", "contact_email")},
        ),
        (
            "Footer",
            {
                "fields": (
                    "footer_title",
                    "footer_title_ru",
                    "footer_title_zh",
                    "footer_description",
                    "footer_description_ru",
                    "footer_description_zh",
                    "footer_explore_title",
                    "footer_explore_title_ru",
                    "footer_explore_title_zh",
                    "footer_social_title",
                    "footer_social_title_ru",
                    "footer_social_title_zh",
                    "footer_newsletter_title",
                    "footer_newsletter_title_ru",
                    "footer_newsletter_title_zh",
                    "newsletter_note",
                    "newsletter_note_ru",
                    "newsletter_note_zh",
                )
            },
        ),
        ("UI dictionary", {"fields": ("ui_i18n",)}),
        ("SEO defaults", {"fields": ("seo_title", "seo_description", "seo_image")}),
        ("System", {"fields": ("created_at", "updated_at")}),
    )

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
    fieldsets = (
        (
            "Core",
            {"fields": ("key", "group", "description", "text", "text_ru", "text_zh")},
        ),
        ("Publishing", {"fields": ("order", "is_published")}),
        ("System", {"fields": ("created_at", "updated_at")}),
    )


class ImagePreviewAdmin(admin.ModelAdmin):
    readonly_fields = ("image_preview", "created_at", "updated_at")

    def image_preview(self, obj):
        if not obj.image_url:
            return "-"
        return format_html(
            '<img src="{}" alt="preview" style="max-height: 80px; border-radius: 6px;" />',
            obj.image_url,
        )

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
        "title_ru",
        "title_zh",
        "subtitle",
        "subtitle_ru",
        "subtitle_zh",
        "body",
        "body_ru",
        "body_zh",
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
        "label_ru",
        "label_zh",
        "page",
        "href",
        "open_in_new_tab",
        "order",
        "is_published",
    )


class TranslationInline(admin.TabularInline):
    model = Translation
    extra = 0
    fields = ("language", "text", "updated_at")
    readonly_fields = ("updated_at",)


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
    fieldsets = (
        (
            "Core",
            {
                "fields": (
                    "title",
                    "title_ru",
                    "title_zh",
                    "slug",
                    "is_active",
                    "is_home",
                    "order",
                    "is_published",
                )
            },
        ),
        (
            "SEO",
            {
                "fields": (
                    "seo_title",
                    "seo_title_ru",
                    "seo_title_zh",
                    "seo_description",
                    "seo_description_ru",
                    "seo_description_zh",
                    "seo_image",
                )
            },
        ),
        ("System", {"fields": ("created_at", "updated_at")}),
    )


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
    fieldsets = (
        (
            "Core",
            {
                "fields": (
                    "page",
                    "key",
                    "section_type",
                    "title",
                    "title_ru",
                    "title_zh",
                    "subtitle",
                    "subtitle_ru",
                    "subtitle_zh",
                    "body",
                    "body_ru",
                    "body_zh",
                    "payload",
                    "payload_i18n",
                    "order",
                    "is_published",
                )
            },
        ),
        ("System", {"fields": ("created_at", "updated_at")}),
    )


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
    fieldsets = (
        (
            "Core",
            {
                "fields": (
                    "title",
                    "title_ru",
                    "title_zh",
                    "code",
                    "location",
                    "order",
                    "is_published",
                )
            },
        ),
        ("System", {"fields": ("created_at", "updated_at")}),
    )


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
    fieldsets = (
        (
            "Core",
            {
                "fields": (
                    "menu",
                    "label",
                    "label_ru",
                    "label_zh",
                    "page",
                    "href",
                    "open_in_new_tab",
                    "order",
                    "is_published",
                )
            },
        ),
        ("System", {"fields": ("created_at", "updated_at")}),
    )


@admin.register(Category)
class CategoryAdmin(ImagePreviewAdmin):
    list_display = ("title", "slug", "size", "order", "is_published", "updated_at")
    list_editable = ("order", "is_published")
    list_filter = ("size", "is_published")
    search_fields = ("title", "slug")
    ordering = ("order", "id")
    prepopulated_fields = {"slug": ("title",)}


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
    search_fields = ("title", "slug", "description")
    ordering = ("order", "id")
    prepopulated_fields = {"slug": ("title",)}


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
    fieldsets = (
        (
            "Core",
            {
                "fields": (
                    "title",
                    "title_ru",
                    "title_zh",
                    "slug",
                    "date_label",
                    "date_label_ru",
                    "date_label_zh",
                    "description",
                    "description_ru",
                    "description_zh",
                    "image_url",
                    "order",
                    "is_published",
                )
            },
        ),
        ("System", {"fields": ("created_at", "updated_at")}),
    )


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
    fieldsets = (
        (
            "Core",
            {
                "fields": (
                    "menu",
                    "section",
                    "title",
                    "title_ru",
                    "title_zh",
                    "slug",
                    "url_key",
                    "page",
                    "href",
                    "external_url",
                    "open_in_new_tab",
                    "order",
                    "is_published",
                )
            },
        ),
        ("System", {"fields": ("created_at", "updated_at")}),
    )


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
