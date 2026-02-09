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
    MenuItem,
    NavigationItem,
    Page,
    SiteSettings,
    SiteText,
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


def _localize_text(default_value: str, translations: dict, lang_code: str, fallback_lang: str) -> str:
    if isinstance(translations, dict):
        translated = translations.get(lang_code)
        if isinstance(translated, str) and translated.strip():
            return translated

    if isinstance(default_value, str) and default_value.strip():
        return default_value

    if isinstance(translations, dict):
        fallback_value = translations.get(fallback_lang)
        if isinstance(fallback_value, str) and fallback_value.strip():
            return fallback_value

    return default_value if isinstance(default_value, str) else ""


def _language_by_code(code: str):
    return (
        Language.objects.filter(code=code, is_active=True)
        .order_by("order", "id")
        .first()
    )


def _active_languages():
    return Language.objects.filter(is_active=True).order_by("order", "id")


def _get_default_language():
    languages = _active_languages()
    return (
        languages.filter(code="en").first()
        or languages.filter(is_default=True).first()
        or languages.first()
    )


def _default_language_code() -> str:
    default_language = _get_default_language()
    if default_language:
        return default_language.code
    return "en"


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
    return fallback or _default_language_code()


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


def _legacy_translation_dict(language_code: str, fallback_lang: str) -> dict[str, str]:
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

    if fallback_lang != language_code:
        fallback_rows = Translation.objects.filter(
            language__code=fallback_lang,
            language__is_active=True,
            key_id__in=key_by_id,
            key__is_active=True,
        ).values_list("key_id", "text")
        for key_id, text in fallback_rows:
            translations.setdefault(key_by_id[key_id], text)

    for _, key in key_records:
        translations.setdefault(key, key)

    return translations


