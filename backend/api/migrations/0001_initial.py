from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Category",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=120)),
                ("image_url", models.URLField(max_length=500)),
                (
                    "size",
                    models.CharField(
                        choices=[
                            ("large", "Large"),
                            ("small", "Small"),
                            ("wide", "Wide"),
                        ],
                        default="small",
                        max_length=10,
                    ),
                ),
                ("order", models.PositiveIntegerField(default=0)),
                ("is_published", models.BooleanField(default=True)),
            ],
            options={"ordering": ("order", "id")},
        ),
        migrations.CreateModel(
            name="ContactMessage",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=120)),
                ("email", models.EmailField(max_length=254)),
                ("message", models.TextField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("is_read", models.BooleanField(default=False)),
            ],
            options={"ordering": ("-created_at",)},
        ),
        migrations.CreateModel(
            name="Expedition",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=150)),
                ("date_label", models.CharField(max_length=80)),
                ("description", models.TextField()),
                ("image_url", models.URLField(max_length=500)),
                ("order", models.PositiveIntegerField(default=0)),
                ("is_published", models.BooleanField(default=True)),
            ],
            options={"ordering": ("order", "id")},
        ),
        migrations.CreateModel(
            name="SiteContent",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("brand_name", models.CharField(default="Romanweiss", max_length=120)),
                ("hero_kicker", models.CharField(blank=True, max_length=200)),
                ("hero_title", models.CharField(default="Romanweiss", max_length=120)),
                ("hero_subtitle", models.TextField(blank=True)),
                ("hero_background_image", models.URLField(blank=True, max_length=500)),
                ("journal_intro", models.TextField(blank=True)),
                ("contact_title", models.CharField(default="Get in touch", max_length=120)),
                ("contact_description", models.TextField(blank=True)),
                ("contact_location", models.CharField(blank=True, max_length=200)),
                ("contact_email", models.EmailField(blank=True, max_length=254)),
                ("contact_socials", models.CharField(blank=True, max_length=250)),
                ("footer_title", models.CharField(default="Romanweiss", max_length=120)),
                ("footer_description", models.TextField(blank=True)),
                (
                    "newsletter_note",
                    models.CharField(
                        blank=True,
                        default="Updates from the road, once a month.",
                        max_length=200,
                    ),
                ),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"verbose_name_plural": "Site content"},
        ),
        migrations.CreateModel(
            name="Story",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=150)),
                ("date_label", models.CharField(max_length=80)),
                ("description", models.TextField()),
                ("image_url", models.URLField(max_length=500)),
                ("order", models.PositiveIntegerField(default=0)),
                ("is_published", models.BooleanField(default=True)),
            ],
            options={"ordering": ("order", "id")},
        ),
    ]
