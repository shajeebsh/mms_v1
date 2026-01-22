import csv
import datetime
import logging
from django.apps import apps

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import models, transaction
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from home.models import SystemSettings

logger = logging.getLogger(__name__)

# Module definitions
MODULES = {
    "membership": {
        "name": "Membership",
        "icon": "group",
        "description": "Houses, members, dues, payments, and vital records",
    },
    "membership_geography": {
        "name": "Membership Geography",
        "icon": "site",
        "description": "Ward, taluk, city, state, country, and postal code dropdown values",
    },
    "membership_houses": {
        "name": "House Registrations",
        "icon": "home",
        "description": "House registrations linked to geography values",
    },
    "assets": {
        "name": "Assets",
        "icon": "home",
        "description": "Shops and property units",
    },
    "education": {
        "name": "Education",
        "icon": "user",
        "description": "Teachers, classes, and student enrollments",
    },
    "finance": {
        "name": "Finance",
        "icon": "money",
        "description": "Donations, expenses, and financial reports",
    },
    "operations": {
        "name": "Operations",
        "icon": "calendar",
        "description": "Prayer times, auditorium bookings, and digital signage",
    },
    "hr": {
        "name": "HR & Payroll",
        "icon": "user",
        "description": "Staff, attendance, leave, and payroll",
    },
    "committee": {
        "name": "Committee & Minutes",
        "icon": "group",
        "description": "Committees, meetings, trustees, and minutes",
    },
    "accounting": {
        "name": "Accounting & Ledger",
        "icon": "list-ul",
        "description": "Chart of accounts, transactions, and ledger",
    },
    "billing": {
        "name": "Billing & Invoices",
        "icon": "doc-full",
        "description": "Invoices, billing payments, and consolidated bills",
    },
}


def _is_superuser(user):
    """Check if user is superuser"""
    return user.is_authenticated and user.is_superuser


@login_required
@user_passes_test(_is_superuser)
@require_http_methods(["GET", "POST"])
def sample_data_management_view(request):
    """Admin view for managing sample data population and removal"""

    if request.method == "POST":
        action = request.POST.get("action")
        selected_modules = request.POST.getlist("modules")

        if not selected_modules:
            messages.warning(request, "Please select at least one module.")
            return redirect("home_admin:sample_data_management")

        if action == "populate":
            return _populate_sample_data(request, selected_modules)
        elif action == "clear":
            return _clear_sample_data(request, selected_modules)
        else:
            messages.error(request, "Invalid action.")
            return redirect("home_admin:sample_data_management")

    # GET request - show the form
    context = {
        "modules": MODULES,
        "enabled_modules": _get_enabled_modules(),
    }

    return render(request, "home/admin/sample_data_management.html", context)


def _populate_sample_data(request, selected_modules):
    """Populate sample data for selected modules"""
    from wagtail.signal_handlers import disable_reference_index_auto_update

    from membership.management.commands.populate_sample_data import Command

    try:
        command = Command()
        command.stdout = type("obj", (object,), {"write": lambda self, msg: None})()
        command.style = type(
            "obj",
            (object,),
            {
                "SUCCESS": lambda x: x,
                "WARNING": lambda x: x,
            },
        )()

        populated_modules = []
        errors = []

        with disable_reference_index_auto_update(), transaction.atomic():
            for module in selected_modules:
                if module not in MODULES:
                    errors.append(f"Unknown module: {module}")
                    continue

                try:
                    if module == "membership":
                        command.create_membership_data()
                    elif module == "membership_geography":
                        command.create_membership_geography_data()
                    elif module == "membership_houses":
                        command.create_house_registration_data()
                    elif module == "assets":
                        command.create_assets_data()
                    elif module == "education":
                        command.create_education_data()
                    elif module == "finance":
                        command.create_finance_data()
                    elif module == "operations":
                        command.create_operations_data()
                    elif module == "hr":
                        command.create_hr_data()
                    elif module == "committee":
                        command.create_committee_data()
                    elif module == "accounting":
                        command.create_accounting_data()
                    elif module == "billing":
                        command.create_billing_data()

                    populated_modules.append(MODULES[module]["name"])
                    logger.info(
                        f"Sample data populated for {module} module by {request.user.username}"
                    )

                except Exception as e:
                    errors.append(
                        f"Error populating {MODULES[module]['name']}: {str(e)}"
                    )
                    logger.error(
                        f"Error populating {module} module: {e}", exc_info=True
                    )

        if populated_modules:
            messages.success(
                request,
                f'Successfully populated sample data for: {", ".join(populated_modules)}',
            )

        if errors:
            for error in errors:
                messages.error(request, error)

    except Exception as e:
        messages.error(
            request, f"An error occurred while populating sample data: {str(e)}"
        )
        logger.error(f"Error in sample data population: {e}", exc_info=True)

    return redirect("home_admin:sample_data_management")


