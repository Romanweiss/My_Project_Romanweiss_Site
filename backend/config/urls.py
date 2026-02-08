from django.contrib import admin
from django.urls import path
from api.views import create_contact_message, health, site_content

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/health/", health),
    path("api/site-content/", site_content),
    path("api/contact-messages/", create_contact_message),
]
