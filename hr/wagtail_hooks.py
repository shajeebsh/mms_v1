from wagtail import hooks
from wagtail.admin.menu import MenuItem
from wagtail.admin.search import SearchArea
from wagtail_modeladmin.options import ModelAdmin, modeladmin_register
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from .models import (
    StaffPosition, StaffMember, Attendance, LeaveType, LeaveRequest,
    SalaryComponent, StaffSalary, Payroll
)


class StaffPositionAdmin(ModelAdmin):
    model = StaffPosition
    menu_label = 'Staff Positions'
    menu_icon = 'user'
    add_to_admin_menu = False
    list_display = ('name', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')


class StaffMemberAdmin(ModelAdmin):
    model = StaffMember
    menu_label = 'Staff Directory'
    menu_icon = 'group'
    add_to_admin_menu = False
    list_display = ('member', 'position', 'employment_type', 'hire_date', 'is_active')
    list_filter = ('position', 'employment_type', 'is_active')
    search_fields = ('member__first_name', 'member__last_name', 'position__name')
    raw_id_fields = ('member',)


class AttendanceAdmin(ModelAdmin):
    model = Attendance
    menu_label = 'Attendance Records'
    menu_icon = 'date'
    add_to_admin_menu = False
    list_display = ('staff_member', 'date', 'status', 'hours_worked')
    list_filter = ('status', 'date')
    search_fields = ('staff_member__member__first_name', 'staff_member__member__last_name')
    raw_id_fields = ('staff_member',)


class LeaveTypeAdmin(ModelAdmin):
    model = LeaveType
    menu_label = 'Leave Types'
    menu_icon = 'time'
    add_to_admin_menu = False
    list_display = ('name', 'days_allowed_per_year', 'is_paid', 'requires_approval')
    list_filter = ('is_paid', 'requires_approval')


class LeaveRequestAdmin(ModelAdmin):
    model = LeaveRequest
    menu_label = 'Leave Requests'
    menu_icon = 'doc-full'
    add_to_admin_menu = False
    list_display = ('staff_member', 'leave_type', 'start_date', 'end_date', 'status')
    list_filter = ('status', 'leave_type', 'start_date')
    search_fields = ('staff_member__member__first_name', 'staff_member__member__last_name')
    raw_id_fields = ('staff_member', 'approved_by')


class SalaryComponentAdmin(ModelAdmin):
    model = SalaryComponent
    menu_label = 'Salary Components'
    menu_icon = 'cog'
    add_to_admin_menu = False
    list_display = ('name', 'component_type', 'is_taxable', 'is_active')
    list_filter = ('component_type', 'is_taxable', 'is_active')


class StaffSalaryAdmin(ModelAdmin):
    model = StaffSalary
    menu_label = 'Staff Salaries'
    menu_icon = 'money'
    add_to_admin_menu = False
    list_display = ('staff_member', 'salary_component', 'amount', 'effective_date', 'is_active')
    list_filter = ('salary_component', 'is_active', 'effective_date')
    search_fields = ('staff_member__member__first_name', 'staff_member__member__last_name')
    raw_id_fields = ('staff_member',)


class PayrollAdmin(ModelAdmin):
    model = Payroll
    menu_label = 'Payroll Records'
    menu_icon = 'download'
    add_to_admin_menu = False
    list_display = ('staff_member', 'pay_period_start', 'pay_period_end', 'net_salary', 'payment_status')
    list_filter = ('payment_status', 'pay_period_start')
    search_fields = ('staff_member__member__first_name', 'staff_member__member__last_name')
    raw_id_fields = ('staff_member', 'processed_by')


# Register all ModelAdmin classes
modeladmin_register(StaffPositionAdmin)
modeladmin_register(StaffMemberAdmin)
modeladmin_register(AttendanceAdmin)
modeladmin_register(LeaveTypeAdmin)
modeladmin_register(LeaveRequestAdmin)
modeladmin_register(SalaryComponentAdmin)
modeladmin_register(StaffSalaryAdmin)
modeladmin_register(PayrollAdmin)


@hooks.register('register_admin_menu_item')
def register_hr_menu():
    return MenuItem(
        _('HR & Payroll'),
        reverse('wagtailadmin_home'),
        icon_name='user',
        order=1000
    )


@hooks.register('register_admin_search_area')
def register_hr_search_area():
    return SearchArea(
        _('HR & Payroll'),
        reverse('wagtailadmin_home'),
        icon_name='user',
        order=1000
    )