def _clear_sample_data(request, selected_modules):
    """Clear sample data for selected modules"""
    from wagtail.signal_handlers import disable_reference_index_auto_update

    from accounting.models import Account, AccountCategory, JournalEntry, Transaction
    from assets.models import PropertyUnit, Shop
    from billing.models import BillingPayment, Invoice, InvoiceLineItem
    from committee.models import (
        Committee,
        CommitteeMember,
        CommitteeType,
        Meeting,
        MeetingAttachment,
        MeetingAttendee,
        Trustee,
        TrusteeMeeting,
        TrusteeMeetingAttachment,
        TrusteeMeetingAttendee,
    )
    from education.models import Class, StudentEnrollment, Teacher
    from finance.models import (
        Donation,
        DonationCategory,
        Expense,
        ExpenseCategory,
        FinancialReport,
    )
    from hr.models import (
        Attendance,
        LeaveRequest,
        LeaveType,
        Payroll,
        SalaryComponent,
        StaffMember,
        StaffPosition,
        StaffSalary,
    )
    from membership.models import (
        City,
        Country,
        HouseRegistration,
        Member,
        MembershipDues,
        Payment,
        PostalCode,
        State,
        Taluk,
        VitalRecord,
        Ward,
    )
    from operations.models import AuditoriumBooking

    cleared_modules = []
    errors = []

    try:
        with disable_reference_index_auto_update(), transaction.atomic():
            for module in selected_modules:
                if module not in MODULES:
                    errors.append(f"Unknown module: {module}")
                    continue

                try:
                    if module == "membership":
                        Payment.objects.all().delete()
                        MembershipDues.objects.all().delete()
                        VitalRecord.objects.all().delete()
                        Member.objects.all().delete()
                        HouseRegistration.objects.all().delete()
                        PostalCode.objects.all().delete()
                        Country.objects.all().delete()
                        State.objects.all().delete()
                        City.objects.all().delete()
                        Taluk.objects.all().delete()
                        Ward.objects.all().delete()
                    elif module == "membership_houses":
                        Payment.objects.all().delete()
                        MembershipDues.objects.all().delete()
                        VitalRecord.objects.all().delete()
                        Member.objects.all().delete()
                        HouseRegistration.objects.all().delete()
                    elif module == "membership_geography":
                        Payment.objects.all().delete()
                        MembershipDues.objects.all().delete()
                        VitalRecord.objects.all().delete()
                        Member.objects.all().delete()
                        HouseRegistration.objects.all().delete()
                        PostalCode.objects.all().delete()
                        Country.objects.all().delete()
                        State.objects.all().delete()
                        City.objects.all().delete()
                        Taluk.objects.all().delete()
                        Ward.objects.all().delete()
                    elif module == "assets":
                        PropertyUnit.objects.all().delete()
                        Shop.objects.all().delete()
                    elif module == "education":
                        StudentEnrollment.objects.all().delete()
                        Class.objects.all().delete()
                        Teacher.objects.all().delete()
                    elif module == "finance":
                        FinancialReport.objects.all().delete()
                        Expense.objects.all().delete()
                        Donation.objects.all().delete()
                        ExpenseCategory.objects.all().delete()
                        DonationCategory.objects.all().delete()
                    elif module == "operations":
                        AuditoriumBooking.objects.all().delete()
                    elif module == "hr":
                        Payroll.objects.all().delete()
                        StaffSalary.objects.all().delete()
                        LeaveRequest.objects.all().delete()
                        Attendance.objects.all().delete()
                        StaffMember.objects.all().delete()
                        SalaryComponent.objects.all().delete()
                        LeaveType.objects.all().delete()
                        StaffPosition.objects.all().delete()
                    elif module == "committee":
                        TrusteeMeetingAttachment.objects.all().delete()
                        TrusteeMeetingAttendee.objects.all().delete()
                        TrusteeMeeting.objects.all().delete()
                        MeetingAttachment.objects.all().delete()
                        MeetingAttendee.objects.all().delete()
                        Meeting.objects.all().delete()
                        CommitteeMember.objects.all().delete()
                        Trustee.objects.all().delete()
                        Committee.objects.all().delete()
                        CommitteeType.objects.all().delete()
                    elif module == "accounting":
                        JournalEntry.objects.all().delete()
                        Transaction.objects.all().delete()
                        Account.objects.all().delete()
                        AccountCategory.objects.all().delete()
                    elif module == "billing":
                        BillingPayment.objects.all().delete()
                        InvoiceLineItem.objects.all().delete()
                        Invoice.objects.all().delete()

                    cleared_modules.append(MODULES[module]["name"])
                    logger.info(
                        f"Sample data cleared for {module} module by {request.user.username}"
                    )

                except Exception as e:
                    errors.append(f"Error clearing {MODULES[module]['name']}: {str(e)}")
                    logger.error(f"Error clearing {module} module: {e}", exc_info=True)

        if cleared_modules:
            messages.success(
                request,
                f'Successfully cleared sample data for: {", ".join(cleared_modules)}',
            )

        if errors:
            for error in errors:
                messages.error(request, error)

    except Exception as e:
        messages.error(
            request, f"An error occurred while clearing sample data: {str(e)}"
        )
        logger.error(f"Error in sample data clearing: {e}", exc_info=True)

    return redirect("home_admin:sample_data_management")


