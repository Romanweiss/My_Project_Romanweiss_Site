from django.db import models
from django.db.models import Q
from django.templatetags.static import static


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField("Created at", auto_now_add=True)
    updated_at = models.DateTimeField("Updated at", auto_now=True)

    class Meta:
        abstract = True


class OrderedPublishableModel(TimeStampedModel):
    order = models.PositiveIntegerField("Order", default=0)
    is_published = models.BooleanField("Published", default=True)

    class Meta:
        abstract = True


class SeoFieldsMixin(models.Model):
    seo_title = models.CharField("SEO title", max_length=255, blank=True)
    seo_description = models.CharField("SEO description", max_length=320, blank=True)
    seo_image = models.URLField("SEO image URL", max_length=500, blank=True)

    class Meta:
        abstract = True


class Language(TimeStampedModel):
    code = models.CharField("Code", max_length=12, unique=True)
    name = models.CharField("Name", max_length=120)
    is_default = models.BooleanField("Default", default=False)
    is_active = models.BooleanField("Active", default=True)
    order = models.PositiveIntegerField("Order", default=0)

    class Meta:
        verbose_name = "Language"
        verbose_name_plural = "Languages"
        ordering = ("order", "id")
        constraints = [
            models.UniqueConstraint(
                fields=("is_default",),
                condition=Q(is_default=True),
                name="content_single_default_language",
            ),
        ]

    def __str__(self):
        return f"{self.name} ({self.code})"


class SiteText(OrderedPublishableModel):
    key = models.CharField("Key", max_length=220, unique=True)
    group = models.CharField("Group", max_length=80, blank=True)
    description = models.CharField("Description", max_length=255, blank=True)
    text = models.TextField("Text (EN)")
    text_i18n = models.JSONField("Text translations", default=dict, blank=True)

    class Meta:
        verbose_name = "Site text"
        verbose_name_plural = "Site texts"
        ordering = ("group", "order", "key")

    def __str__(self):
        return self.key


class SiteSettings(TimeStampedModel, SeoFieldsMixin):
    brand_name = models.CharField("Brand name", max_length=120, default="Romanweiẞ")
    brand_name_i18n = models.JSONField("Brand name translations", default=dict, blank=True)
    footer_title = models.CharField("Footer title", max_length=120, default="Romanweiẞ")
    footer_title_i18n = models.JSONField("Footer title translations", default=dict, blank=True)
    footer_description = models.TextField(
        "Footer description",
        default=(
            "Capturing the silence of remote places, the texture of the wind, "
            "and the stories found in distance."
        ),
    )
    footer_description_i18n = models.JSONField(
        "Footer description translations", default=dict, blank=True
    )
    footer_explore_title = models.CharField(
        "Footer explore title", max_length=80, default="Explore"
    )
    footer_explore_title_i18n = models.JSONField(
        "Footer explore title translations", default=dict, blank=True
    )
    footer_social_title = models.CharField(
        "Footer social title", max_length=80, default="Social"
    )
    footer_social_title_i18n = models.JSONField(
        "Footer social title translations", default=dict, blank=True
    )
    footer_newsletter_title = models.CharField(
        "Footer newsletter title", max_length=80, default="Newsletter"
    )
    footer_newsletter_title_i18n = models.JSONField(
        "Footer newsletter title translations", default=dict, blank=True
    )
    newsletter_note = models.CharField(
        "Newsletter note", max_length=200, default="Updates from the road, once a month."
    )
    newsletter_note_i18n = models.JSONField(
        "Newsletter note translations", default=dict, blank=True
    )
    ui_i18n = models.JSONField("UI translations", default=dict, blank=True)
    contact_email = models.EmailField(
        "Contact email", max_length=254, default="hello@romanweiss.com"
    )

    class Meta:
        verbose_name = "Site settings"
        verbose_name_plural = "Site settings"

    def __str__(self):
        return self.brand_name


class MediaAsset(OrderedPublishableModel):
    title = models.CharField("Title", max_length=120)
    file = models.FileField("File", upload_to="content/media/", blank=True)
    static_path = models.CharField("Static path", max_length=255, blank=True)
    alt_text = models.CharField("Alt text", max_length=255, blank=True)

    class Meta:
        verbose_name = "Media asset"
        verbose_name_plural = "Media assets"
        ordering = ("order", "id")

    @property
    def resolved_url(self) -> str:
        if self.file:
            return self.file.url
        if self.static_path:
            return static(self.static_path)
        return ""

    def __str__(self):
        return self.title


