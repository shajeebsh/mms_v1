"""
Tests for critical business logic: payments and dues
"""
import logging
from decimal import Decimal
from datetime import date, timedelta
from django.test import TestCase, TransactionTestCase
from django.db import transaction
from django.utils import timezone

from .models import Family, Member, MembershipDues, Payment


class PaymentBusinessLogicTest(TransactionTestCase):
    """Test critical payment business logic"""

    def setUp(self):
        self.family = Family.objects.create(name="Test Family")
        
        # Create multiple unpaid dues
        self.due1 = MembershipDues.objects.create(
            family=self.family,
            year=2024,
            month=1,
            amount_due=Decimal("10.00"),
            due_date=date(2024, 1, 1),
            is_paid=False
        )
        self.due2 = MembershipDues.objects.create(
            family=self.family,
            year=2024,
            month=2,
            amount_due=Decimal("10.00"),
            due_date=date(2024, 2, 1),
            is_paid=False
        )
        self.due3 = MembershipDues.objects.create(
            family=self.family,
            year=2024,
            month=3,
            amount_due=Decimal("10.00"),
            due_date=date(2024, 3, 1),
            is_paid=False
        )

    def test_payment_marks_dues_as_paid(self):
        """Test that payment correctly marks associated dues as paid"""
        payment = Payment.objects.create(
            family=self.family,
            amount=Decimal("20.00"),
            payment_method="cash",
            payment_date=date.today()
        )
        
        # Associate first two dues with payment
        payment.membership_dues.add(self.due1, self.due2)
        
        # Mark dues as paid
        for due in payment.membership_dues.all():
            due.is_paid = True
            due.save()
        
        # Verify dues are marked as paid
        self.due1.refresh_from_db()
        self.due2.refresh_from_db()
        self.due3.refresh_from_db()
        
        self.assertTrue(self.due1.is_paid)
        self.assertTrue(self.due2.is_paid)
        self.assertFalse(self.due3.is_paid)  # Not associated with payment

    def test_payment_total_matches_dues_amount(self):
        """Test that payment amount matches total of associated dues"""
        payment = Payment.objects.create(
            family=self.family,
            amount=Decimal("30.00"),
            payment_method="upi",
            payment_date=date.today()
        )
        
        payment.membership_dues.add(self.due1, self.due2, self.due3)
        
        total_dues = payment.total_dues_covered
        self.assertEqual(total_dues, Decimal("30.00"))
        self.assertEqual(total_dues, payment.amount)

    def test_partial_payment_scenario(self):
        """Test scenario where payment covers only some dues"""
        # Create payment for first due only
        payment = Payment.objects.create(
            family=self.family,
            amount=Decimal("10.00"),
            payment_method="cash",
            payment_date=date.today()
        )
        
        payment.membership_dues.add(self.due1)
        self.due1.is_paid = True
        self.due1.save()
        
        # Verify only first due is paid
        self.due1.refresh_from_db()
        self.due2.refresh_from_db()
        self.due3.refresh_from_db()
        
        self.assertTrue(self.due1.is_paid)
        self.assertFalse(self.due2.is_paid)
        self.assertFalse(self.due3.is_paid)

    def test_multiple_payments_for_same_family(self):
        """Test multiple payments for the same family"""
        payment1 = Payment.objects.create(
            family=self.family,
            amount=Decimal("10.00"),
            payment_method="cash",
            payment_date=date.today()
        )
        payment1.membership_dues.add(self.due1)
        self.due1.is_paid = True
        self.due1.save()
        
        payment2 = Payment.objects.create(
            family=self.family,
            amount=Decimal("20.00"),
            payment_method="bank",
            payment_date=date.today()
        )
        payment2.membership_dues.add(self.due2, self.due3)
        self.due2.is_paid = True
        self.due3.is_paid = True
        self.due2.save()
        self.due3.save()
        
        # Verify all payments exist
        payments = Payment.objects.filter(family=self.family)
        self.assertEqual(payments.count(), 2)
        
        # Verify all dues are paid
        self.due1.refresh_from_db()
        self.due2.refresh_from_db()
        self.due3.refresh_from_db()
        self.assertTrue(self.due1.is_paid)
        self.assertTrue(self.due2.is_paid)
        self.assertTrue(self.due3.is_paid)


class DuesBusinessLogicTest(TestCase):
    """Test critical dues business logic"""

    def setUp(self):
        self.family = Family.objects.create(name="Test Family")

    def test_dues_overdue_calculation(self):
        """Test overdue calculation logic"""
        # Create overdue due
        overdue_due = MembershipDues.objects.create(
            family=self.family,
            year=2023,
            month=1,
            amount_due=Decimal("10.00"),
            due_date=date(2023, 1, 1),
            is_paid=False
        )
        
        self.assertTrue(overdue_due.is_overdue)
        
        # Mark as paid - should no longer be overdue
        overdue_due.is_paid = True
        overdue_due.save()
        self.assertFalse(overdue_due.is_overdue)

    def test_dues_unique_constraint(self):
        """Test that same family cannot have duplicate dues for same year/month"""
        MembershipDues.objects.create(
            family=self.family,
            year=2024,
            month=1,
            amount_due=Decimal("10.00"),
            due_date=date(2024, 1, 1)
        )
        
        # Try to create duplicate
        with self.assertRaises(Exception):  # IntegrityError
            MembershipDues.objects.create(
                family=self.family,
                year=2024,
                month=1,
                amount_due=Decimal("10.00"),
                due_date=date(2024, 1, 1)
            )

    def test_dues_auto_due_date(self):
        """Test automatic due date calculation"""
        due = MembershipDues(
            family=self.family,
            year=2024,
            month=5,
            amount_due=Decimal("10.00")
        )
        due.save()
        
        self.assertEqual(due.due_date, date(2024, 5, 1))

    def test_dues_ordering(self):
        """Test that dues are ordered correctly"""
        due1 = MembershipDues.objects.create(
            family=self.family,
            year=2024,
            month=3,
            amount_due=Decimal("10.00"),
            due_date=date(2024, 3, 1)
        )
        due2 = MembershipDues.objects.create(
            family=self.family,
            year=2024,
            month=1,
            amount_due=Decimal("10.00"),
            due_date=date(2024, 1, 1)
        )
        due3 = MembershipDues.objects.create(
            family=self.family,
            year=2024,
            month=2,
            amount_due=Decimal("10.00"),
            due_date=date(2024, 2, 1)
        )
        
        # Query should return in order: year desc, month desc
        dues = MembershipDues.objects.filter(family=self.family)
        self.assertEqual(dues[0], due1)  # Latest month first
        self.assertEqual(dues[1], due2)  # Then earlier months
        self.assertEqual(dues[2], due3)

    def test_bulk_dues_generation(self):
        """Test generating dues for multiple families"""
        family1 = Family.objects.create(name="Family 1")
        family2 = Family.objects.create(name="Family 2")
        family3 = Family.objects.create(name="Family 3")
        
        year = 2024
        month = 6
        
        # Generate dues for all families
        for family in [family1, family2, family3]:
            MembershipDues.objects.create(
                family=family,
                year=year,
                month=month,
                amount_due=Decimal("10.00"),
                due_date=date(year, month, 1)
            )
        
        # Verify all dues were created
        dues = MembershipDues.objects.filter(year=year, month=month)
        self.assertEqual(dues.count(), 3)
        
        # Verify each family has one due
        for family in [family1, family2, family3]:
            family_dues = dues.filter(family=family)
            self.assertEqual(family_dues.count(), 1)

