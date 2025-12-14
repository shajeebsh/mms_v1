from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from membership.models import Member


class CommitteeType(models.Model):
    """Types of committees"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Committee Type"
        verbose_name_plural = "Committee Types"


class Committee(models.Model):
    """Committees within the mosque"""
    name = models.CharField(max_length=200)
    committee_type = models.ForeignKey(CommitteeType, on_delete=models.CASCADE)
    description = models.TextField(blank=True)
    chairperson = models.ForeignKey(Member, on_delete=models.SET_NULL, null=True, blank=True, related_name='chaired_committees')
    secretary = models.ForeignKey(Member, on_delete=models.SET_NULL, null=True, blank=True, related_name='secretary_committees')
    established_date = models.DateField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Committee"
        verbose_name_plural = "Committees"


class CommitteeMember(models.Model):
    """Members of committees"""
    committee = models.ForeignKey(Committee, on_delete=models.CASCADE)
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    role = models.CharField(max_length=100, blank=True)  # e.g., "Member", "Treasurer", etc.
    joined_date = models.DateField()
    left_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.member} - {self.committee}"

    class Meta:
        verbose_name = "Committee Member"
        verbose_name_plural = "Committee Members"
        unique_together = ['committee', 'member']


class Meeting(models.Model):
    """Committee meetings"""
    MEETING_TYPE_CHOICES = [
        ('regular', 'Regular Meeting'),
        ('emergency', 'Emergency Meeting'),
        ('special', 'Special Meeting'),
    ]

    committee = models.ForeignKey(Committee, on_delete=models.CASCADE)
    meeting_type = models.CharField(max_length=20, choices=MEETING_TYPE_CHOICES, default='regular')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    scheduled_date = models.DateField()
    scheduled_time = models.TimeField()
    venue = models.CharField(max_length=200, default="Mosque Conference Room")
    agenda = models.TextField(blank=True)
    minutes = models.TextField(blank=True)
    decisions = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=[
        ('scheduled', 'Scheduled'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], default='scheduled')
    actual_start_time = models.DateTimeField(null=True, blank=True)
    actual_end_time = models.DateTimeField(null=True, blank=True)
    chairperson = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='chaired_meetings')
    minute_taker = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='minutes_taken')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_meetings')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.committee.name} - {self.title} ({self.scheduled_date})"

    class Meta:
        verbose_name = "Meeting"
        verbose_name_plural = "Meetings"
        ordering = ['-scheduled_date', '-scheduled_time']


class MeetingAttendee(models.Model):
    """Attendees of meetings"""
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE)
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    attended = models.BooleanField(default=False)
    apology_reason = models.TextField(blank=True)

    def __str__(self):
        return f"{self.member} - {self.meeting}"

    class Meta:
        verbose_name = "Meeting Attendee"
        verbose_name_plural = "Meeting Attendees"
        unique_together = ['meeting', 'member']


class MeetingAttachment(models.Model):
    """Attachments for meetings (agenda, minutes, documents)"""
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='committee/meetings/')
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    attachment_type = models.CharField(max_length=50, choices=[
        ('agenda', 'Agenda'),
        ('minutes', 'Minutes'),
        ('document', 'Document'),
        ('presentation', 'Presentation'),
        ('other', 'Other'),
    ], default='document')

    def __str__(self):
        return f"{self.meeting} - {self.title}"

    class Meta:
        verbose_name = "Meeting Attachment"
        verbose_name_plural = "Meeting Attachments"


class Trustee(models.Model):
    """Trustees of the mosque"""
    member = models.OneToOneField(Member, on_delete=models.CASCADE)
    position = models.CharField(max_length=100, choices=[
        ('president', 'President'),
        ('vice_president', 'Vice President'),
        ('secretary', 'Secretary'),
        ('treasurer', 'Treasurer'),
        ('trustee', 'Trustee'),
    ])
    appointed_date = models.DateField()
    term_end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.member} - {self.get_position_display()}"

    class Meta:
        verbose_name = "Trustee"
        verbose_name_plural = "Trustees"


class TrusteeMeeting(models.Model):
    """Trustee board meetings"""
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    scheduled_date = models.DateField()
    scheduled_time = models.TimeField()
    venue = models.CharField(max_length=200, default="Mosque Board Room")
    agenda = models.TextField(blank=True)
    minutes = models.TextField(blank=True)
    decisions = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=[
        ('scheduled', 'Scheduled'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], default='scheduled')
    actual_start_time = models.DateTimeField(null=True, blank=True)
    actual_end_time = models.DateTimeField(null=True, blank=True)
    chairperson = models.ForeignKey(Trustee, on_delete=models.SET_NULL, null=True, blank=True, related_name='chaired_trustee_meetings')
    minute_taker = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='trustee_meeting_minutes_taken')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Trustee Meeting - {self.title} ({self.scheduled_date})"

    class Meta:
        verbose_name = "Trustee Meeting"
        verbose_name_plural = "Trustee Meetings"
        ordering = ['-scheduled_date', '-scheduled_time']


class TrusteeMeetingAttendee(models.Model):
    """Attendees of trustee meetings"""
    trustee_meeting = models.ForeignKey(TrusteeMeeting, on_delete=models.CASCADE)
    trustee = models.ForeignKey(Trustee, on_delete=models.CASCADE)
    attended = models.BooleanField(default=False)
    apology_reason = models.TextField(blank=True)

    def __str__(self):
        return f"{self.trustee} - {self.trustee_meeting}"

    class Meta:
        verbose_name = "Trustee Meeting Attendee"
        verbose_name_plural = "Trustee Meeting Attendees"
        unique_together = ['trustee_meeting', 'trustee']


class TrusteeMeetingAttachment(models.Model):
    """Attachments for trustee meetings"""
    trustee_meeting = models.ForeignKey(TrusteeMeeting, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='committee/trustee_meetings/')
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    attachment_type = models.CharField(max_length=50, choices=[
        ('agenda', 'Agenda'),
        ('minutes', 'Minutes'),
        ('document', 'Document'),
        ('presentation', 'Presentation'),
        ('financial_report', 'Financial Report'),
        ('other', 'Other'),
    ], default='document')

    def __str__(self):
        return f"{self.trustee_meeting} - {self.title}"

    class Meta:
        verbose_name = "Trustee Meeting Attachment"
        verbose_name_plural = "Trustee Meeting Attachments"
