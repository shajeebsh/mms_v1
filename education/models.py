from django.db import models
from django.utils import timezone
from membership.models import Member


class Teacher(models.Model):
    member = models.OneToOneField(Member, on_delete=models.CASCADE, related_name='teacher_profile')
    specialization = models.CharField(max_length=200, blank=True)
    qualifications = models.TextField(blank=True)
    hire_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Teacher: {self.member.full_name}"

    class Meta:
        verbose_name = 'Teacher'
        verbose_name_plural = 'Teachers'


class Class(models.Model):
    GRADE_LEVELS = [
        ('preschool', 'Preschool'),
        ('kindergarten', 'Kindergarten'),
        ('elementary', 'Elementary'),
        ('middle', 'Middle School'),
        ('high', 'High School'),
        ('adult', 'Adult Education'),
    ]

    SUBJECTS = [
        ('quran', 'Quran Studies'),
        ('arabic', 'Arabic Language'),
        ('islamic_studies', 'Islamic Studies'),
        ('hadith', 'Hadith'),
        ('fiqh', 'Fiqh'),
        ('seerah', 'Seerah'),
        ('other', 'Other'),
    ]

    name = models.CharField(max_length=200)
    grade_level = models.CharField(max_length=20, choices=GRADE_LEVELS)
    subject = models.CharField(max_length=20, choices=SUBJECTS)
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True, related_name='classes')
    max_students = models.PositiveIntegerField(default=20)
    description = models.TextField(blank=True)
    schedule = models.TextField(blank=True, help_text="Class schedule details")
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.get_subject_display()}"

    @property
    def current_enrollment(self):
        return self.enrollments.filter(status='active').count()

    class Meta:
        verbose_name = 'Class'
        verbose_name_plural = 'Classes'


class StudentEnrollment(models.Model):
    ENROLLMENT_STATUS = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('graduated', 'Graduated'),
        ('transferred', 'Transferred'),
    ]

    student = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='enrollments')
    class_instance = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='enrollments')
    enrollment_date = models.DateField(default=timezone.now)
    status = models.CharField(max_length=20, choices=ENROLLMENT_STATUS, default='active')
    grade = models.CharField(max_length=10, blank=True, help_text="Current grade/mark")
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.student.full_name} - {self.class_instance.name}"

    class Meta:
        unique_together = ('student', 'class_instance')
        ordering = ['-enrollment_date']
