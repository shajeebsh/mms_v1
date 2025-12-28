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

class Account(models.Model):
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
    """Represents a financial event"""
    date = models.DateField(default=timezone.now)
    description = models.CharField(max_length=255)
    reference = models.CharField(max_length=100, blank=True, help_text="External ref (e.g. Receipt #)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.date} - {self.description}"

class JournalEntry(models.Model):
    """Double-entry lines (Debit/Credit)"""
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name='entries')
    account = models.ForeignKey(Account, on_delete=models.PROTECT, related_name='journal_entries')
    debit = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    credit = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    memo = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.account.name}: Dr {self.debit} / Cr {self.credit}"