def _site_text_dict(language_code: str, fallback_lang: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for site_text in SiteText.objects.filter(is_published=True).order_by("group", "order", "key"):
        values[site_text.key] = _localize_text(
            site_text.text,
            site_text.text_i18n,
            language_code,
            fallback_lang,
        )

    if values:
        return values

    return _legacy_translation_dict(language_code, fallback_lang)


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


def _menu_item_key(menu_code: str, token: str) -> str:
    slug_token = token.replace("-", "_")
    if menu_code == "social":
        return f"social.{slug_token}"
    if menu_code == "footer":
        return f"footer.nav.{slug_token}"
    return f"nav.{slug_token}"


def _navigation_payload(lang_code: str, fallback_lang: str, menu_code: str | None = None):
    menus: dict[str, list[dict]] = {"main": [], "footer": [], "social": []}

    queryset = (
        NavigationItem.objects.filter(is_published=True)
        .select_related("page")
        .order_by("menu", "order", "id")
    )
    if menu_code:
        queryset = queryset.filter(menu=menu_code)

    serialized_items = NavigationItemSerializer(
        queryset,
        many=True,
        context={"lang_code": lang_code, "fallback_lang": fallback_lang},
    ).data
    for item in serialized_items:
        menu = item.get("menu") or "main"
        menus.setdefault(menu, []).append(item)

    requested_menus = [menu_code] if menu_code else [key for key, items in menus.items() if not items]
    if requested_menus:
        fallback_items = (
            MenuItem.objects.filter(
                is_published=True,
                menu__is_published=True,
                menu__code__in=requested_menus,
            )
            .select_related("menu", "page")
            .order_by("menu__order", "order", "id")
        )

        for item in fallback_items:
            fallback_href = item.href or ("/" if item.page and item.page.is_home else "")
            if item.page and not fallback_href:
                fallback_href = f"/{item.page.slug}/"

            token_base = (
                item.page.slug
                if item.page
                else (fallback_href.lstrip("/#") or item.label or f"item-{item.id}")
            )
            token = slugify(token_base) or f"item_{item.id}"
            menu = item.menu.code
            label = _localize_text(item.label, item.label_i18n, lang_code, fallback_lang)
            kind = "anchor" if fallback_href.startswith("#") or fallback_href.startswith("/#") else "page"
            if fallback_href.startswith("http://") or fallback_href.startswith("https://") or fallback_href.startswith("mailto:"):
                kind = "external"

            menus.setdefault(menu, []).append(
                {
                    "id": item.id,
                    "menu": menu,
                    "section": "footer" if menu in {"footer", "social"} else "header",
                    "slug": slugify(item.label) or f"item-{item.id}",
                    "url_key": token if kind == "anchor" else "",
                    "label": label,
                    "label_key": _menu_item_key(menu, token),
                    "kind": kind,
                    "href": fallback_href or "#",
                    "page_slug": item.page.slug if item.page else None,
                    "open_in_new_tab": item.open_in_new_tab,
                    "order": item.order,
                    "is_published": item.is_published,
                }
            )

    if menu_code:
        return {menu_code: menus.get(menu_code, [])}
    return menus


class LocalizedSerializerContextMixin:
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["lang_code"] = _resolved_language_code(self.request)
        context["fallback_lang"] = _default_language_code()
        return context


class I18nDictionaryView(APIView):
    def get(self, request):
        lang_code = _resolved_language_code(request)
        fallback_lang = _default_language_code()
        payload = _site_text_dict(lang_code, fallback_lang)
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


class ContentView(APIView):
    def get(self, request):
        lang_code = _resolved_language_code(request)
        fallback_lang = _default_language_code()
        site_settings = _get_or_create_site_settings()

        pages = Page.objects.filter(is_active=True, is_published=True).order_by("order", "id")
        page_payload = [
            {
                "slug": page.slug,
                "title": _localize_text(page.title, page.title_i18n, lang_code, fallback_lang),
                "is_home": page.is_home,
                "order": page.order,
            }
            for page in pages
        ]

        payload = {
            "lang": lang_code,
            "default_lang": fallback_lang,
            "languages": list(
                _active_languages().values(
                    "code",
                    "name",
                    "is_default",
                    "order",
                )
            ),
            "site": SiteSettingsSerializer(
                site_settings,
                context={"lang_code": lang_code, "fallback_lang": fallback_lang},
            ).data,
            "texts": _site_text_dict(lang_code, fallback_lang),
            "pages": page_payload,
        }

        response = Response(payload)
        response["Content-Language"] = lang_code
        if request.query_params.get("lang"):
            _set_language_cookie(response, lang_code)
        return response


class NavigationView(APIView):
    def get(self, request):
        lang_code = _resolved_language_code(request)
        fallback_lang = _default_language_code()
        menu_code = str(request.query_params.get("menu", "")).strip().lower() or None
        payload = _navigation_payload(lang_code, fallback_lang, menu_code)

        response = Response({"lang": lang_code, "menus": payload})
        response["Content-Language"] = lang_code
        if request.query_params.get("lang"):
            _set_language_cookie(response, lang_code)
        return response


class PageDetailView(APIView):
    def get(self, request, slug):
        lang_code = _resolved_language_code(request)
        fallback_lang = _default_language_code()

        queryset = (
            Page.objects.filter(is_active=True, is_published=True)
            .prefetch_related("sections__images")
            .order_by("order", "id")
        )
        page = queryset.filter(slug=slug).first()

        if page is None and slug == "home":
            page = queryset.filter(is_home=True).first() or queryset.first()

        if page is None:
            return Response(
                {"detail": "Page not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        payload = {
            "lang": lang_code,
            "page": PageSerializer(
                page,
                context={"lang_code": lang_code, "fallback_lang": fallback_lang},
            ).data,
        }
        response = Response(payload)
        response["Content-Language"] = lang_code
        if request.query_params.get("lang"):
            _set_language_cookie(response, lang_code)
        return response


class SiteStructureView(APIView):
    def get(self, request):
        lang_code = _resolved_language_code(request)
        fallback_lang = _default_language_code()
        site_settings = _get_or_create_site_settings()
        page = _get_home_page()
        if page is None:
            return Response(
                {"detail": "No active pages are available."},
                status=status.HTTP_404_NOT_FOUND,
            )

        page_data = PageSerializer(
            page,
            context={"lang_code": lang_code, "fallback_lang": fallback_lang},
        ).data

        section_payload = []
        for section in page_data.get("sections", []):
            token = section["key"].replace("-", "_")
            payload = section.get("payload") if isinstance(section.get("payload"), dict) else {}
            payload_keys = {}
            for field, value in payload.items():
                if isinstance(value, str):
                    payload_keys[field] = f"section.{token}.{field}"

            section_payload.append(
                {
                    "id": section["id"],
                    "key": section["key"],
                    "anchor": section.get("anchor") or section["key"],
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

        response = Response(
            {
                "lang": lang_code,
                "languages": list(
                    _active_languages().values(
                        "code",
                        "name",
                        "is_default",
                        "order",
                    )
                ),
                "site": {
                    "brand_name": _localize_text(
                        site_settings.brand_name,
                        site_settings.brand_name_i18n,
                        lang_code,
                        fallback_lang,
                    ),
                    "brand_key": "brand.name",
                    "footer_title": _localize_text(
                        site_settings.footer_title,
                        site_settings.footer_title_i18n,
                        lang_code,
                        fallback_lang,
                    ),
                    "footer_title_key": "footer.title",
                    "footer_description": _localize_text(
                        site_settings.footer_description,
                        site_settings.footer_description_i18n,
                        lang_code,
                        fallback_lang,
                    ),
                    "footer_description_key": "footer.description",
                    "footer_explore_title": _localize_text(
                        site_settings.footer_explore_title,
                        site_settings.footer_explore_title_i18n,
                        lang_code,
                        fallback_lang,
                    ),
                    "footer_explore_title_key": "footer.explore",
                    "footer_social_title": _localize_text(
                        site_settings.footer_social_title,
                        site_settings.footer_social_title_i18n,
                        lang_code,
                        fallback_lang,
                    ),
                    "footer_social_title_key": "footer.social",
                    "footer_newsletter_title": _localize_text(
                        site_settings.footer_newsletter_title,
                        site_settings.footer_newsletter_title_i18n,
                        lang_code,
                        fallback_lang,
                    ),
                    "footer_newsletter_title_key": "footer.newsletter",
                    "newsletter_note": _localize_text(
                        site_settings.newsletter_note,
                        site_settings.newsletter_note_i18n,
                        lang_code,
                        fallback_lang,
                    ),
                    "newsletter_note_key": "footer.newsletter_note",
                    "contact_email": site_settings.contact_email,
                },
                "pages": list(
                    Page.objects.filter(is_active=True)
                    .order_by("order", "id")
                    .values("slug", "is_active", "order")
                ),
                "menus": _navigation_payload(lang_code, fallback_lang),
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
        fallback_lang = _default_language_code()
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
                    site_settings,
                    context={"lang_code": lang_code, "fallback_lang": fallback_lang},
                ).data,
                "page": PageSerializer(
                    page,
                    context={"lang_code": lang_code, "fallback_lang": fallback_lang},
                ).data,
                "menus": MenuSerializer(
                    menus,
                    many=True,
                    context={"lang_code": lang_code, "fallback_lang": fallback_lang},
                ).data,
            }
        )


class SiteSettingsDetailView(APIView):
    def get(self, request):
        lang_code = _resolved_language_code(request)
        fallback_lang = _default_language_code()
        instance = _get_or_create_site_settings()
        return Response(
            SiteSettingsSerializer(
                instance,
                context={"lang_code": lang_code, "fallback_lang": fallback_lang},
            ).data
        )


class MenuDetailView(APIView):
    def get(self, request, code):
        lang_code = _resolved_language_code(request)
        fallback_lang = _default_language_code()
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
            MenuSerializer(
                menu,
                context={"lang_code": lang_code, "fallback_lang": fallback_lang},
            ).data
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


class StoryViewSet(LocalizedSerializerContextMixin, viewsets.ReadOnlyModelViewSet):
    serializer_class = StorySerializer
    queryset = Story.objects.filter(is_published=True).order_by("order", "id")
    pagination_class = None


class NavigationItemViewSet(LocalizedSerializerContextMixin, viewsets.ReadOnlyModelViewSet):
    serializer_class = NavigationItemSerializer
    pagination_class = None

    def get_queryset(self):
        queryset = (
            NavigationItem.objects.filter(is_published=True)
            .select_related("page")
            .order_by("menu", "order", "id")
        )
        menu = self.request.query_params.get("menu")
        if menu:
            queryset = queryset.filter(menu=menu)
        section = self.request.query_params.get("section")
        if section:
            queryset = queryset.filter(section=section)
        return queryset


class SocialLinkViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = SocialLinkSerializer
    queryset = SocialLink.objects.filter(is_published=True).order_by("order", "id")
    pagination_class = None
