from wagtail_modeladmin.options import ModelAdmin, ModelAdminGroup, modeladmin_register
from .models import Invoice, BillingPayment

class InvoiceAdmin(ModelAdmin):
    model = Invoice
    menu_label = 'Invoices'
    menu_icon = 'doc-full'
    list_display = ('invoice_number', 'family', 'shop', 'date_issued', 'due_date', 'status', 'total_amount', 'balance_due')
    list_filter = ('status', 'date_issued')
    search_fields = ('invoice_number', 'family__name', 'shop__name')
    add_to_admin_menu = False
    extra_css = {'all': ('home/css/admin_theme.css',)}

class BillingPaymentAdmin(ModelAdmin):
    model = BillingPayment
    menu_label = 'Billing Payments'
    menu_icon = 'pick'
    list_display = ('invoice', 'amount', 'payment_date', 'payment_method')
    list_filter = ('payment_method', 'payment_date')
    add_to_admin_menu = False
    extra_css = {'all': ('home/css/admin_theme.css',)}

modeladmin_register(InvoiceAdmin)
modeladmin_register(BillingPaymentAdmin)
