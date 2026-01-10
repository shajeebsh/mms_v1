from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db.models import Sum

from .models import StudentEnrollment


@method_decorator(login_required, name='dispatch')
class PendingFeesReportView(TemplateView):
    template_name = "education/pending_fees_report.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Filter for pending or partial payments where course fee > 0
        enrollments = StudentEnrollment.objects.filter(
            payment_status__in=['pending', 'partial'],
            class_instance__course_fee__gt=0
        ).select_related('student', 'class_instance').order_by('class_instance__name', 'student__first_name')

        # Calculate total pending amount
        total_pending = 0
        enrollment_data = []

        for enrollment in enrollments:
            # Refresh payment status to be sure (optional, but safer if signals fail silently)
            # enrollment.update_payment_status() 
            # Skipping update_payment_status() on read for performance, assuming signals work.
            
            balance = enrollment.balance_amount
            if balance > 0:
                total_pending += balance
                enrollment_data.append(enrollment)

        context['enrollments'] = enrollment_data
        context['total_students'] = len(enrollment_data)
        context['total_pending_amount'] = total_pending
        
        return context
