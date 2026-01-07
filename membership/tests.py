import logging
from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone
from wagtail.models import Site

from home.models import SystemSettings

from .models import HouseRegistration, Member, MembershipDues, Payment, VitalRecord


class HouseRegistrationModelTest(TestCase):
    """Test cases for HouseRegistration model"""

    def setUp(self):
        self.house = HouseRegistration.objects.create(
            house_name="Test House",
            house_number="H-001",
        )

    def test_house_creation(self):
        """Test that a house registration can be created"""
        self.assertEqual(self.house.house_name, "Test House")
        self.assertEqual(str(self.house), "Test House")

    def test_house_str_representation(self):
        """Test house string representation"""
        self.assertEqual(str(self.house), "Test House")


class MemberModelTest(TestCase):
    """Test cases for Member model"""

    def setUp(self):
        self.member = Member.objects.create(
            first_name="John",
            last_name="Doe",
            date_of_birth=date(1990, 1, 1),
            gender="M",
            phone="1234567890",
            email="john@example.com",
            is_active=True,
        )

    def test_member_creation(self):
        """Test that a member can be created"""
        self.assertEqual(self.member.first_name, "John")
        self.assertEqual(self.member.last_name, "Doe")
        self.assertTrue(self.member.is_active)

    def test_member_full_name_property(self):
        """Test the full_name property"""
        self.assertEqual(self.member.full_name, "John Doe")

    def test_member_str_representation(self):
        """Test member string representation"""
        self.assertEqual(str(self.member), "John Doe")


class MembershipDuesModelTest(TestCase):
    """Test cases for MembershipDues model"""

    def setUp(self):
        self.house = HouseRegistration.objects.create(house_name="Test House")
        # Create a default site for SystemSettings
        self.site = Site.objects.create(
            hostname="test.com", port=80, site_name="Test Site", is_default_site=True
        )
        SystemSettings.objects.create(
            site=self.site, monthly_membership_dues=Decimal("10.00")
        )

    def test_membership_dues_creation(self):
        """Test that membership dues can be created"""
        due = MembershipDues.objects.create(
            house=self.house,
            year=2024,
            month=1,
            amount_due=Decimal("10.00"),
            due_date=date(2024, 1, 1),
        )
        self.assertEqual(due.house, self.house)
        self.assertEqual(due.year, 2024)
        self.assertEqual(due.month, 1)
        self.assertEqual(due.amount_due, Decimal("10.00"))

    def test_membership_dues_unique_together(self):
        """Test that duplicate dues for same family/year/month are prevented"""
        MembershipDues.objects.create(
            house=self.house,
            year=2024,
            month=1,
            amount_due=Decimal("10.00"),
            due_date=date(2024, 1, 1),
        )
        # Try to create duplicate
        with self.assertRaises(Exception):  # IntegrityError
            MembershipDues.objects.create(
                house=self.house,
                year=2024,
                month=1,
                amount_due=Decimal("10.00"),
                due_date=date(2024, 1, 1),
            )

    def test_membership_dues_auto_calculate_due_date(self):
        """Test that due_date is auto-calculated if not provided"""
        due = MembershipDues(
            house=self.house, year=2024, month=3, amount_due=Decimal("10.00")
        )
        due.save()
        self.assertEqual(due.due_date, date(2024, 3, 1))

    def test_membership_dues_uses_system_settings(self):
        """Test that new dues use system settings for default amount"""
        SystemSettings.objects.update(monthly_membership_dues=Decimal("15.00"))
        due = MembershipDues(
            house=self.house,
            year=2024,
            month=4,
            amount_due=Decimal("10.00"),  # Will be overridden by system settings
        )
        due.save()
        # The amount should be updated from system settings
        self.assertEqual(due.amount_due, Decimal("15.00"))

    def test_membership_dues_validation(self):
        """Test that amount_due must be greater than zero"""
        due = MembershipDues(
            house=self.house,
            year=2024,
            month=1,
            amount_due=Decimal("0.00"),
            due_date=date(2024, 1, 1),
        )
        with self.assertRaises(ValidationError):
            due.clean()

    def test_membership_dues_is_overdue_property(self):
        """Test the is_overdue property"""
        # Create an overdue due
        overdue_due = MembershipDues.objects.create(
            house=self.house,
            year=2023,
            month=1,
            amount_due=Decimal("10.00"),
            due_date=date(2023, 1, 1),
            is_paid=False,
        )
        self.assertTrue(overdue_due.is_overdue)

        # Create a paid due (not overdue even if past due date)
        paid_due = MembershipDues.objects.create(
            house=self.house,
            year=2023,
            month=2,
            amount_due=Decimal("10.00"),
            due_date=date(2023, 2, 1),
            is_paid=True,
        )
        self.assertFalse(paid_due.is_overdue)

        # Create a future due (not overdue)
        future_due = MembershipDues.objects.create(
            house=self.house,
            year=2025,
            month=1,
            amount_due=Decimal("10.00"),
            due_date=date(2025, 1, 1),
            is_paid=False,
        )
        self.assertFalse(future_due.is_overdue)


