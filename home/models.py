from django.db import models
from django.db.models import Sum
from django.utils import timezone
from wagtail.admin.panels import FieldPanel
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
        from membership.models import Family, Member
        from finance.models import Donation, Expense
        from education.models import Class, StudentEnrollment

        context['total_families'] = Family.objects.count()
        context['total_members'] = Member.objects.filter(is_active=True).count()
        context['total_donations'] = Donation.objects.aggregate(total=models.Sum('amount'))['total'] or 0
        context['total_expenses'] = Expense.objects.aggregate(total=models.Sum('amount'))['total'] or 0
        context['net_financial'] = context['total_donations'] - context['total_expenses']
        context['active_classes'] = Class.objects.filter(is_active=True).count()
        context['total_enrollments'] = StudentEnrollment.objects.filter(status='active').count()

        # Recent donations
        context['recent_donations'] = Donation.objects.select_related('member').order_by('-date')[:5]

        # Upcoming events (upcoming bookings)
        from operations.models import AuditoriumBooking
        context['upcoming_bookings'] = AuditoriumBooking.objects.filter(
            booking_date__gte=timezone.now().date(),
            status='approved'
        ).order_by('booking_date')[:5]

        return context
