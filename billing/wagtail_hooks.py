from wagtail.admin.panels import FieldPanel, FieldRowPanel, MultiFieldPanel
from wagtail_modeladmin.options import ModelAdmin, ModelAdminGroup, modeladmin_register

from .models import BillingPayment, Invoice


class InvoiceAdmin(ModelAdmin):
    model = Invoice
    menu_label = "Invoices"
    menu_icon = "doc-full"
    list_display = (
        "invoice_number",
        "house",
        "shop",
        "date_issued",
        "due_date",
        "status",
        "total_amount",
        "balance_due",
    )
    list_filter = ("status", "date_issued")
    search_fields = ("invoice_number", "house__house_name", "house__house_number", "shop__name")
    add_to_admin_menu = False
    panels = [
        MultiFieldPanel(
            [
                FieldRowPanel(
                    [
                        FieldPanel('invoice_number', classname='col6'),
                        FieldPanel('status', classname='col6'),
                    ],
                    classname='compact-row',
                ),
                FieldRowPanel(
                    [
                        FieldPanel('house', classname='col4'),
                        FieldPanel('shop', classname='col4'),
                        FieldPanel('property_unit', classname='col4'),
                    ],
                    classname='compact-row',
                ),
                FieldRowPanel(
                    [
                        FieldPanel('date_issued', classname='col6'),
                        FieldPanel('due_date', classname='col6'),
                    ],
                    classname='compact-row',
                ),
                FieldRowPanel(
                    [
                        FieldPanel('total_amount', classname='col6'),
                        FieldPanel('amount_paid', classname='col6'),
                    ],
                    classname='compact-row',
                ),
            ],
            heading='Invoice Details',
            classname='compact-panel',
        ),
    ]


class BillingPaymentAdmin(ModelAdmin):
    model = BillingPayment
    menu_label = "Billing Payments"
    menu_icon = "pick"
    list_display = ("invoice", "amount", "payment_date", "payment_method")
    list_filter = ("payment_method", "payment_date")
    add_to_admin_menu = False
    panels = [
        MultiFieldPanel(
            [
                FieldRowPanel(
                    [
                        FieldPanel('invoice', classname='col6'),
                        FieldPanel('amount', classname='col6'),
                    ],
                    classname='compact-row',
                ),
                FieldRowPanel(
                    [
                        FieldPanel('payment_date', classname='col6'),
                        FieldPanel('payment_method', classname='col6'),
                    ],
                    classname='compact-row',
                ),
                FieldRowPanel(
                    [
                        FieldPanel('transaction_id', classname='col12'),
                    ],
                    classname='compact-row',
                ),
            ],
            heading='Payment Details',
            classname='compact-panel',
        ),
    ]


modeladmin_register(InvoiceAdmin)
modeladmin_register(BillingPaymentAdmin)
