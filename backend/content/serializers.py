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


class SiteSettingsSerializer(serializers.ModelSerializer):
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
            "created_at",
            "updated_at",
        )


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


class PageSerializer(serializers.ModelSerializer):
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


class MenuItemSerializer(serializers.ModelSerializer):
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


class MenuSerializer(serializers.ModelSerializer):
    items = serializers.SerializerMethodField()

    class Meta:
        model = Menu
        fields = ("id", "code", "title", "location", "items")

    def get_items(self, obj):
        items = [item for item in obj.items.all() if item.is_published]
        items.sort(key=lambda item: (item.order, item.id))
        return MenuItemSerializer(items, many=True).data


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
