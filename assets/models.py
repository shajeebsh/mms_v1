from django.db import models
from django.utils import timezone


class Shop(models.Model):
    SHOP_TYPES = [
        ('retail', 'Retail Shop'),
        ('food', 'Food Vendor'),
        ('service', 'Service Provider'),
        ('other', 'Other'),
    ]

    name = models.CharField(max_length=200)
    shop_type = models.CharField(max_length=20, choices=SHOP_TYPES)
    owner_name = models.CharField(max_length=200, blank=True)
    contact_info = models.TextField(blank=True)
    location = models.CharField(max_length=200, blank=True)
    monthly_rent = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    lease_start = models.DateField(null=True, blank=True)
    lease_end = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.get_shop_type_display()})"


class PropertyUnit(models.Model):
    UNIT_TYPES = [
        ('apartment', 'Apartment'),
        ('office', 'Office Space'),
        ('hall', 'Community Hall'),
        ('parking', 'Parking Space'),
        ('other', 'Other'),
    ]

    name = models.CharField(max_length=200)
    unit_type = models.CharField(max_length=20, choices=UNIT_TYPES)
    address = models.TextField()
    size_sqm = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    monthly_rent = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    tenant_name = models.CharField(max_length=200, blank=True)
    tenant_contact = models.TextField(blank=True)
    lease_start = models.DateField(null=True, blank=True)
    lease_end = models.DateField(null=True, blank=True)
    is_occupied = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.address}"
