from django.db import transaction
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from accounting.models import Account, AccountCategory, JournalEntry, Transaction

from .models import StudentFeePayment


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
                reference=instance.reference_number or f"PAY-{instance.id}",
            )

            # Get Categories (Create if missing)
            asset_cat, _ = AccountCategory.objects.get_or_create(
                name="Current Assets", defaults={"category_type": "asset"}
            )
            revenue_cat, _ = AccountCategory.objects.get_or_create(
                name="Education Revenue", defaults={"category_type": "revenue"}
            )

            # Get Accounts (Fallback to creating if missing)
            # 1. Debit: Cash/Bank (Asset) - try existing cash accounts first
            cash_account = Account.objects.filter(
                category__category_type="asset",
                name__in=["Cash in Hand", "Main Cash", "Petty Cash"],
            ).first()

            if not cash_account:
                # Find next available code starting from 1001
                existing_codes = set(
                    Account.objects.filter(code__startswith="100").values_list(
                        "code", flat=True
                    )
                )
                next_code = "1001"
                for i in range(1, 100):  # Try 1001, 1002, 1003, etc.
                    candidate = f"100{i}"
                    if candidate not in existing_codes:
                        next_code = candidate
                        break

                cash_account = Account.objects.create(
                    name="Cash in Hand", code=next_code, category=asset_cat
                )

            # 2. Credit: Education Revenue (Revenue)
            revenue_account = Account.objects.filter(
                category__category_type="revenue",
                name__in=["Education Fees", "Education Revenue"],
            ).first()

            if not revenue_account:
                # Find next available code starting from 4001
                existing_codes = set(
                    Account.objects.filter(code__startswith="400").values_list(
                        "code", flat=True
                    )
                )
                next_code = "4001"
                for i in range(1, 100):  # Try 4001, 4002, 4003, etc.
                    candidate = f"400{i}"
                    if candidate not in existing_codes:
                        next_code = candidate
                        break

                revenue_account = Account.objects.create(
                    name="Education Fees", code=next_code, category=revenue_cat
                )

            # Debit Cash
            JournalEntry.objects.create(
                transaction=trans, account=cash_account, debit=instance.amount, credit=0
            )

            # Credit Revenue
            JournalEntry.objects.create(
                transaction=trans,
                account=revenue_account,
                debit=0,
                credit=instance.amount,
            )


@receiver(post_delete, sender=StudentFeePayment)
def handle_payment_delete(sender, instance, **kwargs):
    instance.enrollment.update_payment_status()
    # Note: deleting the transaction is harder without a direct link.
    # For MVP, we skip auto-deleting the accounting ledger entry to avoid accidental data loss.
