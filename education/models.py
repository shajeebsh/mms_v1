from django.db import models
from django.utils import timezone
from membership.models import Member


class Teacher(models.Model):
    wagtail_reference_index_ignore = True
    # Personal Details
    name = models.CharField(max_length=200, default="")
    father_name = models.CharField(max_length=200, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    blood_group = models.CharField(max_length=10, blank=True)
    
    # Address
    house_name = models.CharField(max_length=200, blank=True)
    place = models.CharField(max_length=200, blank=True)
    post_office = models.CharField(max_length=200, blank=True)
    via = models.CharField(max_length=200, blank=True)
    pin_code = models.CharField(max_length=20, blank=True)
    district = models.CharField(max_length=200, blank=True)
    state = models.CharField(max_length=200, blank=True)
    lsg_name = models.CharField(max_length=200, blank=True, help_text="Panchayath/Municipality/Corporation")

    # Contact
    land_phone = models.CharField(max_length=20, blank=True)
    mobile_no = models.CharField(max_length=20, blank=True)

    # Qualifications
    teaching_level = models.CharField(max_length=100, blank=True, choices=[
        ('primary', 'Primary'),
        ('secondary', 'Secondary'),
        ('higher_secondary', 'Higher Secondary'),
        ('other', 'Other'),
    ])
    islamic_qualification = models.CharField(max_length=200, blank=True)
    general_qualification = models.CharField(max_length=200, blank=True)

    # Organization & Membership
    organization = models.CharField(max_length=200, blank=True, choices=[('none', 'None'), ('other', 'Other')], default='none')
    membership_no = models.CharField(max_length=50, blank=True)
    unit_name = models.CharField(max_length=200, blank=True)
    unit_secretary_name = models.CharField(max_length=200, blank=True)
    unit_secretary_mobile = models.CharField(max_length=20, blank=True)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Teacher'
        verbose_name_plural = 'Teachers'


class Class(models.Model):
    wagtail_reference_index_ignore = True
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
    course_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Total fee for this course")
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
    wagtail_reference_index_ignore = True
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
    payment_status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('partial', 'Partial'),
        ('paid', 'Paid'),
        ('exempt', 'Exempt'),
    ], default='pending')
    grade = models.CharField(max_length=10, blank=True, help_text="Current grade/mark")

    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.student.full_name} - {self.class_instance.name}"

    class Meta:
        unique_together = ('student', 'class_instance')
        ordering = ['-enrollment_date']

    @property
    def total_paid(self):
        return sum(payment.amount for payment in self.payments.all())

    @property
    def balance_amount(self):
        return self.class_instance.course_fee - self.total_paid

    def update_payment_status(self):
        total = self.total_paid
        fee = self.class_instance.course_fee
        
        if fee == 0:
            self.status = 'exempt' # Or handle as paid? Using payment_status field instead.
            self.payment_status = 'exempt'
        elif total >= fee:
            self.payment_status = 'paid'
        elif total > 0:
            self.payment_status = 'partial'
        else:
            self.payment_status = 'pending'
        self.save()


class StudentFeePayment(models.Model):
    wagtail_reference_index_ignore = True
    PAYMENT_METHODS = [
        ('cash', 'Cash'),
        ('bank_transfer', 'Bank Transfer'),
        ('upi', 'UPI'),
        ('check', 'Check'),
        ('other', 'Other'),
    ]

    enrollment = models.ForeignKey(StudentEnrollment, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(default=timezone.now)
    reference_number = models.CharField(max_length=100, blank=True, help_text="Receipt No / Transaction ID")
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='cash')
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.enrollment.student.full_name} - {self.amount}"

    class Meta:
        ordering = ['-date']


class StudentAdmission(models.Model):
    wagtail_reference_index_ignore = True
    ADMISSION_STATUS = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('enrolled', 'Enrolled'),
    ]

    DOCUMENT_STATUS = [
        ('pending', 'Pending'),
        ('submitted', 'Submitted'),
        ('verified', 'Verified'),
        ('incomplete', 'Incomplete'),
    ]

    # Student Information
    student = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='admissions')
    admission_date = models.DateField(default=timezone.now)
    status = models.CharField(max_length=20, choices=ADMISSION_STATUS, default='pending')
    
    # Admission Details
    class_applied = models.ForeignKey(Class, on_delete=models.PROTECT, related_name='admission_applications')
    admission_number = models.CharField(max_length=50, unique=True, blank=True, help_text="Auto-generated admission ID")
    
    # Documents
    documents_status = models.CharField(max_length=20, choices=DOCUMENT_STATUS, default='pending')
    documents_remarks = models.TextField(blank=True, help_text="Notes about submitted documents")
    
    # Interview/Assessment
    interview_date = models.DateField(null=True, blank=True)
    interview_remarks = models.TextField(blank=True)
    
    # Additional Information
    parent_contact = models.CharField(max_length=20, blank=True)
    emergency_contact = models.CharField(max_length=20, blank=True)
    special_requirements = models.TextField(blank=True, help_text="Any special requirements or needs")
    
    # Administrative
    approved_by = models.CharField(max_length=200, blank=True, help_text="Name of person who approved")
    approval_date = models.DateField(null=True, blank=True)
    remarks = models.TextField(blank=True, help_text="General remarks about admission")
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.student.full_name} - {self.class_applied.name} ({self.get_status_display()})"

    class Meta:
        verbose_name = 'Student Admission'
        verbose_name_plural = 'Student Admissions'
        ordering = ['-admission_date']