class Category(OrderedPublishableModel):
    SIZE_LARGE = "large"
    SIZE_SMALL = "small"
    SIZE_WIDE = "wide"
    SIZE_CHOICES = (
        (SIZE_LARGE, "Large"),
        (SIZE_SMALL, "Small"),
        (SIZE_WIDE, "Wide"),
    )

    title = models.CharField("Title", max_length=120)
    slug = models.SlugField("Slug", max_length=140, unique=True)
    image_url = models.URLField("Image URL", max_length=500)
    cover = models.ForeignKey(
        MediaAsset,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="categories",
    )
    size = models.CharField("Size", max_length=10, choices=SIZE_CHOICES, default=SIZE_SMALL)

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ("order", "id")

    def __str__(self):
        return self.title


class CategoryGalleryItem(OrderedPublishableModel):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="gallery_items",
    )
    title = models.CharField("Title", max_length=180, blank=True)
    title_i18n = models.JSONField("Title translations", default=dict, blank=True)
    description = models.TextField("Description", blank=True)
    description_i18n = models.JSONField("Description translations", default=dict, blank=True)
    media = models.ForeignKey(
        MediaAsset,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="category_gallery_items",
    )
    image_url = models.URLField("Image URL", max_length=500, blank=True)
    alt_text = models.CharField("Alt text", max_length=255, blank=True)

    class Meta:
        verbose_name = "Category gallery item"
        verbose_name_plural = "Category gallery items"
        ordering = ("category_id", "order", "id")

    def __str__(self):
        label = self.title or f"item-{self.id}"
        return f"{self.category.title}: {label}"


class Expedition(OrderedPublishableModel):
    title = models.CharField("Title", max_length=150)
    slug = models.SlugField("Slug", max_length=170, unique=True)
    subtitle = models.CharField("Subtitle", max_length=220, blank=True)
    date_label = models.CharField("Date label", max_length=80)
    description = models.TextField("Description")
    image_url = models.URLField("Image URL", max_length=500)
    cover = models.ForeignKey(
        MediaAsset,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="expeditions",
    )

    class Meta:
        verbose_name = "Expedition"
        verbose_name_plural = "Expeditions"
        ordering = ("order", "id")

    def __str__(self):
        return self.title


class ExpeditionMedia(OrderedPublishableModel):
    KIND_IMAGE = "image"
    KIND_VIDEO = "video"
    KIND_STORY = "story"
    KIND_CHOICES = (
        (KIND_IMAGE, "Image"),
        (KIND_VIDEO, "Video"),
        (KIND_STORY, "Story"),
    )

    expedition = models.ForeignKey(
        Expedition,
        on_delete=models.CASCADE,
        related_name="media_items",
    )
    kind = models.CharField("Kind", max_length=20, choices=KIND_CHOICES, default=KIND_IMAGE)
    title = models.CharField("Title", max_length=180, blank=True)
    title_i18n = models.JSONField("Title translations", default=dict, blank=True)
    body = models.TextField("Body", blank=True)
    body_i18n = models.JSONField("Body translations", default=dict, blank=True)
    media = models.ForeignKey(
        MediaAsset,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="expedition_media_items",
    )
    image_url = models.URLField("Image URL", max_length=500, blank=True)
    video_url = models.URLField("Video URL", max_length=500, blank=True)
    alt_text = models.CharField("Alt text", max_length=255, blank=True)

    class Meta:
        verbose_name = "Expedition media"
        verbose_name_plural = "Expedition media"
        ordering = ("expedition_id", "order", "id")

    def __str__(self):
        return f"{self.expedition.title}: {self.kind}"


class Story(OrderedPublishableModel):
    title = models.CharField("Title", max_length=150)
    title_i18n = models.JSONField("Title translations", default=dict, blank=True)
    slug = models.SlugField("Slug", max_length=170, unique=True)
    date_label = models.CharField("Date label", max_length=80)
    date_label_i18n = models.JSONField("Date label translations", default=dict, blank=True)
    description = models.TextField("Description")
    description_i18n = models.JSONField("Description translations", default=dict, blank=True)
    image_url = models.URLField("Image URL", max_length=500)
    cover = models.ForeignKey(
        MediaAsset,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="stories",
    )

    class Meta:
        verbose_name = "Story"
        verbose_name_plural = "Stories"
        ordering = ("order", "id")

    def __str__(self):
        return self.title


