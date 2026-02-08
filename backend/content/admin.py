from django.contrib import admin
from django.utils.html import format_html

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


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ("brand_name", "contact_email", "updated_at")
    search_fields = ("brand_name", "contact_email")
    ordering = ("-updated_at",)
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        ("Brand", {"fields": ("brand_name", "contact_email")}),
        (
            "Footer",
            {
                "fields": (
                    "footer_title",
                    "footer_description",
                    "footer_explore_title",
                    "footer_social_title",
                    "footer_newsletter_title",
                    "newsletter_note",
                )
            },
        ),
        (
            "Translations",
            {
                "fields": (
                    "brand_name_i18n",
                    "footer_title_i18n",
                    "footer_description_i18n",
                    "footer_explore_title_i18n",
                    "footer_social_title_i18n",
                    "footer_newsletter_title_i18n",
                    "newsletter_note_i18n",
                    "ui_i18n",
                )
            },
        ),
        (
            "SEO defaults",
            {"fields": ("seo_title", "seo_description", "seo_image")},
        ),
        ("System", {"fields": ("created_at", "updated_at")}),
    )

    def has_add_permission(self, request):
        if SiteSettings.objects.exists():
            return False
        return super().has_add_permission(request)


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
    extra = 0
    fields = (
        "key",
        "section_type",
        "title",
        "title_i18n",
        "subtitle",
        "subtitle_i18n",
        "body",
        "body_i18n",
        "payload",
        "payload_i18n",
        "order",
        "is_published",
    )
    show_change_link = True


class MenuItemInline(admin.TabularInline):
    model = MenuItem
    extra = 0
    fields = (
        "label",
        "label_i18n",
        "page",
        "href",
        "open_in_new_tab",
        "order",
        "is_published",
    )


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "is_home", "order", "is_published", "updated_at")
    list_editable = ("is_home", "order", "is_published")
    list_filter = ("is_home", "is_published")
    search_fields = ("title", "slug", "seo_title", "seo_description")
    ordering = ("order", "id")
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("created_at", "updated_at")
    inlines = (PageSectionInline,)
    fieldsets = (
        (
            "Core",
            {"fields": ("title", "title_i18n", "slug", "is_home", "order", "is_published")},
        ),
        (
            "SEO",
            {
                "fields": (
                    "seo_title",
                    "seo_title_i18n",
                    "seo_description",
                    "seo_description_i18n",
                    "seo_image",
                )
            },
        ),
        ("System", {"fields": ("created_at", "updated_at")}),
    )


@admin.register(PageSection)
class PageSectionAdmin(admin.ModelAdmin):
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
                    "subtitle",
                    "body",
                    "payload",
                    "order",
                    "is_published",
                )
            },
        ),
        (
            "Translations",
            {"fields": ("title_i18n", "subtitle_i18n", "body_i18n", "payload_i18n")},
        ),
        ("System", {"fields": ("created_at", "updated_at")}),
    )


@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
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
                    "title_i18n",
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
                    "label_i18n",
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
    list_display = (
        "title",
        "slug",
        "section",
        "href",
        "order",
        "is_published",
        "updated_at",
    )
    list_editable = ("order", "is_published")
    list_filter = ("section", "is_published")
    search_fields = ("title", "slug", "href")
    ordering = ("section", "order", "id")
    prepopulated_fields = {"slug": ("title",)}
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
