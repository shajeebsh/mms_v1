from django.db import models
from django.utils import timezone
from decimal import Decimal

class Invoice(models.Model):
    """Consolidated bill for a specific period"""
    INVOICE_STATUS = [
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('paid', 'Paid'),
        ('partially_paid', 'Partially Paid'),
        ('cancelled', 'Cancelled'),
        ('overdue', 'Overdue'),
    ]
    
    invoice_number = models.CharField(max_length=50, unique=True)
    
    # Can be linked to a House Registration or a Shop/Tenant
    house = models.ForeignKey('membership.HouseRegistration', on_delete=models.SET_NULL, null=True, blank=True, related_name='invoices')
    shop = models.ForeignKey('assets.Shop', on_delete=models.SET_NULL, null=True, blank=True, related_name='invoices')
    property_unit = models.ForeignKey('assets.PropertyUnit', on_delete=models.SET_NULL, null=True, blank=True, related_name='invoices')
    
    date_issued = models.DateField(default=timezone.now)
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=INVOICE_STATUS, default='draft')
    
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Invoice {self.invoice_number} ({self.get_status_display()})"

    @property
    def balance_due(self):
        return self.total_amount - self.amount_paid

class InvoiceLineItem(models.Model):
    """Individual charges on an invoice"""
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='line_items')
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    
    # Optional links to original source
    membership_due = models.ForeignKey('membership.MembershipDues', on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return f"{self.description} - ₹{self.amount}"

class BillingPayment(models.Model):
    """Unified payment intake linked to Invoices"""
    PAYMENT_METHODS = [
        ('cash', 'Cash'),
        ('bank', 'Bank Transfer'),
        ('upi', 'UPI'),
        ('check', 'Check'),
    ]
    
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_date = models.DateField(default=timezone.now)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    transaction_id = models.CharField(max_length=100, blank=True, help_text="e.g. UPI Ref, Check #")
    
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        if is_new:
            # 1. Update Invoice amount_paid and status
            invoice = self.invoice
            invoice.amount_paid += self.amount
            if invoice.balance_due <= 0:
                invoice.status = 'paid'
            elif invoice.amount_paid > 0:
                invoice.status = 'partially_paid'
            invoice.save()
            
            # 2. Post to Accounting Ledger
            from accounting.models import Transaction, JournalEntry, Account
            tx = Transaction.objects.create(
                date=self.payment_date,
                description=f"Payment for Invoice {invoice.invoice_number}",
                reference=self.transaction_id or invoice.invoice_number
            )
            
            # Debit Asset (Cash/Bank) - simplified logic for now
            cash_account = Account.objects.get(code='1001')
            JournalEntry.objects.create(transaction=tx, account=cash_account, debit=self.amount)
            
            # Credit Revenue (Based on what was invoiced)
            # In a full system, this would be more complex (Accounts Receivable vs Revenue)
            # For simplicity, we credit the respective revenue account directly
            if invoice.house:
                rev_account = Account.objects.get(code='4002') # Dues Revenue
            elif invoice.shop:
                rev_account = Account.objects.get(code='4003') # Rental Revenue
            else:
                rev_account = Account.objects.get(code='4001') # General Revenue
                
            JournalEntry.objects.create(transaction=tx, account=rev_account, credit=self.amount)

    def __str__(self):
        return f"Payment ₹{self.amount} for {self.invoice.invoice_number}"
