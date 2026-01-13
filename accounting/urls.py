from django.urls import path

from . import views

app_name = 'accounting'

urlpatterns = [
    path('chart-of-accounts/', views.chart_of_accounts_view, name='chart_of_accounts'),
]
