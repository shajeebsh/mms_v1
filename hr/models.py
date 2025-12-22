from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
from membership.models import Member


class StaffPosition(models.Model):
    """Staff positions in the mosque"""
    POSITION_CHOICES = [
        ('imam', 'Imam'),
        ('assistant_imam', 'Assistant Imam'),
        ('muazzin', 'Muazzin'),
        ('cleaner', 'Cleaner'),
        ('administrator', 'Administrator'),
        ('teacher', 'Teacher'),
        ('maintenance', 'Maintenance Staff'),
        ('security', 'Security Guard'),
        ('other', 'Other'),
    ]

    name = models.CharField(max_length=100, choices=POSITION_CHOICES, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.get_name_display()

    class Meta:
        verbose_name = "Staff Position"
        verbose_name_plural = "Staff Positions"


class StaffMember(models.Model):
    """Staff members working at the mosque"""
    EMPLOYMENT_TYPE_CHOICES = [
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
        ('contract', 'Contract'),
    ]

    member = models.OneToOneField(Member, on_delete=models.CASCADE, related_name='staff_profile')
    position = models.ForeignKey(StaffPosition, on_delete=models.CASCADE)
    employment_type = models.CharField(max_length=20, choices=EMPLOYMENT_TYPE_CHOICES, default='full_time')
    hire_date = models.DateField()
    termination_date = models.DateField(null=True, blank=True)
    base_salary = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    hourly_rate = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    working_hours_per_week = models.IntegerField(default=40)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.member.first_name} {self.member.last_name} - {self.position.get_name_display()}"

    class Meta:
        verbose_name = "Staff Member"
        verbose_name_plural = "Staff Members"


class Attendance(models.Model):
    """Staff attendance records"""
    staff_member = models.ForeignKey(StaffMember, on_delete=models.CASCADE)
    date = models.DateField()
    check_in_time = models.TimeField(null=True, blank=True)
    check_out_time = models.TimeField(null=True, blank=True)
    hours_worked = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=20, choices=[
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
        ('half_day', 'Half Day'),
        ('holiday', 'Holiday'),
    ], default='present')
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.staff_member} - {self.date}"

    class Meta:
        verbose_name = "Attendance"
        verbose_name_plural = "Attendance Records"
        unique_together = ['staff_member', 'date']


class LeaveType(models.Model):
    """Types of leave available"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    days_allowed_per_year = models.IntegerField(default=0)
    is_paid = models.BooleanField(default=True)
    requires_approval = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Leave Type"
        verbose_name_plural = "Leave Types"


class LeaveRequest(models.Model):
    """Leave requests from staff"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    ]

    staff_member = models.ForeignKey(StaffMember, on_delete=models.CASCADE)
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    days_requested = models.DecimalField(max_digits=4, decimal_places=1, default=1)
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_leaves')
    approved_date = models.DateTimeField(null=True, blank=True)
    comments = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.staff_member} - {self.leave_type.name} ({self.start_date} to {self.end_date})"

    class Meta:
        verbose_name = "Leave Request"
        verbose_name_plural = "Leave Requests"


class SalaryComponent(models.Model):
    """Components that make up salary (basic, allowances, deductions)"""
    COMPONENT_TYPE_CHOICES = [
        ('basic', 'Basic Salary'),
        ('allowance', 'Allowance'),
        ('deduction', 'Deduction'),
        ('bonus', 'Bonus'),
    ]

    name = models.CharField(max_length=100)
    component_type = models.CharField(max_length=20, choices=COMPONENT_TYPE_CHOICES)
    description = models.TextField(blank=True)
    is_taxable = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.get_component_type_display()})"

    class Meta:
        verbose_name = "Salary Component"
        verbose_name_plural = "Salary Components"


class StaffSalary(models.Model):
    """Salary details for staff members"""
    staff_member = models.ForeignKey(StaffMember, on_delete=models.CASCADE)
    salary_component = models.ForeignKey(SalaryComponent, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    effective_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.staff_member} - {self.salary_component.name}: ₹{self.amount}"

    class Meta:
        verbose_name = "Staff Salary"
        verbose_name_plural = "Staff Salaries"


class Payroll(models.Model):
    """Monthly payroll records"""
    staff_member = models.ForeignKey(StaffMember, on_delete=models.CASCADE)
    pay_period_start = models.DateField()
    pay_period_end = models.DateField()
    basic_salary = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    allowances = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    deductions = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    gross_salary = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    net_salary = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_date = models.DateField(null=True, blank=True)
    payment_status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled'),
    ], default='pending')
    processed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.staff_member} - {self.pay_period_start} to {self.pay_period_end}"

    class Meta:
        verbose_name = "Payroll"
        verbose_name_plural = "Payroll Records"
        unique_together = ['staff_member', 'pay_period_start', 'pay_period_end']
