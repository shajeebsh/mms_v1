from wagtail.admin.panels import FieldPanel, FieldRowPanel, MultiFieldPanel
from wagtail_modeladmin.options import ModelAdmin, modeladmin_register

from .models import Teacher, Class, StudentEnrollment, StudentFeePayment, StudentAdmission
from home.permission_helpers import ACLPermissionHelper
from wagtail import hooks
from django.urls import path
from . import views
from django import forms
from django.core.exceptions import ValidationError
from membership.models import Member


class TeacherAdmin(ModelAdmin):
    model = Teacher
    permission_helper_class = ACLPermissionHelper
    menu_label = 'Teachers'
    menu_icon = 'user'
    add_to_admin_menu = False  # Will be included in grouped menu
    list_display = ('name', 'mobile_no', 'teaching_level', 'is_active')
    list_filter = ('is_active', 'teaching_level', 'blood_group', 'district', 'state')
    search_fields = ('name', 'mobile_no', 'place', 'district')
    panels = [
        MultiFieldPanel([
            FieldRowPanel([
                FieldPanel('name', classname="col6"),
                FieldPanel('father_name', classname="col6"),
            ], classname="compact-row"),
            FieldRowPanel([
                FieldPanel('date_of_birth', classname="col6"),
                FieldPanel('blood_group', classname="col6"),
            ], classname="compact-row"),
        ], heading="Personal Details", classname="compact-panel"),
        MultiFieldPanel([
            FieldRowPanel([
                FieldPanel('house_name', classname="col6"),
                FieldPanel('place', classname="col6"),
            ], classname="compact-row"),
             FieldRowPanel([
                FieldPanel('post_office', classname="col4"),
                FieldPanel('via', classname="col4"),
                FieldPanel('pin_code', classname="col4"),
            ], classname="compact-row"),
            FieldRowPanel([
                FieldPanel('district', classname="col6"),
                FieldPanel('state', classname="col6"),
            ], classname="compact-row"),
            FieldRowPanel([
                FieldPanel('lsg_name', classname="col12"),
            ], classname="compact-row"),
        ], heading="Address Details", classname="compact-panel"),
        MultiFieldPanel([
            FieldRowPanel([
                FieldPanel('land_phone', classname="col6"),
                FieldPanel('mobile_no', classname="col6"),
            ], classname="compact-row"),
        ], heading="Contact", classname="compact-panel"),
        MultiFieldPanel([
            FieldRowPanel([
                FieldPanel('teaching_level', classname="col12"),
            ], classname="compact-row"),
            FieldRowPanel([
                FieldPanel('islamic_qualification', classname="col12"),
            ], classname="compact-row"),
            FieldRowPanel([
                FieldPanel('general_qualification', classname="col12"),
            ], classname="compact-row"),
        ], heading="Qualifications", classname="compact-panel"),
        MultiFieldPanel([
            FieldRowPanel([
                FieldPanel('organization', classname="col6"),
                FieldPanel('membership_no', classname="col6"),
            ], classname="compact-row"),
             FieldRowPanel([
                FieldPanel('unit_name', classname="col12"),
            ], classname="compact-row"),
            FieldRowPanel([
                FieldPanel('unit_secretary_name', classname="col6"),
                FieldPanel('unit_secretary_mobile', classname="col6"),
            ], classname="compact-row"),
        ], heading="Org. Membership", classname="compact-panel"),
        FieldPanel('is_active'),
    ]


class ClassAdmin(ModelAdmin):
    model = Class
    permission_helper_class = ACLPermissionHelper
    menu_label = 'Classes'
    menu_icon = 'group'
    add_to_admin_menu = False  # Will be included in grouped menu
    list_display = ('name', 'subject', 'grade_level', 'teacher', 'current_enrollment', 'max_students', 'is_active')
    list_filter = ('subject', 'grade_level', 'is_active')
    search_fields = ('name', 'description', 'teacher__name')
    panels = [
        MultiFieldPanel([
            FieldRowPanel([
                FieldPanel('name', classname="col6"),
                FieldPanel('grade_level', classname="col6"),
            ], classname="compact-row"),
            FieldRowPanel([
                FieldPanel('subject', classname="col6"),
                FieldPanel('teacher', classname="col6"),
            ], classname="compact-row"),
            FieldRowPanel([
                FieldPanel('course_fee', classname="col6"),
            ], classname="compact-row"),
            FieldRowPanel([
                FieldPanel('max_students', classname="col4"),
                FieldPanel('start_date', classname="col4"),
                FieldPanel('end_date', classname="col4"),
            ], classname="compact-row"),
             FieldRowPanel([
                FieldPanel('is_active', classname="col12"),
            ], classname="compact-row"),
        ], heading="Class Details", classname="compact-panel"),
        MultiFieldPanel([
            FieldPanel('description'),
            FieldPanel('schedule'),
        ], heading="Description & Schedule", classname="compact-panel"),
    ]


