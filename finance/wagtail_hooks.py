from wagtail.admin.panels import FieldPanel, FieldRowPanel, MultiFieldPanel
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
    list_display = ('donor_display', 'amount', 'donation_type', 'date', 'category')
    list_filter = ('donation_type', 'date', 'category')
    search_fields = ('member__first_name', 'member__last_name', 'donor_name', 'notes', 'receipt_number')
    panels = [
        MultiFieldPanel(
            [
                FieldRowPanel(
                    [
                        FieldPanel('member', classname='col6'),
                        FieldPanel('donor_name', classname='col6'),
                    ],
                    classname='compact-row',
                ),
                FieldRowPanel(
                    [
                        FieldPanel('category', classname='col6'),
                        FieldPanel('amount', classname='col6'),
                    ],
                    classname='compact-row',
                ),
                FieldRowPanel(
                    [
                        FieldPanel('donation_type', classname='col6'),
                        FieldPanel('date', classname='col6'),
                    ],
                    classname='compact-row',
                ),
                FieldRowPanel(
                    [
                        FieldPanel('receipt_number', classname='col12'),
                    ],
                    classname='compact-row',
                ),
                FieldRowPanel(
                    [
                        FieldPanel('notes', classname='col12'),
                    ],
                    classname='compact-row',
                ),
            ],
            heading='Donation Details',
            classname='compact-panel',
        ),
    ]


class ExpenseAdmin(ModelAdmin):
    model = Expense
    permission_helper_class = ACLPermissionHelper
    menu_label = 'Expenses'
    menu_icon = 'minus'
    add_to_admin_menu = False  # Will be included in grouped menu
    list_display = ('name', 'description', 'amount', 'category', 'date', 'approved_by')
    list_filter = ('category', 'date')
    search_fields = ('name', 'description', 'approved_by', 'vendor', 'receipt_number')
    panels = [
        MultiFieldPanel(
            [
                FieldRowPanel(
                    [
                        FieldPanel('name', classname='col6'),
                        FieldPanel('category', classname='col6'),
                    ],
                    classname='compact-row',
                ),
                FieldRowPanel(
                    [
                        FieldPanel('amount', classname='col6'),
                        FieldPanel('date', classname='col6'),
                    ],
                    classname='compact-row',
                ),
                FieldRowPanel(
                    [
                        FieldPanel('approved_by', classname='col6'),
                        FieldPanel('vendor', classname='col6'),
                    ],
                    classname='compact-row',
                ),
                FieldRowPanel(
                    [
                        FieldPanel('receipt_number', classname='col12'),
                    ],
                    classname='compact-row',
                ),
                FieldRowPanel(
                    [
                        FieldPanel('description', classname='col12'),
                    ],
                    classname='compact-row',
                ),
            ],
            heading='Expense Details',
            classname='compact-panel',
        ),
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
        MultiFieldPanel(
            [
                FieldRowPanel(
                    [
                        FieldPanel('period', classname='col4'),
                        FieldPanel('start_date', classname='col4'),
                        FieldPanel('end_date', classname='col4'),
                    ],
                    classname='compact-row',
                ),
                FieldRowPanel(
                    [
                        FieldPanel('total_donations', classname='col4'),
                        FieldPanel('total_expenses', classname='col4'),
                        FieldPanel('net_amount', classname='col4'),
                    ],
                    classname='compact-row',
                ),
                FieldRowPanel(
                    [
                        FieldPanel('generated_by', classname='col12'),
                    ],
                    classname='compact-row',
                ),
            ],
            heading='Report Details',
            classname='compact-panel',
        ),
    ]


modeladmin_register(DonationCategoryAdmin)
modeladmin_register(ExpenseCategoryAdmin)
modeladmin_register(DonationAdmin)
modeladmin_register(ExpenseAdmin)
modeladmin_register(FinancialReportAdmin)