from django.db import transaction
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from accounting.models import Account, AccountCategory, JournalEntry, Transaction

from .models import StudentFeePayment


@receiver(post_save, sender=StudentFeePayment)
def handle_payment_save(sender, instance, created, **kwargs):
    instance.enrollment.update_payment_status()

    with transaction.atomic():
        if created or not instance.transaction:
            trans = Transaction.objects.create(
                date=instance.date,
                name=instance.enrollment.student.full_name,
                description=f"Course Fee: {instance.enrollment.class_instance.name}",
                reference=instance.reference_number or f"PAY-{instance.id}",
            )
            instance.transaction = trans
            instance.save(update_fields=["transaction"])

            asset_cat = AccountCategory.objects.filter(category_type="asset").first()
            if not asset_cat:
                asset_cat = AccountCategory.objects.create(name="Assets", category_type="asset")
            revenue_cat = AccountCategory.objects.filter(category_type="revenue").first()
            if not revenue_cat:
                revenue_cat = AccountCategory.objects.create(name="Revenue", category_type="revenue")

            if instance.payment_method == "cash":
                debit_account = Account.objects.filter(
                    category__category_type="asset",
                    name__in=["Cash in Hand", "Main Cash", "Petty Cash"],
                ).first()
                if not debit_account:
                    existing_codes = set(
                        Account.objects.filter(code__startswith="100").values_list(
                            "code", flat=True
                        )
                    )
                    next_code = "1001"
                    for i in range(1, 100):
                        candidate = f"100{i}"
                        if candidate not in existing_codes:
                            next_code = candidate
                            break
                    debit_account = Account.objects.create(
                        name="Cash in Hand", code=next_code, category=asset_cat
                    )
            else:
                debit_account = Account.objects.filter(
                    category__category_type="asset",
                    name__in=["Bank Account"],
                ).first()
                if not debit_account:
                    existing_codes = set(
                        Account.objects.filter(code__startswith="100").values_list(
                            "code", flat=True
                        )
                    )
                    next_code = "1002"
                    for i in range(2, 200):
                        candidate = f"10{i:02d}"
                        if candidate not in existing_codes:
                            next_code = candidate
                            break
                    debit_account = Account.objects.create(
                        name="Bank Account", code=next_code, category=asset_cat
                    )

            revenue_account = Account.objects.filter(
                category__category_type="revenue",
                name__in=["Education Fees", "Education Revenue"],
            ).first()
            if not revenue_account:
                existing_codes = set(
                    Account.objects.filter(code__startswith="400").values_list(
                        "code", flat=True
                    )
                )
                next_code = "4001"
                for i in range(1, 100):
                    candidate = f"400{i}"
                    if candidate not in existing_codes:
                        next_code = candidate
                        break
                revenue_account = Account.objects.create(
                    name="Education Fees", code=next_code, category=revenue_cat
                )

            JournalEntry.objects.create(
                transaction=trans,
                account=debit_account,
                debit=instance.amount,
                credit=0,
                memo=instance.reference_number or "",
            )
            JournalEntry.objects.create(
                transaction=trans,
                account=revenue_account,
                debit=0,
                credit=instance.amount,
                memo=instance.reference_number or "",
            )
        else:
            trans = instance.transaction
            entries = list(trans.entries.all())
            for entry in entries:
                if entry.debit > 0:
                    entry.debit = instance.amount
                if entry.credit > 0:
                    entry.credit = instance.amount
                entry.memo = instance.reference_number or entry.memo
                entry.save(update_fields=["debit", "credit", "memo"])


@receiver(post_delete, sender=StudentFeePayment)
def handle_payment_delete(sender, instance, **kwargs):
    instance.enrollment.update_payment_status()
    if instance.transaction_id:
        try:
            instance.transaction.delete()
        except Exception:
            pass
