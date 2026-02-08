from django.db import migrations


def seed_content(apps, schema_editor):
    SiteSettings = apps.get_model("content", "SiteSettings")
    Category = apps.get_model("content", "Category")
    Expedition = apps.get_model("content", "Expedition")
    Story = apps.get_model("content", "Story")
    NavigationItem = apps.get_model("content", "NavigationItem")
    SocialLink = apps.get_model("content", "SocialLink")

    if not SiteSettings.objects.exists():
        SiteSettings.objects.create()

    if not Expedition.objects.exists():
        Expedition.objects.bulk_create(
            [
                Expedition(
                    title="Glacial Highlands",
                    slug="glacial-highlands",
                    date_label="October 2023",
                    description="Wind-cut ridgelines and slate-blue valleys above the tree line.",
                    image_url="https://images.unsplash.com/photo-1501785888041-af3ef285b470?auto=format&fit=crop&w=1400&q=80",
                    order=1,
                ),
                Expedition(
                    title="Desert Passage",
                    slug="desert-passage",
                    date_label="August 2023",
                    description="Long asphalt ribbons leading into rust and sandstone labyrinths.",
                    image_url="https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=1400&q=80",
                    order=2,
                ),
                Expedition(
                    title="City at Dawn",
                    slug="city-at-dawn",
                    date_label="May 2023",
                    description="Neon traces softening into morning fog across concrete canyons.",
                    image_url="https://images.unsplash.com/photo-1489515217757-5fd1be406fef?auto=format&fit=crop&w=1400&q=80",
                    order=3,
                ),
            ]
        )

    if not Category.objects.exists():
        Category.objects.bulk_create(
            [
                Category(
                    title="Landscapes",
                    slug="landscapes",
                    image_url="https://images.unsplash.com/photo-1441974231531-c6227db76b6e?auto=format&fit=crop&w=1400&q=80",
                    size="large",
                    order=1,
                ),
                Category(
                    title="Architecture",
                    slug="architecture",
                    image_url="https://images.unsplash.com/photo-1489515217757-5fd1be406fef?auto=format&fit=crop&w=1200&q=80",
                    size="small",
                    order=2,
                ),
                Category(
                    title="Nature",
                    slug="nature",
                    image_url="https://images.unsplash.com/photo-1500534314209-a25ddb2bd429?auto=format&fit=crop&w=1200&q=80",
                    size="small",
                    order=3,
                ),
                Category(
                    title="Travel Series",
                    slug="travel-series",
                    image_url="https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05?auto=format&fit=crop&w=1400&q=80",
                    size="wide",
                    order=4,
                ),
            ]
        )

    if not Story.objects.exists():
        Story.objects.bulk_create(
            [
                Story(
                    title="Echoes of the Mountain",
                    slug="echoes-of-the-mountain",
                    date_label="08.02.2026",
                    description="Why we climb when the world tells us to stay low.",
                    image_url="https://images.unsplash.com/photo-1469474968028-56623f02e42e?auto=format&fit=crop&w=1400&q=80",
                    order=1,
                ),
                Story(
                    title="Lost in the Fog",
                    slug="lost-in-the-fog",
                    date_label="14.01.2026",
                    description="A morning walk that turned into a journey inward.",
                    image_url="https://images.unsplash.com/photo-1482192596544-9eb780fc7f66?auto=format&fit=crop&w=1400&q=80",
                    order=2,
                ),
            ]
        )

    if not NavigationItem.objects.exists():
        NavigationItem.objects.bulk_create(
            [
                NavigationItem(
                    section="header",
                    title="Journey",
                    slug="header-journey",
                    href="#journey",
                    order=1,
                ),
                NavigationItem(
                    section="header",
                    title="Expeditions",
                    slug="header-expeditions",
                    href="#expeditions",
                    order=2,
                ),
                NavigationItem(
                    section="header",
                    title="Stories",
                    slug="header-stories",
                    href="#stories",
                    order=3,
                ),
                NavigationItem(
                    section="header",
                    title="Contact",
                    slug="header-contact",
                    href="#contact",
                    order=4,
                ),
                NavigationItem(
                    section="footer",
                    title="Expeditions",
                    slug="footer-expeditions",
                    href="#expeditions",
                    order=1,
                ),
                NavigationItem(
                    section="footer",
                    title="Journal",
                    slug="footer-journal",
                    href="#stories",
                    order=2,
                ),
                NavigationItem(
                    section="footer",
                    title="Prints",
                    slug="footer-prints",
                    href="#",
                    order=3,
                ),
                NavigationItem(
                    section="footer",
                    title="Collaborate",
                    slug="footer-collaborate",
                    href="#contact",
                    order=4,
                ),
            ]
        )

    if not SocialLink.objects.exists():
        SocialLink.objects.bulk_create(
            [
                SocialLink(
                    title="Instagram",
                    slug="instagram",
                    short_label="IG",
                    url="https://instagram.com",
                    order=1,
                ),
                SocialLink(
                    title="X",
                    slug="x",
                    short_label="X",
                    url="https://x.com",
                    order=2,
                ),
                SocialLink(
                    title="Mail",
                    slug="mail",
                    short_label="Mail",
                    url="mailto:hello@romanweiss.com",
                    order=3,
                ),
            ]
        )


def noop_reverse(apps, schema_editor):
    return None


class Migration(migrations.Migration):
    dependencies = [("content", "0001_initial")]

    operations = [migrations.RunPython(seed_content, noop_reverse)]
