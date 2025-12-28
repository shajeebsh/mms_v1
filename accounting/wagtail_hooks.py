from wagtail_modeladmin.options import ModelAdmin, modeladmin_register
from .models import Account, AccountCategory, Transaction, JournalEntry

class AccountCategoryAdmin(ModelAdmin):
    model = AccountCategory
    menu_label = 'Account Categories'
    menu_icon = 'tag'
    list_display = ('name', 'category_type')
    search_fields = ('name',)
    add_to_admin_menu = False

class AccountAdmin(ModelAdmin):
    model = Account
    menu_label = 'Chart of Accounts'
    menu_icon = 'list-ul'
    list_display = ('code', 'name', 'category', 'is_active')
    list_filter = ('category', 'is_active')
    search_fields = ('code', 'name')
    add_to_admin_menu = False

class TransactionAdmin(ModelAdmin):
    model = Transaction
    menu_label = 'Ledger Transactions'
    menu_icon = 'transfer'
    list_display = ('date', 'description', 'reference')
    search_fields = ('description', 'reference')
    add_to_admin_menu = False

class JournalEntryAdmin(ModelAdmin):
    model = JournalEntry
    menu_label = 'Journal Entries'
    menu_icon = 'form'
    list_display = ('transaction', 'account', 'debit', 'credit')
    list_filter = ('account',)
    add_to_admin_menu = False

modeladmin_register(AccountAdmin)
modeladmin_register(AccountCategoryAdmin)
modeladmin_register(TransactionAdmin)
modeladmin_register(JournalEntryAdmin)
