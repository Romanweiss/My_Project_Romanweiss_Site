from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from api.views import create_contact_message, health

urlpatterns = [
    path("admin/", admin.site.urls),
    path("i18n/", include("django.conf.urls.i18n")),
    path("api/health/", health),
    path("api/v1/health/", health),
    path("api/contact-messages/", create_contact_message),
    path("api/v1/contact-messages/", create_contact_message),
    path("api/", include("content.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
