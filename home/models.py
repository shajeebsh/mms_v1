from django.contrib.auth.models import User
from django.db import models
from django.db.models import Sum
from django.utils import timezone
from wagtail.admin.panels import FieldPanel
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting
from wagtail.models import Page


class HomePage(Page):
    intro = models.CharField(max_length=250, blank=True)
    template = "home/home_page.html"

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
    ]


class DashboardPage(Page):
    template = "home/dashboard_page.html"

    content_panels = Page.content_panels

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)

        # Add dashboard data
        from education.models import Class, StudentEnrollment
        from finance.models import Donation, Expense
        from membership.models import Family, Member

        context["total_families"] = Family.objects.count()
        context["total_members"] = Member.objects.filter(is_active=True).count()
        context["total_donations"] = (
            Donation.objects.aggregate(total=models.Sum("amount"))["total"] or 0
        )
        context["total_expenses"] = (
            Expense.objects.aggregate(total=models.Sum("amount"))["total"] or 0
        )
        context["net_financial"] = (
            context["total_donations"] - context["total_expenses"]
        )
        context["active_classes"] = Class.objects.filter(is_active=True).count()
        context["total_enrollments"] = StudentEnrollment.objects.filter(
            status="active"
        ).count()

        # Recent donations
        context["recent_donations"] = Donation.objects.select_related(
            "member", "category"
        ).order_by("-date")[:5]

        # Upcoming events (upcoming bookings)
        from operations.models import AuditoriumBooking

        context["upcoming_bookings"] = AuditoriumBooking.objects.filter(
            booking_date__gte=timezone.now().date(), status="approved"
        ).order_by("booking_date")[:5]

        return context


class UserProfile(models.Model):
    USER_TYPES = [
        ("admin", "Administrator"),
        ("executive", "Executive Board Member"),
        ("manager", "Department Manager"),
        ("staff", "Staff Member"),
        ("volunteer", "Volunteer"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    user_type = models.CharField(max_length=20, choices=USER_TYPES, default="staff")
    department = models.CharField(
        max_length=100, blank=True, help_text="Department or committee"
    )
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.get_user_type_display()})"

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"


class DashboardWidget(models.Model):
    WIDGET_TYPES = [
        ("kpi", "KPI Tile"),
        ("chart", "Chart"),
        ("table", "Data Table"),
        ("metric", "Metric Card"),
    ]

    title = models.CharField(max_length=200)
    widget_type = models.CharField(max_length=20, choices=WIDGET_TYPES)
    user_types = models.JSONField(
        default=list, help_text="List of user types that can see this widget"
    )
    data_source = models.CharField(
        max_length=100, help_text="Function or model to get data from"
    )
    config = models.JSONField(
        default=dict, help_text="Widget configuration (colors, size, etc.)"
    )
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.title} ({self.widget_type})"

    class Meta:
        ordering = ["order", "title"]


class ReportExport(models.Model):
    EXPORT_TYPES = [
        ("csv", "CSV"),
        ("pdf", "PDF"),
        ("excel", "Excel"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    report_name = models.CharField(max_length=200)
    export_type = models.CharField(max_length=10, choices=EXPORT_TYPES)
    file_path = models.FileField(upload_to="exports/")
    created_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField()

    def __str__(self):
        return f"{self.report_name} ({self.export_type}) - {self.user.username}"

    class Meta:
        ordering = ["-created_at"]


@register_setting
class SystemSettings(BaseSiteSetting):
    monthly_membership_dues = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=10.00,
        help_text="Default monthly membership dues amount",
    )

    panels = [
        FieldPanel("monthly_membership_dues"),
    ]