class StudentEnrollmentAdmin(ModelAdmin):
    model = StudentEnrollment
    permission_helper_class = ACLPermissionHelper
    menu_label = 'Student Enrollments'
    menu_icon = 'tick'
    add_to_admin_menu = False  # Will be included in grouped menu
    list_display = ('student', 'class_instance', 'enrollment_date', 'status', 'grade')
    list_filter = ('status', 'enrollment_date', 'class_instance__subject')
    search_fields = ('student__first_name', 'student__last_name', 'class_instance__name', 'notes')
    panels = [
        MultiFieldPanel([
            FieldRowPanel([
                FieldPanel('student', classname="col6"),
                FieldPanel('class_instance', classname="col6"),
            ], classname="compact-row"),
            FieldRowPanel([
                FieldPanel('enrollment_date', classname="col4"),
                FieldPanel('status', classname="col4"),
                FieldPanel('grade', classname="col4"),
            ], classname="compact-row"),
             FieldRowPanel([
                FieldPanel('notes', classname="col12"),
            ], classname="compact-row"),
        ], heading="Enrollment Details", classname="compact-panel"),
    ]


modeladmin_register(TeacherAdmin)
modeladmin_register(ClassAdmin)
modeladmin_register(StudentEnrollmentAdmin)


class StudentFeePaymentAdmin(ModelAdmin):
    model = StudentFeePayment
    permission_helper_class = ACLPermissionHelper
    menu_label = 'Fee Payments'
    menu_icon = 'money'
    add_to_admin_menu = False
    list_display = ('enrollment', 'amount', 'date', 'payment_method', 'reference_number')
    list_filter = ('payment_method', 'date', 'enrollment__class_instance')
    search_fields = ('enrollment__student__first_name', 'enrollment__student__last_name', 'reference_number')
    panels = [
        MultiFieldPanel([
            FieldRowPanel([
                FieldPanel('enrollment', classname="col6"),
                FieldPanel('amount', classname="col6"),
            ], classname="compact-row"),
            FieldRowPanel([
                FieldPanel('date', classname="col6"),
                FieldPanel('payment_method', classname="col6"),
            ], classname="compact-row"),
            FieldRowPanel([
                FieldPanel('reference_number', classname="col12"),
            ], classname="compact-row"),
            FieldRowPanel([
                FieldPanel('remarks', classname="col12"),
            ], classname="compact-row"),
        ], heading="Payment Details", classname="compact-panel"),
    ]


modeladmin_register(StudentFeePaymentAdmin)


class StudentAdmissionForm(forms.ModelForm):
    """Custom form for StudentAdmission with student as a text field"""
    student_name = forms.CharField(
        max_length=200,
        required=True,
        label="Student Name",
        help_text="Enter student's first and last name"
    )
    
    class Meta:
        model = StudentAdmission
        fields = [
            'student_name',
            'class_applied',
            'admission_date',
            'admission_number',
            'status',
            'documents_status',
            'documents_remarks',
            'interview_date',
            'interview_remarks',
            'parent_contact',
            'emergency_contact',
            'special_requirements',
            'approved_by',
            'approval_date',
            'remarks',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # If editing an existing object, populate student_name with the student's full name
        if self.instance.pk and self.instance.student:
            self.fields['student_name'].initial = self.instance.student.full_name
        # Make student_name required
        self.fields['student_name'].required = True

    def clean_student_name(self):
        """Validate student name - try to find matching student"""
        name = self.cleaned_data.get('student_name', '').strip()
        if not name:
            raise ValidationError("Student name is required.")
        return name

    def save(self, commit=True):
        """Save the form and handle student lookup/creation"""
        instance = super().save(commit=False)
        student_name = self.cleaned_data.get('student_name', '').strip()
        
        # Try to find the student by full name
        if student_name:
            # Split the name to get first and last name
            name_parts = student_name.split()
            first_name = name_parts[0] if name_parts else ''
            last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''
            
            # Search for existing student
            try:
                student = Member.objects.get(
                    first_name__icontains=first_name,
                    last_name__icontains=last_name
                )
                instance.student = student
            except Member.DoesNotExist:
                # If not found, try with just first name
                try:
                    student = Member.objects.get(first_name__icontains=student_name)
                    instance.student = student
                except Member.MultipleObjectsReturned:
                    raise ValidationError(f"Multiple students found with name '{student_name}'. Please be more specific.")
                except Member.DoesNotExist:
                    raise ValidationError(f"Student '{student_name}' not found in the system.")
            except Member.MultipleObjectsReturned:
                raise ValidationError(f"Multiple students found with name '{student_name}'. Please be more specific.")
        
        if commit:
            instance.save()
        return instance


class StudentAdmissionAdmin(ModelAdmin):
    model = StudentAdmission
    permission_helper_class = ACLPermissionHelper
    menu_label = 'Admissions'
    menu_icon = 'form'
    add_to_admin_menu = False
    list_display = ('student', 'class_applied', 'admission_number', 'status', 'admission_date', 'documents_status')
    list_filter = ('status', 'documents_status', 'admission_date', 'class_applied')
    search_fields = ('student__first_name', 'student__last_name', 'admission_number', 'class_applied__name')
    
    def get_form_class(self):
        return StudentAdmissionForm


modeladmin_register(StudentAdmissionAdmin)


@hooks.register('register_admin_urls')
def register_education_admin_urls():
    return [
        path('education/pending-fees/', views.PendingFeesReportView.as_view(), name='education_pending_fees'),
        path('education/record-payment/', views.record_fee_payment_view, name='education_record_fee_payment'),
        path('education/record-payment/<int:enrollment_id>/', views.record_fee_payment_view, name='education_record_fee_payment_for'),
        path('education/payment-history/<int:enrollment_id>/', views.payment_history_view, name='education_payment_history'),
        path('education/all-payments/', views.all_payments_view, name='education_all_payments'),
    ]