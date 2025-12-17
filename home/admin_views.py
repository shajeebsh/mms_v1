import logging
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.db import transaction
from django.shortcuts import render, redirect
from django.urls import reverse
from wagtail.admin.decorators import require_admin_access
from django.views.decorators.http import require_http_methods
from django.utils import timezone

from home.models import SystemSettings

logger = logging.getLogger(__name__)

# Module definitions
MODULES = {
    'membership': {
        'name': 'Membership',
        'icon': 'group',
        'description': 'Families, members, dues, payments, and vital records',
    },
    'assets': {
        'name': 'Assets',
        'icon': 'home',
        'description': 'Shops and property units',
    },
    'education': {
        'name': 'Education',
        'icon': 'user',
        'description': 'Teachers, classes, and student enrollments',
    },
    'finance': {
        'name': 'Finance',
        'icon': 'money',
        'description': 'Donations, expenses, and financial reports',
    },
    'operations': {
        'name': 'Operations',
        'icon': 'calendar',
        'description': 'Prayer times, auditorium bookings, and digital signage',
    },
    'hr': {
        'name': 'HR & Payroll',
        'icon': 'user',
        'description': 'Staff, attendance, leave, and payroll',
    },
    'committee': {
        'name': 'Committee & Minutes',
        'icon': 'group',
        'description': 'Committees, meetings, trustees, and minutes',
    },
}


@require_admin_access
@require_http_methods(["GET", "POST"])
def sample_data_management_view(request):
    """Admin view for managing sample data population and removal"""
    
    if not request.user.is_superuser:
        messages.error(request, 'Only administrators can access sample data management.')
        return redirect('wagtailadmin_home')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        selected_modules = request.POST.getlist('modules')
        
        if not selected_modules:
            messages.warning(request, 'Please select at least one module.')
            return redirect('admin:sample_data_management')
        
        if action == 'populate':
            return _populate_sample_data(request, selected_modules)
        elif action == 'clear':
            return _clear_sample_data(request, selected_modules)
        else:
            messages.error(request, 'Invalid action.')
            return redirect('admin:sample_data_management')
    
    # GET request - show the form
    context = {
        'modules': MODULES,
        'enabled_modules': _get_enabled_modules(),
    }
    return render(request, 'home/admin/sample_data_management.html', context)


def _populate_sample_data(request, selected_modules):
    """Populate sample data for selected modules"""
    from membership.management.commands.populate_sample_data import Command
    
    try:
        command = Command()
        command.stdout = type('obj', (object,), {'write': lambda self, msg: None})()
        command.style = type('obj', (object,), {
            'SUCCESS': lambda x: x,
            'WARNING': lambda x: x,
        })()
        
        populated_modules = []
        errors = []
        
        with transaction.atomic():
            for module in selected_modules:
                if module not in MODULES:
                    errors.append(f"Unknown module: {module}")
                    continue
                
                try:
                    if module == 'membership':
                        command.create_membership_data()
                    elif module == 'assets':
                        command.create_assets_data()
                    elif module == 'education':
                        command.create_education_data()
                    elif module == 'finance':
                        command.create_finance_data()
                    elif module == 'operations':
                        command.create_operations_data()
                    elif module == 'hr':
                        command.create_hr_data()
                    elif module == 'committee':
                        command.create_committee_data()
                    
                    populated_modules.append(MODULES[module]['name'])
                    logger.info(f"Sample data populated for {module} module by {request.user.username}")
                    
                except Exception as e:
                    errors.append(f"Error populating {MODULES[module]['name']}: {str(e)}")
                    logger.error(f"Error populating {module} module: {e}", exc_info=True)
        
        if populated_modules:
            messages.success(
                request,
                f'Successfully populated sample data for: {", ".join(populated_modules)}'
            )
        
        if errors:
            for error in errors:
                messages.error(request, error)
        
    except Exception as e:
        messages.error(request, f'An error occurred while populating sample data: {str(e)}')
        logger.error(f"Error in sample data population: {e}", exc_info=True)
    
    return redirect('admin:sample_data_management')


