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


class PrayerTime(models.Model):
    PRAYER_NAMES = [
        ('fajr', 'Fajr'),
        ('dhuhr', 'Dhuhr'),
        ('asr', 'Asr'),
        ('maghrib', 'Maghrib'),
        ('isha', 'Isha'),
        ('jumah', 'Jumah'),
    ]

    date = models.DateField()
    prayer = models.CharField(max_length=20, choices=PRAYER_NAMES)
    time = models.TimeField()
    is_jumah = models.BooleanField(default=False)
    location = models.CharField(max_length=100, default='Main Mosque')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.prayer} - {self.date} at {self.time}"

    class Meta:
        unique_together = ('date', 'prayer', 'location')
        ordering = ['date', 'time']


class DigitalSignageContent(models.Model):
    CONTENT_TYPES = [
        ('announcement', 'Announcement'),
        ('event', 'Event'),
        ('prayer_times', 'Prayer Times'),
        ('quran_verse', 'Quran Verse'),
        ('image', 'Image'),
        ('video', 'Video'),
    ]

    title = models.CharField(max_length=200)
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPES)
    content = models.TextField(blank=True)
    image = models.ImageField(upload_to='signage/', null=True, blank=True)
    video_url = models.URLField(blank=True)
    display_start = models.DateTimeField()
    display_end = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    priority = models.PositiveIntegerField(default=1, help_text="Higher number = higher priority")
    created_by = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} ({self.get_content_type_display()})"

    class Meta:
        ordering = ['-priority', '-created_at']
