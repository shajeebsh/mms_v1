from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db import transaction
from .models import StudentFeePayment
from accounting.models import Transaction, JournalEntry, Account, AccountCategory

@receiver(post_save, sender=StudentFeePayment)
def handle_payment_save(sender, instance, created, **kwargs):
    # 1. Update Enrollment Status
    instance.enrollment.update_payment_status()

    # 2. Accounting Integration
    # Create or update Transaction
    # For now, we only handle creation logic simply. 
    # To properly update, we'd need to link the Transaction to this payment (e.g. via foreign key or generic relation).
    # Since we didn't add a field to link them yet, we will just create a new one on Create 
    # and ideally logic should be idempotent or we accept this limitation for the MVP.
    
    if created:
        with transaction.atomic():
            # Create Transaction
            trans = Transaction.objects.create(
                date=instance.date,
                description=f"Course Fee: {instance.enrollment.class_instance.name} - {instance.enrollment.student.full_name}",
                reference=instance.reference_number or f"PAY-{instance.id}"
            )

            # Get Categories (Create if missing)
            asset_cat, _ = AccountCategory.objects.get_or_create(
                name="Current Assets",
                defaults={'category_type': 'asset'}
            )
            revenue_cat, _ = AccountCategory.objects.get_or_create(
                name="Education Revenue",
                defaults={'category_type': 'revenue'}
            )

            # Get Accounts (Fallback to creating if missing)
            # 1. Debit: Cash/Bank (Asset) - defaulting to 'Cash in Hand'
            cash_account, _ = Account.objects.get_or_create(
                name="Cash in Hand",
                defaults={'code': '1001', 'category': asset_cat}
            )
            
            # 2. Credit: Education Revenue (Revenue)
            revenue_account, _ = Account.objects.get_or_create(
                name="Education Fees",
                defaults={'code': '4001', 'category': revenue_cat}
            )

            # Debit Cash
            JournalEntry.objects.create(
                transaction=trans,
                account=cash_account,
                debit=instance.amount,
                credit=0
            )

            # Credit Revenue
            JournalEntry.objects.create(
                transaction=trans,
                account=revenue_account,
                debit=0,
                credit=instance.amount
            )


@receiver(post_delete, sender=StudentFeePayment)
def handle_payment_delete(sender, instance, **kwargs):
    instance.enrollment.update_payment_status()
    # Note: deleting the transaction is harder without a direct link. 
    # For MVP, we skip auto-deleting the accounting ledger entry to avoid accidental data loss.
