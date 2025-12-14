from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("django-admin/", admin.site.urls),
    path("cms/", include("wagtail.admin.urls")),
    path("documents/", include("wagtail.documents.urls")),
    path("membership/", include("membership.urls")),
    path("", include("home.urls")),
    path("", include("wagtail.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
