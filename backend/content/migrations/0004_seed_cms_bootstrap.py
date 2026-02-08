from django.db import migrations


HERO_IMAGE = "https://images.unsplash.com/photo-1469474968028-56623f02e42e?auto=format&fit=crop&w=2000&q=80"
JOURNAL_INTRO = (
    "We travel not to escape life, but for life not to escape us. "
    "This journal is a collection of moments from the road - "
    "a visual diary of silence, texture, and light."
)
CONTACT_COPY = (
    "Interested in a collaboration, a print, or just want to say hello? "
    "I am always open to discussing new projects and creative opportunities."
)


def seed_cms_bootstrap(apps, schema_editor):
    SiteSettings = apps.get_model("content", "SiteSettings")
    Expedition = apps.get_model("content", "Expedition")
    Category = apps.get_model("content", "Category")
    Story = apps.get_model("content", "Story")
    NavigationItem = apps.get_model("content", "NavigationItem")
    SocialLink = apps.get_model("content", "SocialLink")
    Page = apps.get_model("content", "Page")
    PageSection = apps.get_model("content", "PageSection")
    SectionImage = apps.get_model("content", "SectionImage")
    Menu = apps.get_model("content", "Menu")
    MenuItem = apps.get_model("content", "MenuItem")

    site_settings = SiteSettings.objects.order_by("-updated_at").first()
    if site_settings is None:
        site_settings = SiteSettings.objects.create()

    if not site_settings.seo_title:
        site_settings.seo_title = site_settings.brand_name
    if not site_settings.seo_description:
        site_settings.seo_description = site_settings.footer_description[:320]
    if not site_settings.seo_image:
        site_settings.seo_image = HERO_IMAGE
    site_settings.save(update_fields=["seo_title", "seo_description", "seo_image"])

    home_page, _ = Page.objects.get_or_create(
        slug="home",
        defaults={
            "title": "Home",
            "is_home": True,
            "order": 1,
            "is_published": True,
            "seo_title": site_settings.seo_title,
            "seo_description": site_settings.seo_description,
            "seo_image": site_settings.seo_image,
        },
    )

    if not home_page.is_home:
        home_page.is_home = True
        home_page.save(update_fields=["is_home"])

    hero_section, _ = PageSection.objects.get_or_create(
        page=home_page,
        key="hero",
        defaults={
            "section_type": "hero",
            "title": site_settings.brand_name,
            "subtitle": "Exploring landscapes, architecture, and the distance between moments.",
            "payload": {
                "kicker": "Travel & Expedition Photography",
                "scroll_label": "Scroll to begin",
            },
            "order": 1,
            "is_published": True,
        },
    )
    if not SectionImage.objects.filter(section=hero_section).exists():
        SectionImage.objects.create(
            section=hero_section,
            image_url=HERO_IMAGE,
            alt_text=f"{site_settings.brand_name} hero image",
            order=1,
            is_published=True,
        )

    PageSection.objects.get_or_create(
        page=home_page,
        key="journal-intro",
        defaults={
            "section_type": "rich_text",
            "body": JOURNAL_INTRO,
            "order": 2,
            "is_published": True,
        },
    )

    expeditions = Expedition.objects.filter(is_published=True).order_by("order", "id")
    expedition_cards = [
        {
            "title": expedition.title,
            "date_label": expedition.date_label,
            "description": expedition.description,
            "image_url": expedition.image_url,
        }
        for expedition in expeditions
    ]
    PageSection.objects.get_or_create(
        page=home_page,
        key="expeditions",
        defaults={
            "section_type": "cards",
            "payload": {
                "eyebrow": "The Journal",
                "title": "Recent Expeditions",
                "subtitle": "Journeys into the remote.",
                "action_label": "View all ->",
                "cards": expedition_cards,
            },
            "order": 3,
            "is_published": True,
        },
    )

    categories = Category.objects.filter(is_published=True).order_by("order", "id")
    category_items = [
        {
            "title": category.title,
            "image_url": category.image_url,
            "size": category.size,
        }
        for category in categories
    ]
    PageSection.objects.get_or_create(
        page=home_page,
        key="categories",
        defaults={
            "section_type": "gallery",
            "payload": {
                "eyebrow": "Portfolio",
                "title": "Fields of Focus",
                "subtitle": "Visual separation through imagery, not boxes.",
                "items": category_items,
            },
            "order": 4,
            "is_published": True,
        },
    )

    stories = Story.objects.filter(is_published=True).order_by("order", "id")
    story_items = [
        {
            "title": story.title,
            "date_label": story.date_label,
            "description": story.description,
            "image_url": story.image_url,
        }
        for story in stories
    ]
    PageSection.objects.get_or_create(
        page=home_page,
        key="stories",
        defaults={
            "section_type": "stories",
            "payload": {
                "eyebrow": "Visual Stories",
                "title": "Selected Stories",
                "action_label": "Read full story",
                "items": story_items,
            },
            "order": 5,
            "is_published": True,
        },
    )

    PageSection.objects.get_or_create(
        page=home_page,
        key="contact",
        defaults={
            "section_type": "contact",
            "title": "Get in touch",
            "body": CONTACT_COPY,
            "payload": {
                "location": "Berlin, Germany",
                "email": site_settings.contact_email,
            },
            "order": 6,
            "is_published": True,
        },
    )

    main_menu, _ = Menu.objects.get_or_create(
        code="main",
        defaults={
            "title": "Main navigation",
            "location": "main",
            "order": 1,
            "is_published": True,
        },
    )
    footer_menu, _ = Menu.objects.get_or_create(
        code="footer",
        defaults={
            "title": "Footer navigation",
            "location": "footer",
            "order": 2,
            "is_published": True,
        },
    )
    social_menu, _ = Menu.objects.get_or_create(
        code="social",
        defaults={
            "title": "Social links",
            "location": "social",
            "order": 3,
            "is_published": True,
        },
    )

    if not MenuItem.objects.filter(menu=main_menu).exists():
        header_items = NavigationItem.objects.filter(
            is_published=True, section="header"
        ).order_by("order", "id")
        if header_items.exists():
            for nav_item in header_items:
                MenuItem.objects.get_or_create(
                    menu=main_menu,
                    label=nav_item.title,
                    defaults={
                        "href": nav_item.href,
                        "order": nav_item.order,
                        "is_published": True,
                    },
                )
        else:
            MenuItem.objects.get_or_create(
                menu=main_menu,
                label="Journey",
                defaults={"href": "#journey", "order": 1, "is_published": True},
            )

    if not MenuItem.objects.filter(menu=footer_menu).exists():
        footer_items = NavigationItem.objects.filter(
            is_published=True, section="footer"
        ).order_by("order", "id")
        if footer_items.exists():
            for nav_item in footer_items:
                MenuItem.objects.get_or_create(
                    menu=footer_menu,
                    label=nav_item.title,
                    defaults={
                        "href": nav_item.href,
                        "order": nav_item.order,
                        "is_published": True,
                    },
                )
        else:
            MenuItem.objects.get_or_create(
                menu=footer_menu,
                label="Contact",
                defaults={"href": "#contact", "order": 1, "is_published": True},
            )

    if not MenuItem.objects.filter(menu=social_menu).exists():
        social_links = SocialLink.objects.filter(is_published=True).order_by("order", "id")
        if social_links.exists():
            for social_link in social_links:
                MenuItem.objects.get_or_create(
                    menu=social_menu,
                    label=social_link.short_label or social_link.title,
                    defaults={
                        "href": social_link.url,
                        "order": social_link.order,
                        "is_published": True,
                        "open_in_new_tab": str(social_link.url).startswith("http"),
                    },
                )
        else:
            MenuItem.objects.get_or_create(
                menu=social_menu,
                label="Mail",
                defaults={
                    "href": f"mailto:{site_settings.contact_email}",
                    "order": 1,
                    "is_published": True,
                },
            )


def noop_reverse(apps, schema_editor):
    return None


class Migration(migrations.Migration):
    dependencies = [
        ("content", "0003_cms_schema"),
    ]

    operations = [migrations.RunPython(seed_cms_bootstrap, noop_reverse)]
