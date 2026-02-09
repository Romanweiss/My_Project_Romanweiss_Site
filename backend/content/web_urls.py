from django.urls import path

from .web_views import (
    ContactSubmitView,
    ContentPageView,
    ExpeditionDetailView,
    ExpeditionsIndexView,
    HomePageView,
)

app_name = "content"

urlpatterns = [
    path("", HomePageView.as_view(), name="home"),
    path("contact/submit/", ContactSubmitView.as_view(), name="contact-submit"),
    path("expeditions/", ExpeditionsIndexView.as_view(), name="expeditions-index"),
    path(
        "expeditions/<slug:slug>/",
        ExpeditionDetailView.as_view(),
        name="expedition-detail",
    ),
    path("<slug:slug>/", ContentPageView.as_view(), name="page"),
]
