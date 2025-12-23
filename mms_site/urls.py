from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from home.views import (
    redirect_finance_donation_create,
    redirect_finance_expense_create,
    redirect_finance_reports,
    wagtail_dashboard_view,
)

urlpatterns = [
    path("django-admin/", admin.site.urls),
    path("cms/", wagtail_dashboard_view, name='wagtailadmin_home'),
    path("cms/", include("wagtail.admin.urls")),
    path("cms/admin/", include("home.admin_urls")),  # Custom admin views
    path("documents/", include("wagtail.documents.urls")),
    path("membership/", include("membership.urls")),
    # Redirect legacy frontend finance URLs to the Wagtail ModelAdmin pages
    path('finance/donation/create/', redirect_finance_donation_create),
    path('finance/expense/create/', redirect_finance_expense_create),
    path('finance/reports/', redirect_finance_reports),
    path("", include("home.urls")),
    path("hr/", include("hr.urls")),
    path("committee/", include("committee.urls")),
    path("", include("wagtail.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
