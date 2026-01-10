import logging
from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone
from wagtail.models import Site

from home.models import SystemSettings

from .models import (
    HouseRegistration, Member, MembershipDues, Payment,
    Ward, Taluk, City, State, Country, PostalCode
)


class BulkPaymentViewTest(TestCase):
    """Integration tests for bulk payment view"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        self.client.login(username="testuser", password="testpass123")

        # Create geographic dependencies
        self.ward = Ward.objects.create(name="Test Ward")
        self.taluk = Taluk.objects.create(name="Test Taluk")
        self.city = City.objects.create(name="Test City")
        self.state = State.objects.create(name="Test State")
        self.country = Country.objects.create(name="Test Country")
        self.postal_code = PostalCode.objects.create(code="123456")

        # Create houses and dues
        self.house1 = HouseRegistration.objects.create(
            house_name="House 1", house_number="H-V1",
            ward=self.ward, taluk=self.taluk, city=self.city,
            state=self.state, country=self.country, postal_code=self.postal_code
        )
        self.house2 = HouseRegistration.objects.create(
            house_name="House 2", house_number="H-V2",
            ward=self.ward, taluk=self.taluk, city=self.city,
            state=self.state, country=self.country, postal_code=self.postal_code
        )

        # Create overdue dues
        self.due1 = MembershipDues.objects.create(
            house=self.house1,
            year=2023,
            month=1,
            amount_due=Decimal("10.00"),
            due_date=date(2023, 1, 1),
            is_paid=False,
        )
        self.due2 = MembershipDues.objects.create(
            house=self.house1,
            year=2023,
            month=2,
            amount_due=Decimal("10.00"),
            due_date=date(2023, 2, 1),
            is_paid=False,
        )
        self.due3 = MembershipDues.objects.create(
            house=self.house2,
            year=2023,
            month=1,
            amount_due=Decimal("10.00"),
            due_date=date(2023, 1, 1),
            is_paid=False,
        )

    def test_bulk_payment_get(self):
        """Test GET request to bulk payment view"""
        response = self.client.get(reverse("bulk_payment"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("houses", response.context)

    def test_bulk_payment_post_success(self):
        """Test successful bulk payment processing"""
        response = self.client.post(
            reverse("bulk_payment"),
            {
                "house_ids": [self.house1.id, self.house2.id],
                "payment_method": "cash",
                "payment_date": date.today().isoformat(),
                "notes": "Test payment",
            },
        )

        # Should redirect
        self.assertEqual(response.status_code, 302)

        # Check that dues are marked as paid
        self.due1.refresh_from_db()
        self.due2.refresh_from_db()
        self.due3.refresh_from_db()
        self.assertTrue(self.due1.is_paid)
        self.assertTrue(self.due2.is_paid)
        self.assertTrue(self.due3.is_paid)

        # Check that payment was created
        payment = Payment.objects.filter(house=self.house1).first()
        self.assertIsNotNone(payment)
        self.assertEqual(payment.amount, Decimal("30.00"))  # 10 + 10 + 10

    def test_bulk_payment_no_families_selected(self):
        """Test bulk payment with no houses selected"""
        response = self.client.post(
            reverse("bulk_payment"),
            {
                "payment_method": "cash",
            },
        )
        self.assertEqual(response.status_code, 302)  # Redirects with error message

    def test_bulk_payment_no_unpaid_dues(self):
        """Test bulk payment when houses have no unpaid dues"""
        # Mark all dues as paid
        MembershipDues.objects.update(is_paid=True)

        response = self.client.post(
            reverse("bulk_payment"),
            {
                "house_ids": [self.house1.id],
                "payment_method": "cash",
                "payment_date": date.today().isoformat(),
            },
        )
        self.assertEqual(response.status_code, 302)  # Redirects with warning


class OverdueReportViewTest(TestCase):
    """Integration tests for overdue report view"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        self.client.login(username="testuser", password="testpass123")

        # Create geographic dependencies
        self.ward = Ward.objects.create(name="Test Ward")
        self.taluk = Taluk.objects.create(name="Test Taluk")
        self.city = City.objects.create(name="Test City")
        self.state = State.objects.create(name="Test State")
        self.country = Country.objects.create(name="Test Country")
        self.postal_code = PostalCode.objects.create(code="123456")

        self.house = HouseRegistration.objects.create(
            house_name="Test House", house_number="H-V3",
            ward=self.ward, taluk=self.taluk, city=self.city,
            state=self.state, country=self.country, postal_code=self.postal_code
        )

        # Create overdue dues
        self.overdue_due = MembershipDues.objects.create(
            house=self.house,
            year=2023,
            month=1,
            amount_due=Decimal("10.00"),
            due_date=date(2023, 1, 1),
            is_paid=False,
        )

        # Create paid due (should not appear)
        self.paid_due = MembershipDues.objects.create(
            house=self.house,
            year=2023,
            month=2,
            amount_due=Decimal("10.00"),
            due_date=date(2023, 2, 1),
            is_paid=True,
        )

        # Create future due (should not appear)
        self.future_due = MembershipDues.objects.create(
            house=self.house,
            year=2025,
            month=1,
            amount_due=Decimal("10.00"),
            due_date=date(2025, 1, 1),
            is_paid=False,
        )

    def test_overdue_report_get(self):
        """Test GET request to overdue report view"""
        response = self.client.get(reverse("overdue_report"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("overdue_dues", response.context)
        self.assertIn("total_overdue_amount", response.context)

        # Should only show overdue, unpaid dues
        overdue_dues = response.context["overdue_dues"]
        self.assertEqual(overdue_dues.count(), 1)
        self.assertEqual(overdue_dues.first(), self.overdue_due)


class GenerateMonthlyDuesViewTest(TestCase):
    """Integration tests for generate monthly dues view"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        self.client.login(username="testuser", password="testpass123")

        # Create site and system settings
        self.site = Site.objects.create(
            hostname="test.com", port=80, site_name="Test Site", is_default_site=True
        )
        SystemSettings.objects.create(
            site=self.site, monthly_membership_dues=Decimal("10.00")
        )

        # Create geographic dependencies
        self.ward = Ward.objects.create(name="Test Ward")
        self.taluk = Taluk.objects.create(name="Test Taluk")
        self.city = City.objects.create(name="Test City")
        self.state = State.objects.create(name="Test State")
        self.country = Country.objects.create(name="Test Country")
        self.postal_code = PostalCode.objects.create(code="123456")

        self.house1 = HouseRegistration.objects.create(
            house_name="House 1", house_number="H-V4",
            ward=self.ward, taluk=self.taluk, city=self.city,
            state=self.state, country=self.country, postal_code=self.postal_code
        )
        self.house2 = HouseRegistration.objects.create(
            house_name="House 2", house_number="H-V5",
            ward=self.ward, taluk=self.taluk, city=self.city,
            state=self.state, country=self.country, postal_code=self.postal_code
        )

    def test_generate_monthly_dues_get(self):
        """Test GET request to generate monthly dues view"""
        response = self.client.get(reverse("generate_monthly_dues"))
        self.assertEqual(response.status_code, 200)

    def test_generate_monthly_dues_post_success(self):
        """Test successful generation of monthly dues"""
        year = 2024
        month = 3

        response = self.client.post(
            reverse("generate_monthly_dues"), {"year": year, "month": month}
        )

        self.assertEqual(response.status_code, 302)  # Redirects after success

        # Check that dues were created for all houses
        dues = MembershipDues.objects.filter(year=year, month=month)
        self.assertEqual(dues.count(), 2)

        for due in dues:
            self.assertEqual(due.amount_due, Decimal("10.00"))
            self.assertEqual(due.due_date, date(year, month, 1))

    def test_generate_monthly_dues_duplicate(self):
        """Test that duplicate dues are not created"""
        year = 2024
        month = 4

        # Create dues first time
        self.client.post(
            reverse("generate_monthly_dues"), {"year": year, "month": month}
        )

        # Try to create again
        response = self.client.post(
            reverse("generate_monthly_dues"), {"year": year, "month": month}
        )

        self.assertEqual(response.status_code, 302)  # Redirects with warning

        # Should still only have 2 dues (one per house)
        dues = MembershipDues.objects.filter(year=year, month=month)
        self.assertEqual(dues.count(), 2)

    def test_generate_monthly_dues_invalid_month(self):
        """Test generation with invalid month"""
        response = self.client.post(
            reverse("generate_monthly_dues"),
            {"year": 2024, "month": 13},  # Invalid month
        )
        self.assertEqual(response.status_code, 302)  # Redirects with error
