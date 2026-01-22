from django.urls import path
from . import admin_views

app_name = 'home_admin'

urlpatterns = [
    path('sample-data-management/', admin_views.sample_data_management_view, name='sample_data_management'),
    path('data-profiling/', admin_views.data_profiling_view, name='data_profiling'),
]

