from django.utils.html import format_html
from wagtail.admin.panels import FieldPanel, FieldRowPanel, MultiFieldPanel
from wagtail_modeladmin.options import ModelAdmin, modeladmin_register
from .models import Account, AccountCategory, Transaction, JournalEntry


class AccountCategoryAdmin(ModelAdmin):
    model = AccountCategory
    menu_label = 'Account Categories'
    menu_icon = 'tag'
    list_display = ('name', 'category_type')
    search_fields = ('name',)
    add_to_admin_menu = False
    panels = [
        MultiFieldPanel(
            [
                FieldRowPanel(
                    [
                        FieldPanel('name', classname='col6'),
                        FieldPanel('category_type', classname='col6'),
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
            heading='Category Details',
            classname='compact-panel',
        ),
    ]


class AccountAdmin(ModelAdmin):
    model = Account
    menu_label = 'Chart of Accounts'
    menu_icon = 'list-ul'
    list_display = ('code', 'name', 'category', 'is_active')
    list_filter = ('category', 'is_active')
    search_fields = ('code', 'name')
    add_to_admin_menu = False
    panels = [
        MultiFieldPanel(
            [
                FieldRowPanel(
                    [
                        FieldPanel('code', classname='col4'),
                        FieldPanel('name', classname='col4'),
                        FieldPanel('category', classname='col4'),
                    ],
                    classname='compact-row',
                ),
                FieldRowPanel(
                    [
                        FieldPanel('is_active', classname='col12'),
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
            heading='Account Details',
            classname='compact-panel',
        ),
    ]


class TransactionAdmin(ModelAdmin):
    model = Transaction
    menu_label = 'Ledger Transactions'
    menu_icon = 'transfer'
    list_display = ('date', 'name', 'description', 'reference', 'transaction_type', 'colored_amount')
    search_fields = ('name', 'description', 'reference')
    list_filter = ('date',)
    add_to_admin_menu = False
    panels = [
        MultiFieldPanel(
            [
                FieldRowPanel(
                    [
                        FieldPanel('date', classname='col6'),
                        FieldPanel('name', classname='col6'),
                    ],
                    classname='compact-row',
                ),
                FieldRowPanel(
                    [
                        FieldPanel('reference', classname='col6'),
                        FieldPanel('description', classname='col6'),
                    ],
                    classname='compact-row',
                ),
            ],
            heading='Transaction Details',
            classname='compact-panel',
        ),
    ]

    def colored_amount(self, obj):
        """Display amount with color based on transaction type"""
        amount = obj.amount
        if obj.is_income:
            return format_html(
                '<span style="color: #28a745; font-weight: bold;">₹{}</span>',
                amount
            )
        else:
            return format_html(
                '<span style="color: #dc3545; font-weight: bold;">₹{}</span>',
                amount
            )
    colored_amount.short_description = 'Amount'


class JournalEntryAdmin(ModelAdmin):
    model = JournalEntry
    menu_label = 'Journal Entries'
    menu_icon = 'form'
    list_display = ('transaction', 'account', 'debit', 'credit')
    list_filter = ('account',)
    add_to_admin_menu = False
    panels = [
        MultiFieldPanel(
            [
                FieldRowPanel(
                    [
                        FieldPanel('transaction', classname='col6'),
                        FieldPanel('account', classname='col6'),
                    ],
                    classname='compact-row',
                ),
                FieldRowPanel(
                    [
                        FieldPanel('debit', classname='col6'),
                        FieldPanel('credit', classname='col6'),
                    ],
                    classname='compact-row',
                ),
                FieldRowPanel(
                    [
                        FieldPanel('memo', classname='col12'),
                    ],
                    classname='compact-row',
                ),
            ],
            heading='Journal Entry Details',
            classname='compact-panel',
        ),
    ]


modeladmin_register(AccountAdmin)
modeladmin_register(AccountCategoryAdmin)
modeladmin_register(TransactionAdmin)
modeladmin_register(JournalEntryAdmin)
