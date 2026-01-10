from decimal import Decimal
from datetime import date
from django.test import TestCase
from django.utils import timezone

from finance.models import DonationCategory, ExpenseCategory, Donation, Expense, FinancialReport
from membership.models import Member
from accounting.models import Account, AccountCategory


class DonationCategoryModelTest(TestCase):
    """Test cases for DonationCategory model"""

    def setUp(self):
        self.category = DonationCategory.objects.create(
            name="Zakat",
            description="Zakat donations"
        )

    def test_donation_category_creation(self):
        """Test that a donation category can be created"""
        self.assertEqual(self.category.name, "Zakat")
        self.assertEqual(str(self.category), "Zakat")

    def test_donation_category_unique(self):
        """Test that donation category names must be unique"""
        with self.assertRaises(Exception):  # IntegrityError
            DonationCategory.objects.create(name="Zakat")


class ExpenseCategoryModelTest(TestCase):
    """Test cases for ExpenseCategory model"""

    def setUp(self):
        self.category = ExpenseCategory.objects.create(
            name="Utilities",
            description="Utility expenses"
        )

    def test_expense_category_creation(self):
        """Test that an expense category can be created"""
        self.assertEqual(self.category.name, "Utilities")
        self.assertEqual(str(self.category), "Utilities")


class DonationModelTest(TestCase):
    """Test cases for Donation model"""

    def setUp(self):
        # Create required accounting accounts for signals
        asset_cat = AccountCategory.objects.create(name="Current Assets", category_type="asset")
        revenue_cat = AccountCategory.objects.create(name="Revenue", category_type="revenue")
        
        Account.objects.create(code="1001", name="Cash in Hand", category=asset_cat)
        Account.objects.create(code="4001", name="Donation Revenue", category=revenue_cat)
        
        self.member = Member.objects.create(
            first_name="John",
            last_name="Doe",
            # Family/House not strictly required for this test at DB level
        )
        self.category = DonationCategory.objects.create(name="Zakat")

    def test_donation_creation(self):
        """Test that a donation can be created"""
        donation = Donation.objects.create(
            member=self.member,
            category=self.category,
            amount=Decimal("100.00"),
            donation_type="cash",
            date=date.today()
        )
        self.assertEqual(donation.member, self.member)
        self.assertEqual(donation.amount, Decimal("100.00"))
        self.assertEqual(donation.donation_type, "cash")

    def test_donation_without_member(self):
        """Test that donation can be created without a member (anonymous)"""
        donation = Donation.objects.create(
            category=self.category,
            amount=Decimal("50.00"),
            donation_type="online",
            date=date.today()
        )
        self.assertIsNone(donation.member)
        self.assertEqual(donation.amount, Decimal("50.00"))

    def test_donation_str_representation(self):
        """Test donation string representation"""
        donation = Donation.objects.create(
            member=self.member,
            amount=Decimal("100.00"),
            date=date.today()
        )
        self.assertIn("John Doe", str(donation))
        self.assertIn("100.00", str(donation))

    def test_donation_ordering(self):
        """Test that donations are ordered by date descending"""
        donation1 = Donation.objects.create(
            member=self.member,
            amount=Decimal("100.00"),
            date=date(2024, 1, 1)
        )
        donation2 = Donation.objects.create(
            member=self.member,
            amount=Decimal("200.00"),
            date=date(2024, 2, 1)
        )
        
        donations = Donation.objects.all()
        self.assertEqual(donations[0], donation2)  # Latest first
        self.assertEqual(donations[1], donation1)


class ExpenseModelTest(TestCase):
    """Test cases for Expense model"""

    def setUp(self):
        # Create required accounting accounts for signals
        asset_cat = AccountCategory.objects.create(name="Current Assets", category_type="asset")
        expense_cat = AccountCategory.objects.create(name="Expenses", category_type="expense")
        
        Account.objects.create(code="1001", name="Cash in Hand", category=asset_cat)
        Account.objects.create(code="5001", name="General Expense", category=expense_cat)
        
        self.category = ExpenseCategory.objects.create(name="Utilities")

    def test_expense_creation(self):
        """Test that an expense can be created"""
        expense = Expense.objects.create(
            category=self.category,
            amount=Decimal("500.00"),
            date=date.today(),
            description="Electricity bill",
            approved_by="Admin",
            vendor="Power Company"
        )
        self.assertEqual(expense.amount, Decimal("500.00"))
        self.assertEqual(expense.description, "Electricity bill")
        self.assertEqual(expense.approved_by, "Admin")

    def test_expense_str_representation(self):
        """Test expense string representation"""
        expense = Expense.objects.create(
            category=self.category,
            amount=Decimal("500.00"),
            date=date.today(),
            description="Electricity bill"
        )
        self.assertIn("Electricity bill", str(expense))
        self.assertIn("500.00", str(expense))

    def test_expense_ordering(self):
        """Test that expenses are ordered by date descending"""
        expense1 = Expense.objects.create(
            category=self.category,
            amount=Decimal("100.00"),
            date=date(2024, 1, 1),
            description="Expense 1"
        )
        expense2 = Expense.objects.create(
            category=self.category,
            amount=Decimal("200.00"),
            date=date(2024, 2, 1),
            description="Expense 2"
        )
        
        expenses = Expense.objects.all()
        self.assertEqual(expenses[0], expense2)  # Latest first
        self.assertEqual(expenses[1], expense1)


class FinancialReportModelTest(TestCase):
    """Test cases for FinancialReport model"""

    def test_financial_report_creation(self):
        """Test that a financial report can be created"""
        report = FinancialReport.objects.create(
            period="monthly",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 31),
            total_donations=Decimal("1000.00"),
            total_expenses=Decimal("500.00"),
            net_amount=Decimal("500.00"),
            generated_by="Admin"
        )
        self.assertEqual(report.period, "monthly")
        self.assertEqual(report.total_donations, Decimal("1000.00"))
        self.assertEqual(report.net_amount, Decimal("500.00"))

    def test_financial_report_str_representation(self):
        """Test financial report string representation"""
        report = FinancialReport.objects.create(
            period="monthly",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 31),
            total_donations=Decimal("1000.00"),
            total_expenses=Decimal("500.00"),
            net_amount=Decimal("500.00")
        )
        self.assertIn("Monthly", str(report))
        self.assertIn("2024-01-01", str(report))

    def test_financial_report_ordering(self):
        """Test that financial reports are ordered by generated_at descending"""
        report1 = FinancialReport.objects.create(
            period="monthly",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 31),
            total_donations=Decimal("1000.00"),
            total_expenses=Decimal("500.00"),
            net_amount=Decimal("500.00")
        )
        # Wait a moment to ensure different timestamps
        import time
        time.sleep(0.01)
        report2 = FinancialReport.objects.create(
            period="monthly",
            start_date=date(2024, 2, 1),
            end_date=date(2024, 2, 29),
            total_donations=Decimal("2000.00"),
            total_expenses=Decimal("1000.00"),
            net_amount=Decimal("1000.00")
        )
        
        reports = FinancialReport.objects.all()
        self.assertEqual(reports[0], report2)  # Latest first
        self.assertEqual(reports[1], report1)
