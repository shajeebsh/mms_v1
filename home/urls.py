from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

app_name = 'home'

urlpatterns = [
    path('export/<str:report_type>/', views.export_report_view, name='export_report'),
    path('api/live-data/', views.live_data_feed, name='live_data_feed'),
]