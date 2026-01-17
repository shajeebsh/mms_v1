from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

from .models import StudentEnrollment, StudentFeePayment, Class


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


@login_required
def record_fee_payment_view(request, enrollment_id=None):
    """View to record a fee payment for a student enrollment"""
    enrollment = None
    if enrollment_id:
        enrollment = get_object_or_404(
            StudentEnrollment.objects.select_related('student', 'class_instance'),
            id=enrollment_id
        )
    
    if request.method == "POST":
        enrollment_id_post = request.POST.get("enrollment_id")
        amount = request.POST.get("amount")
        payment_date = request.POST.get("payment_date")
        payment_method = request.POST.get("payment_method")
        reference_number = request.POST.get("reference_number", "")
        remarks = request.POST.get("remarks", "")

        if not enrollment_id_post:
            messages.error(request, "Please select a student enrollment.")
            return redirect("education_record_fee_payment")

        try:
            enrollment = get_object_or_404(StudentEnrollment, id=enrollment_id_post)
            amount_decimal = Decimal(amount)

            if amount_decimal <= 0:
                messages.error(request, "Payment amount must be greater than zero.")
                return redirect("education_record_fee_payment_for", enrollment_id=enrollment_id_post)

            with transaction.atomic():
                payment = StudentFeePayment.objects.create(
                    enrollment=enrollment,
                    amount=amount_decimal,
                    date=payment_date or timezone.now().date(),
                    payment_method=payment_method,
                    reference_number=reference_number,
                    remarks=remarks
                )

                messages.success(
                    request,
                    f"Payment of ₹{amount_decimal} recorded successfully for {enrollment.student.full_name}!"
                )

            return redirect("education_payment_history", enrollment_id=enrollment.id)

        except (ValueError, TypeError) as e:
            messages.error(request, f"Invalid input: {str(e)}")
        except Exception as e:
            messages.error(request, f"Error recording payment: {str(e)}")
        
        if enrollment:
            return redirect("education_record_fee_payment_for", enrollment_id=enrollment.id)
        return redirect("education_record_fee_payment")

    # GET request - show form
    enrollments_with_pending = StudentEnrollment.objects.filter(
        payment_status__in=['pending', 'partial'],
        class_instance__course_fee__gt=0
    ).select_related('student', 'class_instance').order_by('student__first_name')

    context = {
        "enrollment": enrollment,
        "enrollments": enrollments_with_pending,
        "payment_methods": StudentFeePayment.PAYMENT_METHODS,
        "today": timezone.now().date(),
    }
    return render(request, "education/record_fee_payment.html", context)


@login_required
def payment_history_view(request, enrollment_id):
    """View to show payment history for an enrollment"""
    enrollment = get_object_or_404(
        StudentEnrollment.objects.select_related('student', 'class_instance'),
        id=enrollment_id
    )
    payments = enrollment.payments.all().order_by('-date', '-created_at')

    context = {
        "enrollment": enrollment,
        "payments": payments,
        "total_paid": enrollment.total_paid,
        "balance": enrollment.balance_amount,
        "course_fee": enrollment.class_instance.course_fee,
    }
    return render(request, "education/payment_history.html", context)


@login_required
def all_payments_view(request):
    """View to show all fee payments with filtering"""
    class_filter = request.GET.get('class_id')
    status_filter = request.GET.get('status')
    
    payments = StudentFeePayment.objects.select_related(
        'enrollment__student', 'enrollment__class_instance'
    ).order_by('-date', '-created_at')

    if class_filter:
        payments = payments.filter(enrollment__class_instance_id=class_filter)

    if status_filter:
        payments = payments.filter(enrollment__payment_status=status_filter)

    # Calculate totals
    total_collected = payments.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

    classes = Class.objects.filter(is_active=True).order_by('name')

    context = {
        "payments": payments[:100],  # Limit to recent 100 payments
        "total_collected": total_collected,
        "classes": classes,
        "selected_class": class_filter,
        "selected_status": status_filter,
        "payment_statuses": StudentEnrollment.ENROLLMENT_STATUS,
    }
    return render(request, "education/all_payments.html", context)