class NavigationItem(OrderedPublishableModel):
    SECTION_HEADER = "header"
    SECTION_FOOTER = "footer"
    SECTION_CHOICES = (
        (SECTION_HEADER, "Header"),
        (SECTION_FOOTER, "Footer"),
    )
    MENU_MAIN = "main"
    MENU_FOOTER = "footer"
    MENU_SOCIAL = "social"
    MENU_CHOICES = (
        (MENU_MAIN, "Main"),
        (MENU_FOOTER, "Footer"),
        (MENU_SOCIAL, "Social"),
    )

    section = models.CharField("Section", max_length=20, choices=SECTION_CHOICES)
    menu = models.CharField("Menu", max_length=20, choices=MENU_CHOICES, default=MENU_MAIN)
    title = models.CharField("Title", max_length=80)
    title_i18n = models.JSONField("Title translations", default=dict, blank=True)
    slug = models.SlugField("Slug", max_length=100, unique=True)
    url_key = models.SlugField("URL key", max_length=120, blank=True)
    page = models.ForeignKey(
        "Page",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="navigation_items",
    )
    external_url = models.CharField("External URL", max_length=300, blank=True)
    href = models.CharField("Href", max_length=200)
    open_in_new_tab = models.BooleanField("Open in new tab", default=False)

    class Meta:
        verbose_name = "Navigation item"
        verbose_name_plural = "Navigation items"
        ordering = ("menu", "order", "id")

    def __str__(self):
        return f"{self.get_section_display()}: {self.title}"


class SocialLink(OrderedPublishableModel):
    title = models.CharField("Title", max_length=80)
    slug = models.SlugField("Slug", max_length=100, unique=True)
    short_label = models.CharField("Short label", max_length=12)
    url = models.CharField("URL", max_length=300, blank=True)

    class Meta:
        verbose_name = "Social link"
        verbose_name_plural = "Social links"
        ordering = ("order", "id")

    def __str__(self):
        return self.title


class Page(OrderedPublishableModel, SeoFieldsMixin):
    title = models.CharField("Title", max_length=255)
    title_i18n = models.JSONField("Title translations", default=dict, blank=True)
    slug = models.SlugField("Slug", max_length=160, unique=True)
    is_active = models.BooleanField("Active", default=True)
    is_home = models.BooleanField("Home page", default=False)
    seo_title_i18n = models.JSONField("SEO title translations", default=dict, blank=True)
    seo_description_i18n = models.JSONField(
        "SEO description translations", default=dict, blank=True
    )

    class Meta:
        verbose_name = "Page"
        verbose_name_plural = "Pages"
        ordering = ("order", "id")
        constraints = [
            models.UniqueConstraint(
                fields=("is_home",),
                condition=Q(is_home=True),
                name="content_single_home_page",
            ),
        ]

    def __str__(self):
        return self.title


class HeroSection(OrderedPublishableModel):
    page = models.OneToOneField(
        Page,
        on_delete=models.CASCADE,
        related_name="hero",
        null=True,
        blank=True,
    )
    key = models.SlugField("Key", max_length=80, default="hero")
    kicker = models.CharField("Kicker", max_length=220, blank=True)
    title = models.CharField("Title", max_length=220)
    subtitle = models.CharField("Subtitle", max_length=320, blank=True)
    cta_label = models.CharField("CTA label", max_length=120, blank=True)
    cta_url = models.CharField("CTA URL", max_length=255, blank=True)
    scroll_label = models.CharField("Scroll label", max_length=120, blank=True)
    media = models.ForeignKey(
        MediaAsset,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="hero_sections",
    )

    class Meta:
        verbose_name = "Hero section"
        verbose_name_plural = "Hero sections"
        ordering = ("order", "id")

    def __str__(self):
        if self.page_id:
            return f"{self.page.slug}: {self.title}"
        return self.title


