from django.urls import path
from . import views

app_name = 'membership'

urlpatterns = [
    path('bulk-payment/', views.bulk_payment_view, name='bulk_payment'),
    path('overdue-report/', views.overdue_report_view, name='overdue_report'),
    path('generate-monthly-dues/', views.generate_monthly_dues_view, name='generate_monthly_dues'),
    path('download-questionnaire/', views.download_questionnaire_view, name='download_questionnaire'),
    path('preview-questionnaire/', views.preview_questionnaire_view, name='preview_questionnaire'),
    path('print-card/<int:member_id>/', views.print_membership_card_view, name='print_membership_card'),
    path('preview-card/<int:member_id>/', views.preview_membership_card_view, name='preview_membership_card'),
]