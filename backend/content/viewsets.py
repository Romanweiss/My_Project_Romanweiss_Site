from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (
    Category,
    Expedition,
    Menu,
    NavigationItem,
    Page,
    SiteSettings,
    SocialLink,
    Story,
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


def _get_or_create_site_settings():
    instance = SiteSettings.objects.order_by("-updated_at").first()
    if instance is None:
        instance = SiteSettings.objects.create()
    return instance


def _get_home_page():
    queryset = (
        Page.objects.filter(is_published=True)
        .prefetch_related("sections__images")
        .order_by("order", "id")
    )
    return queryset.filter(is_home=True).first() or queryset.first()


class SiteBootstrapView(APIView):
    def get(self, request):
        site_settings = _get_or_create_site_settings()
        page = _get_home_page()
        if page is None:
            return Response(
                {"detail": "No published pages are available."},
                status=status.HTTP_404_NOT_FOUND,
            )

        menus = (
            Menu.objects.filter(is_published=True)
            .prefetch_related("items__page")
            .order_by("order", "id")
        )

        return Response(
            {
                "site": SiteSettingsSerializer(site_settings).data,
                "page": PageSerializer(page).data,
                "menus": MenuSerializer(menus, many=True).data,
            }
        )


class SiteSettingsDetailView(APIView):
    def get(self, request):
        instance = _get_or_create_site_settings()
        return Response(SiteSettingsSerializer(instance).data)


class MenuDetailView(APIView):
    def get(self, request, code):
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
        return Response(MenuSerializer(menu).data)


class PageViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PageSerializer
    lookup_field = "slug"
    pagination_class = None

    def get_queryset(self):
        queryset = (
            Page.objects.filter(is_published=True)
            .prefetch_related("sections__images")
            .order_by("order", "id")
        )
        is_home = self.request.query_params.get("is_home")
        if is_home is not None:
            is_home_value = is_home.lower() in {"1", "true", "yes"}
            queryset = queryset.filter(is_home=is_home_value)
        return queryset


class SiteSettingsViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = SiteSettingsSerializer
    queryset = SiteSettings.objects.order_by("-updated_at")
    pagination_class = None

    def list(self, request, *args, **kwargs):
        instance = self.get_queryset().first()
        if instance is None:
            instance = SiteSettings.objects.create()
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
