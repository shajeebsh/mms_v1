from django.db.models.signals import post_save
from django.dispatch import receiver
from finance.models import Donation, Expense
from membership.models import Payment as MemberPayment
from billing.models import BillingPayment
from .models import Transaction, JournalEntry, Account, AccountCategory, get_or_create_account

@receiver(post_save, sender=Donation)
def post_donation_to_ledger(sender, instance, created, **kwargs):
    if created:
        # 1. Create Transaction
        tx = Transaction.objects.create(
            date=instance.date,
            description=f"Donation: {instance.member} ({instance.category})",
            reference=instance.receipt_number
        )
        
        # 2. Debit Asset (Cash/Bank) - Assuming default "Main Cash" for now
        cash_account = get_or_create_account('1001', 'Main Cash', 'asset')
        JournalEntry.objects.create(transaction=tx, account=cash_account, debit=instance.amount)
        
        # 3. Credit Revenue (Donations)
        donation_account = get_or_create_account('4001', 'Donations Revenue', 'revenue')
        JournalEntry.objects.create(transaction=tx, account=donation_account, credit=instance.amount)

@receiver(post_save, sender=Expense)
def post_expense_to_ledger(sender, instance, created, **kwargs):
    if created:
        tx = Transaction.objects.create(
            date=instance.date,
            description=f"Expense: {instance.description}",
            reference=instance.receipt_number
        )
        
        # 1. Debit Expense
        expense_account = get_or_create_account('5001', 'General Expenses', 'expense')
        JournalEntry.objects.create(transaction=tx, account=expense_account, debit=instance.amount)
        
        # 2. Credit Asset (Cash/Bank)
        cash_account = get_or_create_account('1001', 'Main Cash', 'asset')
        JournalEntry.objects.create(transaction=tx, account=cash_account, credit=instance.amount)

@receiver(post_save, sender=MemberPayment)
def post_membership_payment_to_ledger(sender, instance, created, **kwargs):
    if created:
        tx = Transaction.objects.create(
            date=instance.payment_date,
            description=f"Membership Dues Payment: {instance.member}",
            reference=instance.receipt_number
        )
        
        # 1. Debit Asset (Cash)
        cash_account = get_or_create_account('1001', 'Main Cash', 'asset')
        JournalEntry.objects.create(transaction=tx, account=cash_account, debit=instance.amount)
        
        # 2. Credit Revenue (Membership Dues)
        dues_account = get_or_create_account('4002', 'Membership Dues Revenue', 'revenue')
        JournalEntry.objects.create(transaction=tx, account=dues_account, credit=instance.amount)
