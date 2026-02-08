from django.contrib import admin

from .models import Category, ContactMessage, Expedition, SiteContent, Story


@admin.register(SiteContent)
class SiteContentAdmin(admin.ModelAdmin):
    list_display = ("brand_name", "updated_at")
    readonly_fields = ("updated_at",)


@admin.register(Expedition)
class ExpeditionAdmin(admin.ModelAdmin):
    list_display = ("title", "date_label", "order", "is_published")
    list_editable = ("order", "is_published")
    search_fields = ("title", "description")
    ordering = ("order", "id")


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("title", "size", "order", "is_published")
    list_editable = ("size", "order", "is_published")
    search_fields = ("title",)
    ordering = ("order", "id")


@admin.register(Story)
class StoryAdmin(admin.ModelAdmin):
    list_display = ("title", "date_label", "order", "is_published")
    list_editable = ("order", "is_published")
    search_fields = ("title", "description")
    ordering = ("order", "id")


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "created_at", "is_read")
    list_filter = ("is_read", "created_at")
    list_editable = ("is_read",)
    search_fields = ("name", "email", "message")
    ordering = ("-created_at",)
    readonly_fields = ("name", "email", "message", "created_at")
