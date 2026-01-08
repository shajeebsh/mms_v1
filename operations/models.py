from django.db import models
from django.utils import timezone
from membership.models import Member


class AuditoriumBooking(models.Model):
    BOOKING_STATUS = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    event_name = models.CharField(max_length=200)
    organizer = models.CharField(max_length=200)
    contact_person = models.CharField(max_length=200)
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=20)
    booking_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    expected_attendees = models.PositiveIntegerField()
    purpose = models.TextField()
    special_requirements = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=BOOKING_STATUS, default='pending')
    approved_by = models.CharField(max_length=100, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.event_name} - {self.booking_date}"

    class Meta:
        ordering = ['-booking_date', '-start_time']
