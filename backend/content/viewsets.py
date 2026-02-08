from django.conf import settings
from django.utils.text import slugify
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (
    Category,
    Expedition,
    Language,
    Menu,
    NavigationItem,
    Page,
    SiteSettings,
    SocialLink,
    Story,
    Translation,
    TranslationKey,
)
from .serializers import (
    CategorySerializer,
    ExpeditionSerializer,
    MenuSerializer,
    NavigationItemSerializer,
    PageSerializer,
    SiteSettingsSerializer,
    SocialLinkSerializer,
    StorySerializer,
)


def _localize_text(default_value: str, translations: dict, lang_code: str) -> str:
    if lang_code == "en":
        return default_value
    if isinstance(translations, dict):
        translated = translations.get(lang_code)
        if isinstance(translated, str) and translated.strip():
            return translated
    return default_value


def _language_by_code(code: str):
    return (
        Language.objects.filter(code=code, is_active=True)
        .order_by("order", "id")
        .first()
    )


def _active_languages():
    return Language.objects.filter(is_active=True).order_by("order", "id")


def _get_default_language():
    return _active_languages().filter(is_default=True).first() or _active_languages().first()


def _resolve_language(request):
    requested = str(request.query_params.get("lang", "")).strip().lower()
    if requested:
        language = _language_by_code(requested)
        if language:
            return language

    cookie_code = str(request.COOKIES.get("lang", "")).strip().lower()
    if cookie_code:
        language = _language_by_code(cookie_code)
        if language:
            return language

    return _get_default_language()


def _resolved_language_code(request):
    language = _resolve_language(request)
    if language:
        return language.code
    fallback = str(request.query_params.get("lang", "")).strip().lower()
    return fallback or "en"


def _set_language_cookie(response, language_code: str):
    response.set_cookie(
        key="lang",
        value=language_code,
        max_age=60 * 60 * 24 * 365,
        samesite="Lax",
        secure=not settings.DEBUG,
        httponly=False,
        path="/",
    )


def _translation_dict(language_code: str) -> dict[str, str]:
    key_records = list(
        TranslationKey.objects.filter(is_active=True).values_list("id", "key")
    )
    if not key_records:
        return {}

    key_by_id = {key_id: key for key_id, key in key_records}
    translations: dict[str, str] = {}

    current_rows = Translation.objects.filter(
        language__code=language_code,
        language__is_active=True,
        key_id__in=key_by_id,
        key__is_active=True,
    ).values_list("key_id", "text")
    for key_id, text in current_rows:
        translations[key_by_id[key_id]] = text

    default_language = _get_default_language()
    if default_language and default_language.code != language_code:
        fallback_rows = Translation.objects.filter(
            language=default_language,
            key_id__in=key_by_id,
            key__is_active=True,
        ).values_list("key_id", "text")
        for key_id, text in fallback_rows:
            translations.setdefault(key_by_id[key_id], text)

    for _, key in key_records:
        translations.setdefault(key, key)

    return translations


def _get_or_create_site_settings():
    instance = SiteSettings.objects.order_by("-updated_at").first()
    if instance is None:
        instance = SiteSettings.objects.create(brand_name="Romanweiẞ", footer_title="Romanweiẞ")
    return instance


def _get_home_page():
    queryset = (
        Page.objects.filter(is_active=True, is_published=True)
        .prefetch_related("sections__images")
        .order_by("order", "id")
    )
    return queryset.filter(is_home=True).first() or queryset.first()


def _section_token(section_key: str) -> str:
    return section_key.replace("-", "_")


def _menu_item_href(item) -> str:
    if item.href:
        return item.href
    if item.page:
        return "/" if item.page.is_home else f"/{item.page.slug}/"
    return "#"


def _menu_item_key(menu_code: str, item, position: int) -> str:
    if item.page:
        token = slugify(item.page.slug) or item.page.slug
    elif item.href.startswith("#"):
        token = slugify(item.href[1:]) or f"item_{position + 1}"
    else:
        token = slugify(item.label) or f"item_{position + 1}"

    if menu_code == "social":
        return f"social.{token}"
    if menu_code == "footer":
        return f"footer.nav.{token}"
    return f"nav.{token}"


class LocalizedSerializerContextMixin:
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["lang_code"] = _resolved_language_code(self.request)
        return context


