from decimal import Decimal

from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from accounting.models import Account, AccountCategory
from education.models import Class, StudentEnrollment, StudentFeePayment, Teacher
from membership.models import Member


class Command(BaseCommand):
    help = "Seed sample data for Education module to cover payment scenarios"

    def handle(self, *args, **options):
        self.stdout.write("Seeding Education sample data...")
        with transaction.atomic():
            self._ensure_accounts_categories()
            members = self._ensure_members()
            teachers = self._create_teachers()
            classes = self._create_classes(teachers)
            self._create_enrollments_and_payments(members, classes)
        self.stdout.write(
            self.style.SUCCESS("Education sample data seeded successfully")
        )

    def _ensure_accounts_categories(self):
        asset_cat = AccountCategory.objects.filter(category_type="asset").first()
        if not asset_cat:
            asset_cat = AccountCategory.objects.create(
                name="Assets", category_type="asset"
            )
        revenue_cat = AccountCategory.objects.filter(category_type="revenue").first()
        if not revenue_cat:
            revenue_cat = AccountCategory.objects.create(
                name="Revenue", category_type="revenue"
            )

        def next_code(prefix):
            existing = set(
                Account.objects.filter(code__startswith=prefix).values_list(
                    "code", flat=True
                )
            )
            start = int(prefix) * 10 + 1 if len(prefix) == 3 else int(prefix)
            for i in range(1, 200):
                candidate = f"{prefix}{i}"
                if candidate not in existing:
                    return candidate
            return f"{prefix}999"

        cash = Account.objects.filter(
            category__category_type="asset",
            name__in=["Cash in Hand", "Main Cash", "Petty Cash"],
        ).first()
        if not cash:
            Account.objects.create(
                name="Cash in Hand", code=next_code("100"), category=asset_cat
            )

        bank = Account.objects.filter(
            category__category_type="asset", name="Bank Account"
        ).first()
        if not bank:
            Account.objects.create(
                name="Bank Account", code=next_code("100"), category=asset_cat
            )

        revenue = Account.objects.filter(
            category__category_type="revenue",
            name__in=["Education Fees", "Education Revenue"],
        ).first()
        if not revenue:
            Account.objects.create(
                name="Education Fees", code=next_code("400"), category=revenue_cat
            )

    def _ensure_members(self):
        members = list(Member.objects.all()[:4])
        if len(members) < 4:
            # Create minimal members if not enough in DB
            base_idx = len(members)
            for i in range(base_idx, 4):
                members.append(
                    Member.objects.create(
                        first_name=f"Student{i+1}",
                        last_name="Demo",
                        gender="M",
                        phone=f"+1-555-01{i+1:02d}",
                        whatsapp_number=f"+1-555-09{i+1:02d}",
                        email=f"student{i+1}@example.com",
                    )
                )
        return members

    def _create_teachers(self):
        t1, _ = Teacher.objects.get_or_create(name="Teacher Alpha")
        t2, _ = Teacher.objects.get_or_create(name="Teacher Beta")
        return [t1, t2]

    def _create_classes(self, teachers):
        c1, _ = Class.objects.get_or_create(
            name="Python 101",
            defaults={
                "grade_level": "high",
                "subject": "other",
                "teacher": teachers[0],
                "course_fee": Decimal("1000.00"),
                "is_active": True,
            },
        )
        c2, _ = Class.objects.get_or_create(
            name="Quran Basics",
            defaults={
                "grade_level": "elementary",
                "subject": "quran",
                "teacher": teachers[1],
                "course_fee": Decimal("0.00"),
                "is_active": True,
            },
        )
        c3, _ = Class.objects.get_or_create(
            name="Arabic Intro",
            defaults={
                "grade_level": "middle",
                "subject": "arabic",
                "teacher": teachers[1],
                "course_fee": Decimal("500.00"),
                "is_active": True,
            },
        )
        return [c1, c2, c3]

    def _create_enrollments_and_payments(self, members, classes):
        today = timezone.now().date()

        # Scenario A: Partial then paid across two payments (cash + bank)
        enr_a, _ = StudentEnrollment.objects.get_or_create(
            student=members[0], class_instance=classes[0]
        )
        StudentFeePayment.objects.create(
            enrollment=enr_a,
            amount=Decimal("500.00"),
            date=today,
            payment_method="cash",
            reference_number="EDU-A-001",
            remarks="Initial cash part payment",
        )
        StudentFeePayment.objects.create(
            enrollment=enr_a,
            amount=Decimal("500.00"),
            date=today,
            payment_method="bank_transfer",
            reference_number="EDU-A-002",
            remarks="Bank transfer to complete fee",
        )

        # Scenario B: Exempt course fee (no payment needed)
        enr_b, _ = StudentEnrollment.objects.get_or_create(
            student=members[1], class_instance=classes[1]
        )
        enr_b.update_payment_status()

        # Scenario C: Pending (no payment yet)
        enr_c, _ = StudentEnrollment.objects.get_or_create(
            student=members[2], class_instance=classes[2]
        )
        enr_c.update_payment_status()

        # Scenario D: Paid in full via UPI
        enr_d, _ = StudentEnrollment.objects.get_or_create(
            student=members[3], class_instance=classes[2]
        )
        StudentFeePayment.objects.create(
            enrollment=enr_d,
            amount=Decimal("500.00"),
            date=today,
            payment_method="upi",
            reference_number="EDU-D-001",
            remarks="Full fee via UPI",
        )

        # Scenario E: Update payment amount to test idempotent signal update
        enr_e, _ = StudentEnrollment.objects.get_or_create(
            student=members[0], class_instance=classes[2]
        )
        pay_e = StudentFeePayment.objects.create(
            enrollment=enr_e,
            amount=Decimal("200.00"),
            date=today,
            payment_method="cash",
            reference_number="EDU-E-001",
            remarks="Initial small payment",
        )
        pay_e.amount = Decimal("300.00")
        pay_e.reference_number = "EDU-E-001-UPDATED"
        pay_e.save(update_fields=["amount", "reference_number", "updated_at"])

        # Scenario F: Create then delete payment to validate transaction deletion
        enr_f, _ = StudentEnrollment.objects.get_or_create(
            student=members[1], class_instance=classes[2]
        )
        pay_f = StudentFeePayment.objects.create(
            enrollment=enr_f,
            amount=Decimal("100.00"),
            date=today,
            payment_method="cash",
            reference_number="EDU-F-001",
            remarks="To be deleted",
        )
        pay_f.delete()