def _clear_sample_data(request, selected_modules):
    """Clear sample data for selected modules"""
    from assets.models import PropertyUnit, Shop
    from education.models import Class, StudentEnrollment, Teacher
    from finance.models import (Donation, DonationCategory, Expense,
                                ExpenseCategory, FinancialReport)
    from membership.models import (Family, Member, MembershipDues, Payment,
                                   VitalRecord)
    from operations.models import (AuditoriumBooking, DigitalSignageContent,
                                   PrayerTime)
    from hr.models import (StaffPosition, StaffMember, Attendance, LeaveType,
                           LeaveRequest, SalaryComponent, StaffSalary, Payroll)
    from committee.models import (CommitteeType, Committee, CommitteeMember,
                                   Meeting, MeetingAttendee, Trustee,
                                   TrusteeMeeting, TrusteeMeetingAttendee)
    
    cleared_modules = []
    errors = []
    
    try:
        with transaction.atomic():
            for module in selected_modules:
                if module not in MODULES:
                    errors.append(f"Unknown module: {module}")
                    continue
                
                try:
                    if module == 'membership':
                        Payment.objects.all().delete()
                        MembershipDues.objects.all().delete()
                        VitalRecord.objects.all().delete()
                        Member.objects.all().delete()
                        Family.objects.all().delete()
                    elif module == 'assets':
                        PropertyUnit.objects.all().delete()
                        Shop.objects.all().delete()
                    elif module == 'education':
                        StudentEnrollment.objects.all().delete()
                        Class.objects.all().delete()
                        Teacher.objects.all().delete()
                    elif module == 'finance':
                        FinancialReport.objects.all().delete()
                        Expense.objects.all().delete()
                        Donation.objects.all().delete()
                        ExpenseCategory.objects.all().delete()
                        DonationCategory.objects.all().delete()
                    elif module == 'operations':
                        DigitalSignageContent.objects.all().delete()
                        PrayerTime.objects.all().delete()
                        AuditoriumBooking.objects.all().delete()
                    elif module == 'hr':
                        Payroll.objects.all().delete()
                        StaffSalary.objects.all().delete()
                        LeaveRequest.objects.all().delete()
                        Attendance.objects.all().delete()
                        StaffMember.objects.all().delete()
                        SalaryComponent.objects.all().delete()
                        LeaveType.objects.all().delete()
                        StaffPosition.objects.all().delete()
                    elif module == 'committee':
                        TrusteeMeetingAttendee.objects.all().delete()
                        TrusteeMeeting.objects.all().delete()
                        MeetingAttendee.objects.all().delete()
                        Meeting.objects.all().delete()
                        CommitteeMember.objects.all().delete()
                        Trustee.objects.all().delete()
                        Committee.objects.all().delete()
                        CommitteeType.objects.all().delete()
                    
                    cleared_modules.append(MODULES[module]['name'])
                    logger.info(f"Sample data cleared for {module} module by {request.user.username}")
                    
                except Exception as e:
                    errors.append(f"Error clearing {MODULES[module]['name']}: {str(e)}")
                    logger.error(f"Error clearing {module} module: {e}", exc_info=True)
        
        if cleared_modules:
            messages.success(
                request,
                f'Successfully cleared sample data for: {", ".join(cleared_modules)}'
            )
        
        if errors:
            for error in errors:
                messages.error(request, error)
        
    except Exception as e:
        messages.error(request, f'An error occurred while clearing sample data: {str(e)}')
        logger.error(f"Error in sample data clearing: {e}", exc_info=True)
    
    return redirect('admin:sample_data_management')


def _get_enabled_modules():
    """Get list of enabled module names"""
    enabled = []
    for module_name in MODULES.keys():
        if SystemSettings.is_module_enabled(module_name):
            enabled.append(module_name)
    return enabled

