import logging
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

logger = logging.getLogger(__name__)


class Ward(models.Model):
    name = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Wards"


class Taluk(models.Model):
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Taluks"


class City(models.Model):
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Cities"


class State(models.Model):
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "States"


class Country(models.Model):
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Countries"


class PostalCode(models.Model):
    code = models.CharField(max_length=10, unique=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.code

    class Meta:
        verbose_name_plural = "Postal Codes"


class HouseRegistration(models.Model):
    house_name = models.CharField(max_length=200, blank=True)
    house_number = models.CharField(max_length=50, blank=True)

    ward = models.ForeignKey(Ward, on_delete=models.SET_NULL, null=True, blank=True)
    taluk = models.ForeignKey(Taluk, on_delete=models.SET_NULL, null=True, blank=True)
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, blank=True)
    state = models.ForeignKey(State, on_delete=models.SET_NULL, null=True, blank=True)
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, blank=True)
    postal_code = models.ForeignKey(PostalCode, on_delete=models.SET_NULL, null=True, blank=True)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        display = self.house_name or self.house_number
        return display or f"House #{self.pk}"

    class Meta:
        verbose_name = "House Registration"
        verbose_name_plural = "House Registrations"


class Member(models.Model):
    GENDER_CHOICES = [
        ("M", "Male"),
        ("F", "Female"),
        ("O", "Other"),
    ]

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    # family field removed - replaced with individual text fields for now
    is_head_of_family = models.BooleanField(default=False, help_text="Is this person head of family?")
    
    MARITAL_STATUS_CHOICES = [
        ("S", "Single"),
        ("M", "Married"),
        ("W", "Widowed"),
        ("D", "Divorced"),
    ]
    marital_status = models.CharField(max_length=1, choices=MARITAL_STATUS_CHOICES, blank=True)
    
    BLOOD_GROUP_CHOICES = [
        ("A+", "A+"), ("A-", "A-"),
        ("B+", "B+"), ("B-", "B-"),
        ("AB+", "AB+"), ("AB-", "AB-"),
        ("O+", "O+"), ("O-", "O-"),
    ]
    blood_group = models.CharField(max_length=5, choices=BLOOD_GROUP_CHOICES, blank=True, verbose_name="Blood Group")
    
    aadhaar_no = models.CharField(max_length=12, blank=True, verbose_name="Aadhaar Card No")
    phone = models.CharField(max_length=20, blank=True)
    whatsapp_number = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    
    # Keep existing text fields and add new dropdown fields
    ward_no = models.CharField(max_length=20, blank=True, verbose_name="Ward No")
    taluk = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True, default="India")
    
    address = models.TextField(blank=True, help_text="Personal address if different from family")
    postal_code = models.CharField(max_length=10, blank=True)
    
    # New dropdown fields
    ward_no_dropdown = models.ForeignKey(Ward, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Ward No (Dropdown)")
    taluk_dropdown = models.ForeignKey(Taluk, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Taluk (Dropdown)")
    city_dropdown = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="City (Dropdown)")
    state_dropdown = models.ForeignKey(State, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="State (Dropdown)")
    country_dropdown = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Country (Dropdown)")
    postal_code_dropdown = models.ForeignKey(PostalCode, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Postal Code (Dropdown)")
    
    photo = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class MembershipDues(models.Model):
    """Monthly membership dues for families - ₹10 per couple per month"""

    house = models.ForeignKey(
        HouseRegistration, on_delete=models.CASCADE, related_name="membership_dues"
    )
    year = models.PositiveIntegerField(help_text="Year for the dues")
    month = models.PositiveIntegerField(help_text="Month for the dues (1-12)")
    amount_due = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("10.00"),
        help_text="Amount due (matches System Settings)",
    )
    is_paid = models.BooleanField(default=False)
    due_date = models.DateField(help_text="Due date for payment")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["house", "year", "month"]
        ordering = ["-year", "-month", "house__house_name", "house__house_number"]
        verbose_name = "Membership Due"
        verbose_name_plural = "Membership Dues"

    def __str__(self):
        return f"{self.house} - {self.year}-{self.month:02d} (₹{self.amount_due})"

    def clean(self):
        if self.amount_due <= 0:
            raise ValidationError("Amount due must be greater than zero")

    def save(self, *args, **kwargs):
        # Auto-calculate due date if not set
        if not self.due_date:
            from datetime import date
            self.due_date = date(self.year, self.month, 1)

        # Use system setting for default amount if new and amount is default
        if self.pk is None and self.amount_due == Decimal("10.00"):
            from home.models import SystemSettings
            from wagtail.models import Site

            try:
                # Try to get the default site
                site = Site.objects.filter(is_default_site=True).first()
                if not site:
                    site = Site.objects.first()

                if site:
                    settings = SystemSettings.for_site(site)
                    self.amount_due = settings.monthly_membership_dues
            except (SystemSettings.DoesNotExist, Site.DoesNotExist, AttributeError) as e:
                # Fallback to hardcoded default if any issues with settings/site
                logger.warning(
                    f"Could not load system settings for membership dues, using default: {e}"
                )
            except Exception as e:
                # Catch any other unexpected errors
                logger.error(
                    f"Unexpected error loading system settings for membership dues: {e}",
                    exc_info=True
                )

        super().save(*args, **kwargs)

    @property
    def is_overdue(self):
        """Check if the dues are overdue"""
        return not self.is_paid and self.due_date < timezone.now().date()


class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ("cash", "Cash"),
        ("bank", "Bank Transfer"),
        ("upi", "UPI"),
    ]

    house = models.ForeignKey(
        HouseRegistration, on_delete=models.CASCADE, related_name="payments"
    )
    amount = models.DecimalField(
        max_digits=10, decimal_places=2, help_text="Payment amount"
    )
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHOD_CHOICES)
    receipt_number = models.CharField(
        max_length=20,
        unique=True,
        editable=False,
        help_text="Auto-generated receipt number",
    )
    payment_date = models.DateField(default=timezone.now)
    notes = models.TextField(blank=True, help_text="Payment notes")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    # Many-to-many relationship for bulk payments
    membership_dues = models.ManyToManyField(
        MembershipDues,
        blank=True,
        related_name="payments",
        help_text="Dues covered by this payment",
    )

    class Meta:
        ordering = ["-payment_date", "-created_at"]
        verbose_name = "Payment"
        verbose_name_plural = "Payments"

    def __str__(self):
        return f"Receipt #{self.receipt_number} - {self.house} - ₹{self.amount}"

    def save(self, *args, **kwargs):
        if not self.receipt_number:
            # Generate auto receipt number: REC-YYYYMMDD-XXXX
            today = timezone.now().date()
            prefix = f"REC-{today.strftime('%Y%m%d')}"
            # Find the next available number for today
            existing_receipts = Payment.objects.filter(
                receipt_number__startswith=prefix
            ).order_by("-receipt_number")

            if existing_receipts.exists():
                last_number = int(
                    existing_receipts.first().receipt_number.split("-")[-1]
                )
                next_number = last_number + 1
            else:
                next_number = 1

            self.receipt_number = f"{prefix}-{next_number:04d}"

        super().save(*args, **kwargs)

    @property
    def total_dues_covered(self):
        """Total amount of dues covered by this payment"""
        return sum(due.amount_due for due in self.membership_dues.all())


class VitalRecord(models.Model):
    RECORD_TYPE_CHOICES = [
        ("birth", "Birth"),
        ("death", "Death"),
        ("nikah", "Nikah (Marriage)"),
        ("janazah", "Janazah (Funeral)"),
        ("aqiqah", "Aqiqah"),
        ("shahada", "Shahada"),
        ("other", "Other"),
    ]

    record_type = models.CharField(max_length=20, choices=RECORD_TYPE_CHOICES)
    date = models.DateField()
    member = models.ForeignKey(
        Member, on_delete=models.CASCADE, related_name="vital_records"
    )
    details = models.TextField(
        blank=True, help_text="Additional details about the record"
    )
    location = models.CharField(
        max_length=200, blank=True, help_text="Location where the event occurred"
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.record_type} - {self.member.full_name} ({self.date})"

    class Meta:
        ordering = ["-date"]
