from django.urls import path
from rest_framework.routers import DefaultRouter

from .viewsets import (
    CategoryViewSet,
    ExpeditionViewSet,
    MenuDetailView,
    NavigationItemViewSet,
    PageViewSet,
    SiteBootstrapView,
    SiteSettingsDetailView,
    SiteSettingsViewSet,
    SocialLinkViewSet,
    StoryViewSet,
)

legacy_router = DefaultRouter()
legacy_router.register("settings", SiteSettingsViewSet, basename="settings")
legacy_router.register("categories", CategoryViewSet, basename="categories")
legacy_router.register("expeditions", ExpeditionViewSet, basename="expeditions")
legacy_router.register("stories", StoryViewSet, basename="stories")
legacy_router.register("navigation", NavigationItemViewSet, basename="navigation")
legacy_router.register("social-links", SocialLinkViewSet, basename="social-links")

v1_router = DefaultRouter()
v1_router.register("v1/pages", PageViewSet, basename="v1-pages")

urlpatterns = [
    path("v1/site/", SiteSettingsDetailView.as_view(), name="v1-site"),
    path("v1/bootstrap/", SiteBootstrapView.as_view(), name="v1-bootstrap"),
    path("v1/menus/<slug:code>/", MenuDetailView.as_view(), name="v1-menu-detail"),
]
urlpatterns += v1_router.urls
urlpatterns += legacy_router.urls
