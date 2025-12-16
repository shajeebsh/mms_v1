from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

app_name = 'home'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('portal/', views.portal_view, name='portal'),
    path('export/<str:report_type>/', views.export_report_view, name='export_report'),
    path('api/live-data/', views.live_data_feed, name='live_data_feed'),
]