from django.urls import path
from . import admin_views

app_name = 'admin'

urlpatterns = [
    path('sample-data-management/', admin_views.sample_data_management_view, name='sample_data_management'),
]

