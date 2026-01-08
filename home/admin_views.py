import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import transaction
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
    for module_name, module_info in context["modules"].items():
        print(
            f"DEBUG: Module {module_name}, Description: {module_info.get('description')}"
        )
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
