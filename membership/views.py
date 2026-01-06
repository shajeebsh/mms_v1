import logging
from decimal import Decimal

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from django.http import HttpResponse
from .models import HouseRegistration, Member, MembershipDues, Payment
from .utils import generate_membership_questionnaire, generate_membership_card

logger = logging.getLogger(__name__)


def bulk_payment_view(request):
    """View for bulk payment processing"""
    if request.method == "POST":
        house_ids = request.POST.getlist("house_ids")
        payment_method = request.POST.get("payment_method")
        payment_date = request.POST.get("payment_date")
        notes = request.POST.get("notes", "")

        if not house_ids:
            messages.error(request, "Please select at least one house.")
            return redirect("bulk_payment")

        if not payment_method:
            messages.error(request, "Please select a payment method.")
            return redirect("bulk_payment")

        try:
            with transaction.atomic():
                total_amount = Decimal("0.00")
                selected_dues = []

                # Optimize: Get all houses and dues in bulk
                houses = HouseRegistration.objects.filter(id__in=house_ids)
                # Get all unpaid dues for selected houses in one query
                dues = (
                    MembershipDues.objects.filter(house__in=houses, is_paid=False)
                    .select_related("house")
                    .order_by("year", "month")
                )

                # Group dues by house
                for house in houses:
                    house_dues = [due for due in dues if due.house_id == house.id]
                    if house_dues:
                        selected_dues.extend(house_dues)
                        total_amount += sum(due.amount_due for due in house_dues)

                if not selected_dues:
                    messages.warning(
                        request, "No unpaid dues found for selected houses."
                    )
                    return redirect("bulk_payment")

                # Create payment record
                payment = Payment.objects.create(
                    house=HouseRegistration.objects.filter(
                        id__in=house_ids
                    ).first(),  # Use first house as reference
                    amount=total_amount,
                    payment_method=payment_method,
                    payment_date=payment_date or timezone.now().date(),
                    notes=f"Bulk payment for {len(house_ids)} houses - {notes}",
                )

                # Associate dues with payment and mark as paid
                for due in selected_dues:
                    payment.membership_dues.add(due)
                    due.is_paid = True
                    due.save()

                messages.success(
                    request,
                    f"Bulk payment processed successfully! Receipt #{payment.receipt_number} for ₹{total_amount}",
                )
                logger.info(
                    f"Bulk payment processed: Receipt #{payment.receipt_number}, "
                    f"Amount: ₹{total_amount}, Houses: {len(house_ids)}"
                )

        except ValidationError as e:
            messages.error(request, f"Validation error: {str(e)}")
            logger.warning(f"Validation error in bulk payment: {e}")
        except (ValueError, TypeError) as e:
            messages.error(request, f"Invalid input: {str(e)}")
            logger.error(f"Invalid input in bulk payment: {e}", exc_info=True)
        except Exception as e:
            messages.error(
                request,
                "An unexpected error occurred while processing the payment. Please try again.",
            )
            logger.error(f"Unexpected error in bulk payment: {e}", exc_info=True)

        return redirect("bulk_payment")

    # GET request - show form
    # Get houses with unpaid dues
    houses_with_dues = (
        HouseRegistration.objects.filter(membership_dues__is_paid=False)
        .distinct()
        .order_by("house_name", "house_number")
    )

    context = {
        "houses": houses_with_dues,
        "payment_methods": Payment.PAYMENT_METHOD_CHOICES,
    }
    return render(request, "membership/bulk_payment.html", context)


def overdue_report_view(request):
    """View for overdue membership dues report"""
    # Get current date
    today = timezone.now().date()

    # Get overdue dues with optimized query
    overdue_dues = (
        MembershipDues.objects.filter(is_paid=False, due_date__lt=today)
        .select_related("house")
        .prefetch_related("payments")
        .order_by("due_date", "house__house_name", "house__house_number")
    )

    # Calculate totals
    total_overdue_amount = overdue_dues.aggregate(total=Sum("amount_due"))[
        "total"
    ] or Decimal("0.00")

    # Group by house for summary
    house_summary = {}
    for due in overdue_dues:
        house_name = str(due.house)
        if house_name not in house_summary:
            house_summary[house_name] = {
                "house": due.house,
                "dues_count": 0,
                "total_amount": Decimal("0.00"),
                "dues": [],
            }
        house_summary[house_name]["dues_count"] += 1
        house_summary[house_name]["total_amount"] += due.amount_due
        house_summary[house_name]["dues"].append(due)

    context = {
        "overdue_dues": overdue_dues,
        "total_overdue_amount": total_overdue_amount,
        "house_summary": house_summary,
        "today": today,
    }
    return render(request, "membership/overdue_report.html", context)


def generate_monthly_dues_view(request):
    """View to generate monthly dues for all houses"""
    if request.method == "POST":
        try:
            year = int(request.POST.get("year"))
            month = int(request.POST.get("month"))

            # Validate month range
            if not (1 <= month <= 12):
                messages.error(request, "Month must be between 1 and 12.")
                return redirect("generate_monthly_dues")

            # Check if dues already exist for this month
            existing_dues = MembershipDues.objects.filter(year=year, month=month)
            if existing_dues.exists():
                messages.warning(request, f"Dues for {year}-{month:02d} already exist!")
                return redirect("generate_monthly_dues")

            # Generate dues for all houses
            houses = HouseRegistration.objects.all()
            created_count = 0

            with transaction.atomic():
                for house in houses:
                    # For now, assume each house pays ₹10 regardless of member count
                    # This can be enhanced with more complex logic later

                    MembershipDues.objects.create(
                        house=house,
                        year=year,
                        month=month,
                        amount_due=Decimal("10.00"),
                        due_date=timezone.datetime(year, month, 1).date(),
                    )
                    created_count += 1

            messages.success(
                request,
                f"Generated {created_count} dues records for {year}-{month:02d}",
            )
            logger.info(
                f"Generated {created_count} dues records for {year}-{month:02d}"
            )
            return redirect("generate_monthly_dues")

        except (ValueError, TypeError) as e:
            messages.error(request, "Invalid year or month provided.")
            logger.warning(f"Invalid input in generate_monthly_dues: {e}")
            return redirect("generate_monthly_dues")
        except Exception as e:
            messages.error(
                request, "An error occurred while generating dues. Please try again."
            )
            logger.error(
                f"Unexpected error in generate_monthly_dues: {e}", exc_info=True
            )
            return redirect("generate_monthly_dues")

    # GET request - show form
    today = timezone.now().date()
    context = {
        "current_year": today.year,
        "current_month": today.month,
    }
    return render(request, "membership/generate_monthly_dues.html", context)


def download_questionnaire_view(request):
    """View to download a blank membership questionnaire"""
    buffer = generate_membership_questionnaire()
    response = HttpResponse(buffer.read(), content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="membership_questionnaire.pdf"'
    return response


def preview_questionnaire_view(request):
    """View to preview the membership questionnaire"""
    return render(request, 'membership/preview_questionnaire.html')


def print_membership_card_view(request, member_id):
    """View to download/print a membership card for a specific member"""
    member = get_object_or_404(Member, id=member_id)
    buffer = generate_membership_card(member)
    response = HttpResponse(buffer.read(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="membership_card_{member.id}.pdf"'
    return response


def preview_membership_card_view(request, member_id):
    """View to preview a membership card for a specific member"""
    member = get_object_or_404(Member, id=member_id)
    context = {
        'member': member,
    }
    return render(request, 'membership/preview_card.html', context)
