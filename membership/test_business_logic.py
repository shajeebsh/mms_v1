"""
Tests for critical business logic: payments and dues
"""
import logging
from decimal import Decimal
from datetime import date, timedelta
from django.test import TestCase, TransactionTestCase
from django.db import transaction
from django.utils import timezone

from .models import HouseRegistration, Member, MembershipDues, Payment


class PaymentBusinessLogicTest(TransactionTestCase):
    """Test critical payment business logic"""

    def setUp(self):
        self.house = HouseRegistration.objects.create(house_name="Test House")
        
        # Create multiple unpaid dues
        self.due1 = MembershipDues.objects.create(
            house=self.house,
            year=2024,
            month=1,
            amount_due=Decimal("10.00"),
            due_date=date(2024, 1, 1),
            is_paid=False
        )
        self.due2 = MembershipDues.objects.create(
            house=self.house,
            year=2024,
            month=2,
            amount_due=Decimal("10.00"),
            due_date=date(2024, 2, 1),
            is_paid=False
        )
        self.due3 = MembershipDues.objects.create(
            house=self.house,
            year=2024,
            month=3,
            amount_due=Decimal("10.00"),
            due_date=date(2024, 3, 1),
            is_paid=False
        )

    def test_payment_marks_dues_as_paid(self):
        """Test that payment correctly marks associated dues as paid"""
        payment = Payment.objects.create(
            house=self.house,
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
            house=self.house,
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
            house=self.house,
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
        """Test multiple payments for the same house"""
        payment1 = Payment.objects.create(
            house=self.house,
            amount=Decimal("10.00"),
            payment_method="cash",
            payment_date=date.today()
        )
        payment1.membership_dues.add(self.due1)
        self.due1.is_paid = True
        self.due1.save()
        
        payment2 = Payment.objects.create(
            house=self.house,
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
        payments = Payment.objects.filter(house=self.house)
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
        self.house = HouseRegistration.objects.create(house_name="Test House")

    def test_dues_overdue_calculation(self):
        """Test overdue calculation logic"""
        # Create overdue due
        overdue_due = MembershipDues.objects.create(
            house=self.house,
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
            house=self.house,
            year=2024,
            month=1,
            amount_due=Decimal("10.00"),
            due_date=date(2024, 1, 1)
        )
        
        # Try to create duplicate
        with self.assertRaises(Exception):  # IntegrityError
            MembershipDues.objects.create(
                house=self.house,
                year=2024,
                month=1,
                amount_due=Decimal("10.00"),
                due_date=date(2024, 1, 1)
            )

    def test_dues_auto_due_date(self):
        """Test automatic due date calculation"""
        due = MembershipDues(
            house=self.house,
            year=2024,
            month=5,
            amount_due=Decimal("10.00")
        )
        due.save()
        
        self.assertEqual(due.due_date, date(2024, 5, 1))

    def test_dues_ordering(self):
        """Test that dues are ordered correctly"""
        due1 = MembershipDues.objects.create(
            house=self.house,
            year=2024,
            month=3,
            amount_due=Decimal("10.00"),
            due_date=date(2024, 3, 1)
        )
        due2 = MembershipDues.objects.create(
            house=self.house,
            year=2024,
            month=1,
            amount_due=Decimal("10.00"),
            due_date=date(2024, 1, 1)
        )
        due3 = MembershipDues.objects.create(
            house=self.house,
            year=2024,
            month=2,
            amount_due=Decimal("10.00"),
            due_date=date(2024, 2, 1)
        )
        
        # Query should return in order: year desc, month desc
        dues = MembershipDues.objects.filter(house=self.house)
        self.assertEqual(dues[0], due1)  # Latest month first
        self.assertEqual(dues[1], due2)  # Then earlier months
        self.assertEqual(dues[2], due3)

    def test_bulk_dues_generation(self):
        """Test generating dues for multiple houses"""
        house1 = HouseRegistration.objects.create(house_name="House 1")
        house2 = HouseRegistration.objects.create(house_name="House 2")
        house3 = HouseRegistration.objects.create(house_name="House 3")
        
        year = 2024
        month = 6
        
        # Generate dues for all houses
        for house in [house1, house2, house3]:
            MembershipDues.objects.create(
                house=house,
                year=year,
                month=month,
                amount_due=Decimal("10.00"),
                due_date=date(year, month, 1)
            )
        
        # Verify all dues were created
        dues = MembershipDues.objects.filter(year=year, month=month)
        self.assertEqual(dues.count(), 3)
        
        # Verify each house has one due
        for house in [house1, house2, house3]:
            house_dues = dues.filter(house=house)
            self.assertEqual(house_dues.count(), 1)

