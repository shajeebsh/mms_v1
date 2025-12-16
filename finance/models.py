from django.db import models
from django.utils import timezone

from membership.models import Member


class DonationCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class ExpenseCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Donation(models.Model):
    DONATION_TYPES = [
        ("cash", "Cash"),
        ("check", "Check"),
        ("online", "Online"),
        ("other", "Other"),
    ]

    member = models.ForeignKey(
        Member,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="donations",
    )
    category = models.ForeignKey(
        DonationCategory, on_delete=models.SET_NULL, null=True, blank=True
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    donation_type = models.CharField(
        max_length=20, choices=DONATION_TYPES, default="cash"
    )
    date = models.DateField(default=timezone.now)
    notes = models.TextField(blank=True)
    receipt_number = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Donation by {self.member} - ₹{self.amount}"

    class Meta:
        ordering = ["-date"]


class Expense(models.Model):
    category = models.ForeignKey(
        ExpenseCategory, on_delete=models.SET_NULL, null=True, blank=True
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(default=timezone.now)
    description = models.TextField()
    approved_by = models.CharField(max_length=100, blank=True)
    vendor = models.CharField(max_length=200, blank=True)
    receipt_number = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Expense: {self.description} - ₹{self.amount}"

    class Meta:
        ordering = ["-date"]


class FinancialReport(models.Model):
    REPORT_PERIODS = [
        ("monthly", "Monthly"),
        ("quarterly", "Quarterly"),
        ("yearly", "Yearly"),
    ]

    period = models.CharField(max_length=20, choices=REPORT_PERIODS)
    start_date = models.DateField()
    end_date = models.DateField()
    total_donations = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_expenses = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    net_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    generated_at = models.DateTimeField(default=timezone.now)
    generated_by = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.period.title()} Report: {self.start_date} to {self.end_date}"

    class Meta:
        ordering = ["-generated_at"]
        ordering = ["-generated_at"]
