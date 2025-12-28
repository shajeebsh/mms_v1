from django.db.models.signals import post_save
from django.dispatch import receiver
from finance.models import Donation, Expense
from membership.models import Payment as MemberPayment
from billing.models import BillingPayment
from .models import Transaction, JournalEntry, Account

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
        cash_account = Account.objects.get(code='1001') # Cash
        JournalEntry.objects.create(transaction=tx, account=cash_account, debit=instance.amount)
        
        # 3. Credit Revenue (Donations)
        donation_account = Account.objects.get(code='4001') # Donation Revenue
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
        expense_account = Account.objects.get(code='5001') # General Expense
        JournalEntry.objects.create(transaction=tx, account=expense_account, debit=instance.amount)
        
        # 2. Credit Asset (Cash/Bank)
        cash_account = Account.objects.get(code='1001') # Cash
        JournalEntry.objects.create(transaction=tx, account=cash_account, credit=instance.amount)

@receiver(post_save, sender=MemberPayment)
def post_membership_payment_to_ledger(sender, instance, created, **kwargs):
    if created:
        tx = Transaction.objects.create(
            date=instance.payment_date,
            description=f"Membership Dues Payment: {instance.family}",
            reference=instance.receipt_number
        )
        
        # 1. Debit Asset (Cash)
        cash_account = Account.objects.get(code='1001')
        JournalEntry.objects.create(transaction=tx, account=cash_account, debit=instance.amount)
        
        # 2. Credit Revenue (Membership Dues)
        dues_account = Account.objects.get(code='4002')
        JournalEntry.objects.create(transaction=tx, account=dues_account, credit=instance.amount)
