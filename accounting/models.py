from django.db import models
from django.utils import timezone

class AccountCategory(models.Model):
    """Assets, Liabilities, Equity, Revenue, Expenses"""
    CATEGORY_TYPES = [
        ('asset', 'Asset'),
        ('liability', 'Liability'),
        ('equity', 'Equity'),
        ('revenue', 'Revenue'),
        ('expense', 'Expense'),
    ]
    name = models.CharField(max_length=100)
    category_type = models.CharField(max_length=20, choices=CATEGORY_TYPES)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} ({self.get_category_type_display()})"

    class Meta:
        verbose_name_plural = "Account Categories"
    wagtail_reference_index_ignore = True

class Account(models.Model):
    wagtail_reference_index_ignore = True
    """Specific accounts (e.g., 'HDFC Bank', 'Main Mosque Cash')"""
    name = models.CharField(max_length=100)
    category = models.ForeignKey(AccountCategory, on_delete=models.PROTECT, related_name='accounts')
    code = models.CharField(max_length=20, unique=True, help_text="Accounting code (e.g., 1001)")
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.code} - {self.name}"

class Transaction(models.Model):
    wagtail_reference_index_ignore = True
    """Represents a financial event"""
    date = models.DateField(default=timezone.now)
    name = models.CharField(
        max_length=200,
        blank=True,
        help_text="Name of the person/entity related to this transaction",
    )
    description = models.CharField(max_length=255)
    reference = models.CharField(max_length=100, blank=True, help_text="External ref (e.g. Receipt #)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.name:
            return f"{self.date} - {self.name} - {self.description}"
        return f"{self.date} - {self.description}"

    @property
    def total_debit(self):
        """Sum of all debit entries for this transaction"""
        return sum(entry.debit for entry in self.entries.all())

    @property
    def total_credit(self):
        """Sum of all credit entries for this transaction"""
        return sum(entry.credit for entry in self.entries.all())

    @property
    def transaction_type(self):
        """Determine transaction type based on accounts involved"""
        entries = self.entries.select_related('account__category').all()
        for entry in entries:
            cat_type = entry.account.category.category_type
            if cat_type == 'revenue' and entry.credit > 0:
                return 'Income'
            if cat_type == 'expense' and entry.debit > 0:
                return 'Expense'
        return 'Transfer'

    @property
    def amount(self):
        """Returns the transaction amount (debit total, which equals credit total)"""
        return self.total_debit

    @property
    def is_income(self):
        """Check if this is an income transaction"""
        return self.transaction_type == 'Income'

class JournalEntry(models.Model):
    wagtail_reference_index_ignore = True
    """Double-entry lines (Debit/Credit)"""
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name='entries')
    account = models.ForeignKey(Account, on_delete=models.PROTECT, related_name='journal_entries')
    debit = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    credit = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    memo = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.account.name}: Dr {self.debit} / Cr {self.credit}"
