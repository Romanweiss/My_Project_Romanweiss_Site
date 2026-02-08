from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import Category, ContactMessage, Expedition, SiteContent, Story

@api_view(["GET"])
def health(request):
    return Response({"status": "ok"})


def _site_defaults():
    return {
        "brand_name": "Romanweiss",
        "hero_kicker": "Travel & Expedition Photography",
        "hero_title": "Romanweiss",
        "hero_subtitle": "Exploring landscapes, architecture, and the distance between moments.",
        "hero_background_image": "https://images.unsplash.com/photo-1469474968028-56623f02e42e?auto=format&fit=crop&w=2000&q=80",
        "journal_intro": (
            "We travel not to escape life, but for life not to escape us. "
            "This journal is a collection of moments from the road - a visual diary of silence, texture, and light."
        ),
        "contact_title": "Get in touch",
        "contact_description": (
            "Interested in a collaboration, a print, or just want to say hello? "
            "I am always open to discussing new projects and creative opportunities."
        ),
        "contact_location": "Berlin, Germany",
        "contact_email": "hello@romanweiss.com",
        "contact_socials": "Instagram · Behance · Vimeo",
        "footer_title": "Romanweiss",
        "footer_description": (
            "Capturing the silence of remote places, the texture of the wind, and "
            "the stories found in distance."
        ),
        "newsletter_note": "Updates from the road, once a month.",
    }


@api_view(["GET"])
def site_content(request):
    site = SiteContent.objects.order_by("-updated_at").first()
    site_payload = _site_defaults()

    if site:
        site_payload = {
            "brand_name": site.brand_name,
            "hero_kicker": site.hero_kicker,
            "hero_title": site.hero_title,
            "hero_subtitle": site.hero_subtitle,
            "hero_background_image": site.hero_background_image,
            "journal_intro": site.journal_intro,
            "contact_title": site.contact_title,
            "contact_description": site.contact_description,
            "contact_location": site.contact_location,
            "contact_email": site.contact_email,
            "contact_socials": site.contact_socials,
            "footer_title": site.footer_title,
            "footer_description": site.footer_description,
            "newsletter_note": site.newsletter_note,
        }

    expeditions = list(
        Expedition.objects.filter(is_published=True)
        .values("title", "date_label", "description", "image_url")
        .order_by("order", "id")
    )
    categories = list(
        Category.objects.filter(is_published=True)
        .values("title", "image_url", "size")
        .order_by("order", "id")
    )
    stories = list(
        Story.objects.filter(is_published=True)
        .values("title", "date_label", "description", "image_url")
        .order_by("order", "id")
    )

    return Response(
        {
            "site": site_payload,
            "expeditions": expeditions,
            "categories": categories,
            "stories": stories,
        }
    )


@api_view(["POST"])
def create_contact_message(request):
    name = str(request.data.get("name", "")).strip()
    email = str(request.data.get("email", "")).strip()
    message = str(request.data.get("message", "")).strip()

    if not name or not email or not message:
        return Response(
            {"detail": "Name, email, and message are required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        validate_email(email)
    except ValidationError:
        return Response(
            {"detail": "Invalid email address."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    saved_message = ContactMessage.objects.create(
        name=name,
        email=email,
        message=message,
    )
    return Response(
        {"status": "received", "id": saved_message.id},
        status=status.HTTP_201_CREATED,
    )
