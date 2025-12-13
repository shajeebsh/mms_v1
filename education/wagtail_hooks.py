from wagtail.admin.panels import FieldPanel
from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register

from .models import Teacher, Class, StudentEnrollment


class TeacherAdmin(ModelAdmin):
    model = Teacher
    menu_label = 'Teachers'
    menu_icon = 'user'
    add_to_admin_menu = False  # Will be included in grouped menu
    list_display = ('member', 'specialization', 'hire_date', 'is_active')
    list_filter = ('is_active', 'hire_date')
    search_fields = ('member__first_name', 'member__last_name', 'specialization')
    panels = [
        FieldPanel('member'),
        FieldPanel('specialization'),
        FieldPanel('qualifications'),
        FieldPanel('hire_date'),
        FieldPanel('is_active'),
    ]


class ClassAdmin(ModelAdmin):
    model = Class
    menu_label = 'Classes'
    menu_icon = 'group'
    add_to_admin_menu = False  # Will be included in grouped menu
    list_display = ('name', 'subject', 'grade_level', 'teacher', 'current_enrollment', 'max_students', 'is_active')
    list_filter = ('subject', 'grade_level', 'is_active')
    search_fields = ('name', 'description', 'teacher__member__first_name', 'teacher__member__last_name')
    panels = [
        FieldPanel('name'),
        FieldPanel('grade_level'),
        FieldPanel('subject'),
        FieldPanel('teacher'),
        FieldPanel('max_students'),
        FieldPanel('description'),
        FieldPanel('schedule'),
        FieldPanel('start_date'),
        FieldPanel('end_date'),
        FieldPanel('is_active'),
    ]


class StudentEnrollmentAdmin(ModelAdmin):
    model = StudentEnrollment
    menu_label = 'Student Enrollments'
    menu_icon = 'tick'
    add_to_admin_menu = False  # Will be included in grouped menu
    list_display = ('student', 'class_instance', 'enrollment_date', 'status', 'grade')
    list_filter = ('status', 'enrollment_date', 'class_instance__subject')
    search_fields = ('student__first_name', 'student__last_name', 'class_instance__name', 'notes')
    panels = [
        FieldPanel('student'),
        FieldPanel('class_instance'),
        FieldPanel('enrollment_date'),
        FieldPanel('status'),
        FieldPanel('grade'),
        FieldPanel('notes'),
    ]


modeladmin_register(TeacherAdmin)
modeladmin_register(ClassAdmin)
modeladmin_register(StudentEnrollmentAdmin)