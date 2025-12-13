from django.db import models
from django.utils import timezone


class Family(models.Model):
    name = models.CharField(max_length=200, help_text="Family name or surname")
    address = models.TextField(blank=True, help_text="Family address")
    phone = models.CharField(max_length=20, blank=True, help_text="Primary phone number")
    email = models.EmailField(blank=True, help_text="Family email")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Families"


class Member(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    family = models.ForeignKey(Family, on_delete=models.CASCADE, related_name='members')
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class VitalRecord(models.Model):
    RECORD_TYPE_CHOICES = [
        ('birth', 'Birth'),
        ('death', 'Death'),
        ('marriage', 'Marriage'),
        ('baptism', 'Baptism'),
        ('confirmation', 'Confirmation'),
        ('other', 'Other'),
    ]

    record_type = models.CharField(max_length=20, choices=RECORD_TYPE_CHOICES)
    date = models.DateField()
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='vital_records')
    details = models.TextField(blank=True, help_text="Additional details about the record")
    location = models.CharField(max_length=200, blank=True, help_text="Location where the event occurred")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.record_type} - {self.member.full_name} ({self.date})"

    class Meta:
        ordering = ['-date']