class I18nDictionaryView(APIView):
    def get(self, request):
        lang_code = _resolved_language_code(request)
        payload = _translation_dict(lang_code)
        response = Response(payload)
        response["Content-Language"] = lang_code
        if request.query_params.get("lang"):
            _set_language_cookie(response, lang_code)
        return response


class SetLanguageView(APIView):
    def post(self, request):
        requested = str(request.data.get("lang", "")).strip().lower()
        if not requested:
            requested = str(request.query_params.get("lang", "")).strip().lower()
        language = _language_by_code(requested)
        if language is None:
            return Response(
                {"detail": "Unsupported language."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        response = Response({"lang": language.code})
        _set_language_cookie(response, language.code)
        return response


class SiteStructureView(APIView):
    def get(self, request):
        lang_code = _resolved_language_code(request)
        site_settings = _get_or_create_site_settings()
        page = _get_home_page()
        if page is None:
            return Response(
                {"detail": "No active pages are available."},
                status=status.HTTP_404_NOT_FOUND,
            )

        page_data = PageSerializer(page, context={"lang_code": lang_code}).data
        menus = (
            Menu.objects.filter(is_published=True)
            .prefetch_related("items__page")
            .order_by("order", "id")
        )

        menu_payload: dict[str, list[dict]] = {"main": [], "footer": [], "social": []}
        for menu in menus:
            normalized_code = menu.code if menu.code in menu_payload else menu.code
            items = [item for item in menu.items.all() if item.is_published]
            items.sort(key=lambda item: (item.order, item.id))

            serialized_items = []
            for index, item in enumerate(items):
                serialized_items.append(
                    {
                        "id": item.id,
                        "href": _menu_item_href(item),
                        "label": _localize_text(item.label, item.label_i18n, lang_code),
                        "label_key": _menu_item_key(menu.code, item, index),
                        "open_in_new_tab": item.open_in_new_tab,
                    }
                )

            if normalized_code in menu_payload:
                menu_payload[normalized_code] = serialized_items
            else:
                menu_payload[normalized_code] = serialized_items

        section_payload = []
        for section in page_data.get("sections", []):
            token = _section_token(section["key"])
            anchor = "journey" if section["key"] == "hero" else section["key"]
            payload_keys = {}
            payload = section.get("payload") if isinstance(section.get("payload"), dict) else {}
            for field in ("kicker", "scroll_label", "eyebrow", "title", "subtitle", "action_label"):
                if isinstance(payload.get(field), str):
                    payload_keys[field] = f"section.{token}.{field}"

            section_payload.append(
                {
                    "id": section["id"],
                    "key": section["key"],
                    "anchor": anchor,
                    "section_type": section["section_type"],
                    "title": section.get("title", ""),
                    "title_key": f"section.{token}.title",
                    "subtitle": section.get("subtitle", ""),
                    "subtitle_key": f"section.{token}.subtitle",
                    "body": section.get("body", ""),
                    "body_key": f"section.{token}.body",
                    "payload": payload,
                    "payload_keys": payload_keys,
                    "images": section.get("images", []),
                }
            )

        pages = list(
            Page.objects.filter(is_active=True)
            .order_by("order", "id")
            .values("slug", "is_active", "order")
        )

        languages = list(
            _active_languages().values(
                "code",
                "name",
                "is_default",
                "order",
            )
        )

        response = Response(
            {
                "lang": lang_code,
                "languages": languages,
                "site": {
                    "brand_name": _localize_text(
                        site_settings.brand_name, site_settings.brand_name_i18n, lang_code
                    ),
                    "brand_key": "brand.name",
                    "footer_title": _localize_text(
                        site_settings.footer_title, site_settings.footer_title_i18n, lang_code
                    ),
                    "footer_title_key": "footer.title",
                    "footer_description": _localize_text(
                        site_settings.footer_description,
                        site_settings.footer_description_i18n,
                        lang_code,
                    ),
                    "footer_description_key": "footer.description",
                    "footer_explore_title": _localize_text(
                        site_settings.footer_explore_title,
                        site_settings.footer_explore_title_i18n,
                        lang_code,
                    ),
                    "footer_explore_title_key": "footer.explore",
                    "footer_social_title": _localize_text(
                        site_settings.footer_social_title,
                        site_settings.footer_social_title_i18n,
                        lang_code,
                    ),
                    "footer_social_title_key": "footer.social",
                    "footer_newsletter_title": _localize_text(
                        site_settings.footer_newsletter_title,
                        site_settings.footer_newsletter_title_i18n,
                        lang_code,
                    ),
                    "footer_newsletter_title_key": "footer.newsletter",
                    "newsletter_note": _localize_text(
                        site_settings.newsletter_note,
                        site_settings.newsletter_note_i18n,
                        lang_code,
                    ),
                    "newsletter_note_key": "footer.newsletter_note",
                    "contact_email": site_settings.contact_email,
                },
                "pages": pages,
                "menus": menu_payload,
                "sections": section_payload,
            }
        )
        response["Content-Language"] = lang_code
        if request.query_params.get("lang"):
            _set_language_cookie(response, lang_code)
        return response


class SiteBootstrapView(APIView):
    def get(self, request):
        lang_code = _resolved_language_code(request)
        site_settings = _get_or_create_site_settings()
        page = _get_home_page()
        if page is None:
            return Response(
                {"detail": "No active pages are available."},
                status=status.HTTP_404_NOT_FOUND,
            )

        menus = (
            Menu.objects.filter(is_published=True)
            .prefetch_related("items__page")
            .order_by("order", "id")
        )

        return Response(
            {
                "lang": lang_code,
                "site": SiteSettingsSerializer(
                    site_settings, context={"request": request, "lang_code": lang_code}
                ).data,
                "page": PageSerializer(
                    page, context={"request": request, "lang_code": lang_code}
                ).data,
                "menus": MenuSerializer(
                    menus,
                    many=True,
                    context={"request": request, "lang_code": lang_code},
                ).data,
            }
        )


class SiteSettingsDetailView(APIView):
    def get(self, request):
        lang_code = _resolved_language_code(request)
        instance = _get_or_create_site_settings()
        return Response(
            SiteSettingsSerializer(
                instance, context={"request": request, "lang_code": lang_code}
            ).data
        )


class MenuDetailView(APIView):
    def get(self, request, code):
        lang_code = _resolved_language_code(request)
        menu = (
            Menu.objects.filter(code=code, is_published=True)
            .prefetch_related("items__page")
            .first()
        )
        if menu is None:
            return Response(
                {"detail": "Menu not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(
            MenuSerializer(menu, context={"request": request, "lang_code": lang_code}).data
        )


class PageViewSet(LocalizedSerializerContextMixin, viewsets.ReadOnlyModelViewSet):
    serializer_class = PageSerializer
    lookup_field = "slug"
    pagination_class = None

    def get_queryset(self):
        queryset = (
            Page.objects.filter(is_active=True, is_published=True)
            .prefetch_related("sections__images")
            .order_by("order", "id")
        )
        is_home = self.request.query_params.get("is_home")
        if is_home is not None:
            is_home_value = is_home.lower() in {"1", "true", "yes"}
            queryset = queryset.filter(is_home=is_home_value)
        return queryset


class SiteSettingsViewSet(LocalizedSerializerContextMixin, viewsets.ReadOnlyModelViewSet):
    serializer_class = SiteSettingsSerializer
    queryset = SiteSettings.objects.order_by("-updated_at")
    pagination_class = None

    def list(self, request, *args, **kwargs):
        instance = self.get_queryset().first()
        if instance is None:
            instance = SiteSettings.objects.create(brand_name="Romanweiẞ", footer_title="Romanweiẞ")
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CategorySerializer
    queryset = Category.objects.filter(is_published=True).order_by("order", "id")
    pagination_class = None


class ExpeditionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ExpeditionSerializer
    queryset = Expedition.objects.filter(is_published=True).order_by("order", "id")
    pagination_class = None


class StoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = StorySerializer
    queryset = Story.objects.filter(is_published=True).order_by("order", "id")
    pagination_class = None


class NavigationItemViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = NavigationItemSerializer
    pagination_class = None

    def get_queryset(self):
        queryset = NavigationItem.objects.filter(is_published=True).order_by(
            "section", "order", "id"
        )
        section = self.request.query_params.get("section")
        if section:
            queryset = queryset.filter(section=section)
        return queryset


class SocialLinkViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = SocialLinkSerializer
    queryset = SocialLink.objects.filter(is_published=True).order_by("order", "id")
    pagination_class = None
