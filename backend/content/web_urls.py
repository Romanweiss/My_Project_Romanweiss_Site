from django.urls import path

from .web_views import ContactSubmitView, ContentPageView, HomePageView

app_name = "content"

urlpatterns = [
    path("", HomePageView.as_view(), name="home"),
    path("contact/submit/", ContactSubmitView.as_view(), name="contact-submit"),
    path("<slug:slug>/", ContentPageView.as_view(), name="page"),
]