def _get_enabled_modules():
    """Get list of enabled module names"""
    enabled = []
    for module_name in MODULES.keys():
        if SystemSettings.is_module_enabled(module_name):
            enabled.append(module_name)
    return enabled


@login_required
@user_passes_test(_is_superuser)
def data_profiling_view(request):
    """Admin view for data profiling statistics"""
    
    stats = []
    target_apps = [
        'membership', 'finance', 'education', 'assets', 
        'operations', 'hr', 'committee', 'accounting', 'billing', 'home'
    ]
    
    for app_label in target_apps:
        try:
            app_config = apps.get_app_config(app_label)
        except LookupError:
            continue
            
        for model in app_config.get_models():
            # Skip historical models or M2M through models if they clutter
            if model._meta.auto_created:
                continue
                
            model_name = model._meta.verbose_name.title()
            count = model.objects.count()
            
            last_updated = None
            # Try to find a date field for 'last updated'
            date_fields = [f.name for f in model._meta.fields if isinstance(f, (models.DateTimeField, models.DateField))]
            
            if 'updated_at' in date_fields:
                latest_record = model.objects.order_by('-updated_at').first()
                if latest_record:
                    last_updated = latest_record.updated_at
            elif 'created_at' in date_fields:
                latest_record = model.objects.order_by('-created_at').first()
                if latest_record:
                    last_updated = latest_record.created_at
            elif date_fields:
                # Fallback to any date field
                field_name = date_fields[0]
                latest_record = model.objects.order_by(f'-{field_name}').first()
                if latest_record:
                    last_updated = getattr(latest_record, field_name)

            # Ensure last_updated is a datetime object for template formatting
            if last_updated and isinstance(last_updated, datetime.date) and not isinstance(last_updated, datetime.datetime):
                last_updated = datetime.datetime.combine(last_updated, datetime.time.min)
                if settings.USE_TZ:
                    last_updated = timezone.make_aware(last_updated)

            stats.append({
                'app': app_label.title(),
                'model': model_name,
                'count': count,
                'last_updated': last_updated,
            })

    # Sort stats by app then by record count descending
    stats.sort(key=lambda x: (x['app'], -x['count']))

    # Handle CSV Export
    if request.GET.get('export') == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="data_profiling_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Module', 'Model Name', 'Record Count', 'Last Updated'])
        
        for s in stats:
            last_upd = s['last_updated'].strftime('%Y-%m-%d %H:%M:%S') if s['last_updated'] else 'N/A'
            writer.writerow([s['app'], s['model'], s['count'], last_upd])
            
        return response

    context = {
        'stats': stats,
        'now': timezone.now(),
    }
    
    return render(request, "home/admin/data_profiling.html", context)