class PaymentModelTest(TestCase):
    """Test cases for Payment model"""

    def setUp(self):
        self.house = HouseRegistration.objects.create(house_name="Test House")

    def test_payment_creation(self):
        """Test that a payment can be created"""
        payment = Payment.objects.create(
            house=self.house,
            amount=Decimal("50.00"),
            payment_method="cash",
            payment_date=date.today(),
        )
        self.assertEqual(payment.house, self.house)
        self.assertEqual(payment.amount, Decimal("50.00"))
        self.assertTrue(payment.receipt_number.startswith("REC-"))

    def test_payment_auto_generate_receipt_number(self):
        """Test that receipt number is auto-generated"""
        payment1 = Payment.objects.create(
            house=self.house,
            amount=Decimal("10.00"),
            payment_method="cash",
            payment_date=date.today(),
        )
        self.assertTrue(payment1.receipt_number.startswith("REC-"))

        payment2 = Payment.objects.create(
            house=self.house,
            amount=Decimal("20.00"),
            payment_method="upi",
            payment_date=date.today(),
        )
        # Receipt numbers should be different
        self.assertNotEqual(payment1.receipt_number, payment2.receipt_number)

    def test_payment_total_dues_covered_property(self):
        """Test the total_dues_covered property"""
        # Create dues
        due1 = MembershipDues.objects.create(
            house=self.house,
            year=2024,
            month=1,
            amount_due=Decimal("10.00"),
            due_date=date(2024, 1, 1),
        )
        due2 = MembershipDues.objects.create(
            house=self.house,
            year=2024,
            month=2,
            amount_due=Decimal("10.00"),
            due_date=date(2024, 2, 1),
        )

        # Create payment and associate dues
        payment = Payment.objects.create(
            house=self.house,
            amount=Decimal("20.00"),
            payment_method="cash",
            payment_date=date.today(),
        )
        payment.membership_dues.add(due1, due2)

        self.assertEqual(payment.total_dues_covered, Decimal("20.00"))

    def test_payment_str_representation(self):
        """Test payment string representation"""
        payment = Payment.objects.create(
            house=self.house,
            amount=Decimal("50.00"),
            payment_method="cash",
            payment_date=date.today(),
        )
        self.assertIn("Receipt #", str(payment))
        self.assertIn(str(self.house), str(payment))


class VitalRecordModelTest(TestCase):
    """Test cases for VitalRecord model"""

    def setUp(self):
        self.member = Member.objects.create(first_name="John", last_name="Doe")

    def test_vital_record_creation(self):
        """Test that a vital record can be created"""
        record = VitalRecord.objects.create(
            record_type="birth",
            date=date(1990, 1, 1),
            member=self.member,
            details="Born at hospital",
            location="City Hospital",
        )
        self.assertEqual(record.record_type, "birth")
        self.assertEqual(record.member, self.member)

    def test_vital_record_str_representation(self):
        """Test vital record string representation"""
        record = VitalRecord.objects.create(
            record_type="nikah", date=date(2020, 1, 1), member=self.member
        )
        self.assertIn("nikah", str(record).lower())
        self.assertIn("John Doe", str(record))
