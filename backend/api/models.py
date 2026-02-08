from django.db import models


class SiteContent(models.Model):
    brand_name = models.CharField(max_length=120, default="Romanweiss")
    hero_kicker = models.CharField(max_length=200, blank=True)
    hero_title = models.CharField(max_length=120, default="Romanweiss")
    hero_subtitle = models.TextField(blank=True)
    hero_background_image = models.URLField(max_length=500, blank=True)
    journal_intro = models.TextField(blank=True)
    contact_title = models.CharField(max_length=120, default="Get in touch")
    contact_description = models.TextField(blank=True)
    contact_location = models.CharField(max_length=200, blank=True)
    contact_email = models.EmailField(blank=True)
    contact_socials = models.CharField(max_length=250, blank=True)
    footer_title = models.CharField(max_length=120, default="Romanweiss")
    footer_description = models.TextField(blank=True)
    newsletter_note = models.CharField(
        max_length=200,
        default="Updates from the road, once a month.",
        blank=True,
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Site content"

    def __str__(self):
        return self.brand_name


class Expedition(models.Model):
    title = models.CharField(max_length=150)
    date_label = models.CharField(max_length=80)
    description = models.TextField()
    image_url = models.URLField(max_length=500)
    order = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ("order", "id")

    def __str__(self):
        return self.title


class Category(models.Model):
    SIZE_LARGE = "large"
    SIZE_SMALL = "small"
    SIZE_WIDE = "wide"
    SIZE_CHOICES = (
        (SIZE_LARGE, "Large"),
        (SIZE_SMALL, "Small"),
        (SIZE_WIDE, "Wide"),
    )

    title = models.CharField(max_length=120)
    image_url = models.URLField(max_length=500)
    size = models.CharField(max_length=10, choices=SIZE_CHOICES, default=SIZE_SMALL)
    order = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ("order", "id")

    def __str__(self):
        return self.title


class Story(models.Model):
    title = models.CharField(max_length=150)
    date_label = models.CharField(max_length=80)
    description = models.TextField()
    image_url = models.URLField(max_length=500)
    order = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ("order", "id")

    def __str__(self):
        return self.title


class ContactMessage(models.Model):
    name = models.CharField(max_length=120)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.name} <{self.email}>"
