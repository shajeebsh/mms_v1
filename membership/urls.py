from django.urls import path
from . import views

app_name = 'membership'

urlpatterns = [
    path('bulk-payment/', views.bulk_payment_view, name='bulk_payment'),
    path('overdue-report/', views.overdue_report_view, name='overdue_report'),
    path('generate-monthly-dues/', views.generate_monthly_dues_view, name='generate_monthly_dues'),
]