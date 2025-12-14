from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from django.db.models import Sum, Q
from decimal import Decimal
from .models import Family, MembershipDues, Payment


def bulk_payment_view(request):
    """View for bulk payment processing"""
    if request.method == 'POST':
        family_ids = request.POST.getlist('family_ids')
        payment_method = request.POST.get('payment_method')
        payment_date = request.POST.get('payment_date')
        notes = request.POST.get('notes', '')

        if not family_ids:
            messages.error(request, 'Please select at least one family.')
            return redirect('bulk_payment')

        if not payment_method:
            messages.error(request, 'Please select a payment method.')
            return redirect('bulk_payment')

        try:
            with transaction.atomic():
                total_amount = Decimal('0.00')
                selected_dues = []

                # Calculate total amount and collect dues for selected families
                for family_id in family_ids:
                    family = get_object_or_404(Family, id=family_id)
                    # Get unpaid dues for this family
                    dues = MembershipDues.objects.filter(
                        family=family,
                        is_paid=False
                    ).order_by('year', 'month')

                    if dues.exists():
                        selected_dues.extend(dues)
                        total_amount += sum(due.amount_due for due in dues)

                if not selected_dues:
                    messages.warning(request, 'No unpaid dues found for selected families.')
                    return redirect('bulk_payment')

                # Create payment record
                payment = Payment.objects.create(
                    family=Family.objects.filter(id__in=family_ids).first(),  # Use first family as reference
                    amount=total_amount,
                    payment_method=payment_method,
                    payment_date=payment_date or timezone.now().date(),
                    notes=f"Bulk payment for {len(family_ids)} families - {notes}"
                )

                # Associate dues with payment and mark as paid
                for due in selected_dues:
                    payment.membership_dues.add(due)
                    due.is_paid = True
                    due.save()

                messages.success(request, f'Bulk payment processed successfully! Receipt #{payment.receipt_number} for ₹{total_amount}')

        except Exception as e:
            messages.error(request, f'Error processing payment: {str(e)}')

        return redirect('bulk_payment')

    # GET request - show form
    # Get families with unpaid dues
    families_with_dues = Family.objects.filter(
        membership_dues__is_paid=False
    ).distinct().order_by('name')

    context = {
        'families': families_with_dues,
        'payment_methods': Payment.PAYMENT_METHOD_CHOICES,
    }
    return render(request, 'membership/bulk_payment.html', context)


def overdue_report_view(request):
    """View for overdue membership dues report"""
    # Get current date
    today = timezone.now().date()

    # Get overdue dues
    overdue_dues = MembershipDues.objects.filter(
        is_paid=False,
        due_date__lt=today
    ).select_related('family').order_by('due_date', 'family__name')

    # Calculate totals
    total_overdue_amount = overdue_dues.aggregate(
        total=Sum('amount_due')
    )['total'] or Decimal('0.00')

    # Group by family for summary
    family_summary = {}
    for due in overdue_dues:
        family_name = due.family.name
        if family_name not in family_summary:
            family_summary[family_name] = {
                'family': due.family,
                'dues_count': 0,
                'total_amount': Decimal('0.00'),
                'dues': []
            }
        family_summary[family_name]['dues_count'] += 1
        family_summary[family_name]['total_amount'] += due.amount_due
        family_summary[family_name]['dues'].append(due)

    context = {
        'overdue_dues': overdue_dues,
        'total_overdue_amount': total_overdue_amount,
        'family_summary': family_summary,
        'today': today,
    }
    return render(request, 'membership/overdue_report.html', context)


def generate_monthly_dues_view(request):
    """View to generate monthly dues for all families"""
    if request.method == 'POST':
        year = int(request.POST.get('year'))
        month = int(request.POST.get('month'))

        # Check if dues already exist for this month
        existing_dues = MembershipDues.objects.filter(year=year, month=month)
        if existing_dues.exists():
            messages.warning(request, f'Dues for {year}-{month:02d} already exist!')
            return redirect('generate_monthly_dues')

        # Generate dues for all families
        families = Family.objects.all()
        created_count = 0

        for family in families:
            # Check if family has at least one active couple (simplified logic)
            active_members = family.members.filter(is_active=True)
            # For now, assume each family pays ₹10 regardless of member count
            # This can be enhanced with more complex logic later

            MembershipDues.objects.create(
                family=family,
                year=year,
                month=month,
                amount_due=Decimal('10.00'),
                due_date=timezone.datetime(year, month, 1).date()
            )
            created_count += 1

        messages.success(request, f'Generated {created_count} dues records for {year}-{month:02d}')
        return redirect('generate_monthly_dues')

    # GET request - show form
    today = timezone.now().date()
    context = {
        'current_year': today.year,
        'current_month': today.month,
    }
    return render(request, 'membership/generate_monthly_dues.html', context)