class PageSection(OrderedPublishableModel):
    TYPE_HERO = "hero"
    TYPE_RICH_TEXT = "rich_text"
    TYPE_CARDS = "cards"
    TYPE_GALLERY = "gallery"
    TYPE_STORIES = "stories"
    TYPE_CONTACT = "contact"
    TYPE_CHOICES = (
        (TYPE_HERO, "Hero"),
        (TYPE_RICH_TEXT, "Rich text"),
        (TYPE_CARDS, "Cards"),
        (TYPE_GALLERY, "Gallery"),
        (TYPE_STORIES, "Stories"),
        (TYPE_CONTACT, "Contact"),
    )

    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name="sections")
    key = models.SlugField("Key", max_length=80)
    section_type = models.CharField("Section type", max_length=32, choices=TYPE_CHOICES)
    title = models.CharField("Title", max_length=255, blank=True)
    title_i18n = models.JSONField("Title translations", default=dict, blank=True)
    subtitle = models.CharField("Subtitle", max_length=320, blank=True)
    subtitle_i18n = models.JSONField("Subtitle translations", default=dict, blank=True)
    body = models.TextField("Body", blank=True)
    body_i18n = models.JSONField("Body translations", default=dict, blank=True)
    payload = models.JSONField("Payload", default=dict, blank=True)
    payload_i18n = models.JSONField("Payload translations", default=dict, blank=True)

    class Meta:
        verbose_name = "Page section"
        verbose_name_plural = "Page sections"
        ordering = ("page_id", "order", "id")
        constraints = [
            models.UniqueConstraint(
                fields=("page", "key"), name="content_unique_page_section_key"
            ),
        ]

    def __str__(self):
        return f"{self.page.title}: {self.key}"


class SectionImage(OrderedPublishableModel):
    section = models.ForeignKey(
        PageSection, on_delete=models.CASCADE, related_name="images"
    )
    image_url = models.URLField("Image URL", max_length=500)
    alt_text = models.CharField("Alt text", max_length=255, blank=True)
    caption = models.CharField("Caption", max_length=255, blank=True)

    class Meta:
        verbose_name = "Section image"
        verbose_name_plural = "Section images"
        ordering = ("section_id", "order", "id")

    def __str__(self):
        return self.alt_text or self.image_url


class Menu(OrderedPublishableModel):
    LOCATION_MAIN = "main"
    LOCATION_FOOTER = "footer"
    LOCATION_SOCIAL = "social"
    LOCATION_CHOICES = (
        (LOCATION_MAIN, "Main"),
        (LOCATION_FOOTER, "Footer"),
        (LOCATION_SOCIAL, "Social"),
    )

    code = models.SlugField("Code", max_length=50, unique=True)
    title = models.CharField("Title", max_length=120)
    title_i18n = models.JSONField("Title translations", default=dict, blank=True)
    location = models.CharField(
        "Location",
        max_length=20,
        choices=LOCATION_CHOICES,
        default=LOCATION_MAIN,
    )

    class Meta:
        verbose_name = "Menu"
        verbose_name_plural = "Menus"
        ordering = ("order", "id")

    def __str__(self):
        return self.title


class MenuItem(OrderedPublishableModel):
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE, related_name="items")
    label = models.CharField("Label", max_length=120)
    label_i18n = models.JSONField("Label translations", default=dict, blank=True)
    page = models.ForeignKey(
        Page,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="menu_items",
    )
    href = models.CharField("Href", max_length=255, blank=True)
    open_in_new_tab = models.BooleanField("Open in new tab", default=False)

    class Meta:
        verbose_name = "Menu item"
        verbose_name_plural = "Menu items"
        ordering = ("menu_id", "order", "id")

    def __str__(self):
        return f"{self.menu.title}: {self.label}"


class TranslationKey(TimeStampedModel):
    key = models.CharField("Key", max_length=220, unique=True)
    namespace = models.CharField("Namespace", max_length=80, blank=True)
    description = models.CharField("Description", max_length=255, blank=True)
    is_active = models.BooleanField("Active", default=True)

    class Meta:
        verbose_name = "Translation key"
        verbose_name_plural = "Translation keys"
        ordering = ("namespace", "key")

    def __str__(self):
        return self.key


class Translation(TimeStampedModel):
    language = models.ForeignKey(
        Language, on_delete=models.CASCADE, related_name="translations"
    )
    key = models.ForeignKey(
        TranslationKey, on_delete=models.CASCADE, related_name="translations"
    )
    text = models.TextField("Text")

    class Meta:
        verbose_name = "Translation"
        verbose_name_plural = "Translations"
        ordering = ("language__order", "key__key")
        constraints = [
            models.UniqueConstraint(
                fields=("language", "key"),
                name="content_unique_language_translation_key",
            ),
        ]

    def __str__(self):
        return f"{self.language.code}: {self.key.key}"
