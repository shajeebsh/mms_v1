from wagtail.admin.panels import FieldPanel
from wagtail_modeladmin.options import ModelAdmin, modeladmin_register

from .models import Donation, Expense, FinancialReport, DonationCategory, ExpenseCategory


from home.permission_helpers import ACLPermissionHelper

class DonationCategoryAdmin(ModelAdmin):
    model = DonationCategory
    permission_helper_class = ACLPermissionHelper
    menu_label = 'Donation Categories'
    menu_icon = 'tag'
    add_to_admin_menu = False  # Will be included in grouped menu
    list_display = ('name', 'description')
    search_fields = ('name', 'description')


class ExpenseCategoryAdmin(ModelAdmin):
    model = ExpenseCategory
    permission_helper_class = ACLPermissionHelper
    menu_label = 'Expense Categories'
    menu_icon = 'tag'
    add_to_admin_menu = False  # Will be included in grouped menu
    list_display = ('name', 'description')
    search_fields = ('name', 'description')


class DonationAdmin(ModelAdmin):
    model = Donation
    permission_helper_class = ACLPermissionHelper
    menu_label = 'Donations'
    menu_icon = 'money'
    add_to_admin_menu = False  # Will be included in grouped menu
    list_display = ('member', 'amount', 'donation_type', 'date', 'category')
    list_filter = ('donation_type', 'date', 'category')
    search_fields = ('member__first_name', 'member__last_name', 'notes', 'receipt_number')
    panels = [
        FieldPanel('member'),
        FieldPanel('category'),
        FieldPanel('amount'),
        FieldPanel('donation_type'),
        FieldPanel('date'),
        FieldPanel('notes'),
        FieldPanel('receipt_number'),
    ]


class ExpenseAdmin(ModelAdmin):
    model = Expense
    permission_helper_class = ACLPermissionHelper
    menu_label = 'Expenses'
    menu_icon = 'minus'
    add_to_admin_menu = False  # Will be included in grouped menu
    list_display = ('description', 'amount', 'category', 'date', 'approved_by')
    list_filter = ('category', 'date')
    search_fields = ('description', 'approved_by', 'vendor', 'receipt_number')
    panels = [
        FieldPanel('category'),
        FieldPanel('amount'),
        FieldPanel('date'),
        FieldPanel('description'),
        FieldPanel('approved_by'),
        FieldPanel('vendor'),
        FieldPanel('receipt_number'),
    ]


class FinancialReportAdmin(ModelAdmin):
    model = FinancialReport
    permission_helper_class = ACLPermissionHelper
    menu_label = 'Financial Reports'
    menu_icon = 'chart-bar'
    add_to_admin_menu = False  # Will be included in grouped menu
    list_display = ('period', 'start_date', 'end_date', 'total_donations', 'total_expenses', 'net_amount')
    list_filter = ('period', 'generated_at')
    search_fields = ('period', 'generated_by')
    panels = [
        FieldPanel('period'),
        FieldPanel('start_date'),
        FieldPanel('end_date'),
        FieldPanel('total_donations'),
        FieldPanel('total_expenses'),
        FieldPanel('net_amount'),
        FieldPanel('generated_by'),
    ]


modeladmin_register(DonationCategoryAdmin)
modeladmin_register(ExpenseCategoryAdmin)
modeladmin_register(DonationAdmin)
modeladmin_register(ExpenseAdmin)
modeladmin_register(FinancialReportAdmin)