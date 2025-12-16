import csv
import json
from datetime import datetime, timedelta
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count, Q, Sum
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, SimpleDocTemplate, Table, TableStyle

from assets.models import PropertyUnit, Shop
from education.models import Class, StudentEnrollment, Teacher
from finance.models import Donation, DonationCategory, Expense, ExpenseCategory
from membership.models import Family, Member, MembershipDues, Payment
from operations.models import (AuditoriumBooking, DigitalSignageContent,
                               PrayerTime)

from .models import DashboardWidget, ReportExport, UserProfile


def login_view(request):
    """Custom login view with user type selection"""
    if request.user.is_authenticated:
        return redirect('home:dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', 'home:dashboard')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'home/login.html')


def logout_view(request):
    """Custom logout view"""
    logout(request)
    return redirect('home:login')


@login_required
def dashboard_view(request):
    """Main dashboard view based on user type"""
    user_profile = getattr(request.user, 'profile', None)
    if not user_profile:
        # Create default profile for existing users
        user_profile = UserProfile.objects.create(
            user=request.user,
            user_type='staff'
        )

    user_type = user_profile.user_type

    # Get dashboard data based on user type
    context = {
        'user_profile': user_profile,
        'user_type': user_type,
    }

    if user_type == 'admin':
        context.update(get_admin_dashboard_data())
    elif user_type == 'executive':
        context.update(get_executive_dashboard_data())
    elif user_type == 'manager':
        context.update(get_manager_dashboard_data())
    else:  # staff or volunteer
        context.update(get_staff_dashboard_data())

    # Add quick actions / widgets depending on the user's groups or role
    context['quick_actions'] = get_quick_actions(request.user)

    return render(request, 'home/dashboard.html', context)


def get_quick_actions(user):
    """Return a list of quick action dicts depending on user groups or superuser."""
    actions = []
    if not user or user.is_anonymous:
        return actions

    if user.is_superuser:
        return [
            {'name': 'Site Admin', 'url': '/django-admin/', 'icon': 'cog'},
            {'name': 'Wagtail CMS', 'url': '/cms/', 'icon': 'pencil'},
            {'name': 'Run Migrations', 'url': '/admin/db/', 'icon': 'database'},
        ]

    group_names = set(g.name.lower() for g in user.groups.all())

    if 'membership' in group_names:
        actions += [
            {'name': 'Members', 'url': '/membership/', 'icon': 'user'},
            {'name': 'Families', 'url': '/membership/families/', 'icon': 'group'},
            {'name': 'Overdue Dues', 'url': '/membership/overdue-report/', 'icon': 'warning'},
        ]

    if 'finance' in group_names:
        actions += [
            {'name': 'Record Donation', 'url': '/finance/donation/create/', 'icon': 'money'},
            {'name': 'Record Expense', 'url': '/finance/expense/create/', 'icon': 'minus'},
            {'name': 'Financial Reports', 'url': '/finance/reports/', 'icon': 'chart-bar'},
        ]

    if 'education' in group_names:
        actions += [
            {'name': 'Add Class', 'url': '/education/class/create/', 'icon': 'book'},
            {'name': 'Enroll Student', 'url': '/education/enroll/', 'icon': 'user-plus'},
            {'name': 'Teachers', 'url': '/education/teachers/', 'icon': 'user-tie'},
        ]

    if 'assets' in group_names:
        actions += [
            {'name': 'Shops', 'url': '/assets/shops/', 'icon': 'shopping-cart'},
            {'name': 'Property Units', 'url': '/assets/units/', 'icon': 'home'},
        ]

    if 'operations' in group_names:
        actions += [
            {'name': 'Auditorium Bookings', 'url': '/operations/bookings/', 'icon': 'calendar'},
            {'name': 'Digital Signage', 'url': '/operations/signage/', 'icon': 'tv'},
            {'name': 'Prayer Times', 'url': '/operations/prayer-times/', 'icon': 'clock'},
        ]

    if 'hr' in group_names:
        actions += [
            {'name': 'Staff Directory', 'url': '/hr/staff/', 'icon': 'users'},
            {'name': 'Attendance', 'url': '/hr/attendance/', 'icon': 'clipboard'},
            {'name': 'Payroll', 'url': '/hr/payroll/', 'icon': 'money-bill'},
        ]

    if 'committee' in group_names:
        actions += [
            {'name': 'Trustees', 'url': '/committee/trustees/', 'icon': 'user-shield'},
            {'name': 'Meetings', 'url': '/committee/meetings/', 'icon': 'calendar-alt'},
            {'name': 'Attachments', 'url': '/committee/attachments/', 'icon': 'paperclip'},
        ]

    return actions


def get_admin_dashboard_data():
    """Get comprehensive dashboard data for administrators"""
    today = timezone.now().date()
    current_year = today.year

    # Basic counts
    data = {
        'total_families': Family.objects.count(),
        'total_members': Member.objects.filter(is_active=True).count(),
        'total_teachers': Teacher.objects.filter(is_active=True).count(),
        'total_classes': Class.objects.filter(is_active=True).count(),
        'total_shops': Shop.objects.count(),
        'total_properties': PropertyUnit.objects.count(),
    }

    # Financial data
    total_donations = Donation.objects.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    total_expenses = Expense.objects.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    total_dues_collected = Payment.objects.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

    data.update({
        'total_donations': total_donations,
        'total_expenses': total_expenses,
        'net_income': total_donations - total_expenses,
        'total_dues_collected': total_dues_collected,
    })

    # Monthly trends (last 12 months)
    monthly_data = []
    for i in range(11, -1, -1):
        month_date = today - timedelta(days=30*i)
        month_start = month_date.replace(day=1)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)

        donations = Donation.objects.filter(date__range=[month_start, month_end]).aggregate(total=Sum('amount'))['total'] or 0
        expenses = Expense.objects.filter(date__range=[month_start, month_end]).aggregate(total=Sum('amount'))['total'] or 0
        dues = Payment.objects.filter(payment_date__range=[month_start, month_end]).aggregate(total=Sum('amount'))['total'] or 0

        monthly_data.append({
            'month': month_date.strftime('%b %Y'),
            'donations': float(donations),
            'expenses': float(expenses),
            'dues': float(dues),
        })

    data['monthly_trends'] = monthly_data

    # Recent activities
    data['recent_donations'] = Donation.objects.select_related('member').order_by('-date')[:5]
    data['recent_payments'] = Payment.objects.select_related('family').order_by('-payment_date')[:5]
    data['upcoming_bookings'] = AuditoriumBooking.objects.filter(
        booking_date__gte=today,
        status='approved'
    ).order_by('booking_date')[:5]

    return data


def get_executive_dashboard_data():
    """Get executive dashboard data with KPIs and trends"""
    today = timezone.now().date()
    current_year = today.year

    # Key Performance Indicators
    total_members = Member.objects.filter(is_active=True).count()
    total_families = Family.objects.count()

    # Income data
    total_donations = Donation.objects.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    total_dues = Payment.objects.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    total_income = total_donations + total_dues

    # Occupancy data
    occupied_units = PropertyUnit.objects.filter(is_occupied=True).count()
    total_units = PropertyUnit.objects.count()
    occupancy_rate = (occupied_units / total_units * 100) if total_units > 0 else 0

    # Monthly targets vs actual (simplified)
    monthly_dues_target = total_families * 10  # ₹10 per family per month
    current_month_dues = Payment.objects.filter(
        payment_date__year=current_year,
        payment_date__month=today.month
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

    data = {
        'kpis': {
            'total_members': total_members,
            'total_families': total_families,
            'total_income': total_income,
            'occupancy_rate': occupancy_rate,
        },
        'monthly_dues_target': monthly_dues_target,
        'current_month_dues': float(current_month_dues),
        'remaining_dues': float(max(0, monthly_dues_target - float(current_month_dues))),
        'dues_achievement': (float(current_month_dues) / monthly_dues_target * 100) if monthly_dues_target > 0 else 0,
    }

    # Trend data for charts
    monthly_income_data = []
    for i in range(11, -1, -1):
        month_date = today - timedelta(days=30*i)
        month_start = month_date.replace(day=1)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)

        donations = Donation.objects.filter(date__range=[month_start, month_end]).aggregate(total=Sum('amount'))['total'] or 0
        dues = Payment.objects.filter(payment_date__range=[month_start, month_end]).aggregate(total=Sum('amount'))['total'] or 0

        monthly_income_data.append({
            'month': month_date.strftime('%b %Y'),
            'income': float(donations + dues),
            'target': monthly_dues_target,
        })

    data['monthly_income_trends'] = monthly_income_data

    # Auditorium revenue (from bookings)
    auditorium_bookings = AuditoriumBooking.objects.filter(
        status='completed',
        booking_date__year=current_year
    ).count()
    # Assume average revenue per booking
    avg_revenue_per_booking = Decimal('5000.00')
    total_auditorium_revenue = auditorium_bookings * avg_revenue_per_booking

    data['auditorium_revenue'] = float(total_auditorium_revenue)

    return data


def get_manager_dashboard_data():
    """Get department manager dashboard data"""
    today = timezone.now().date()

    data = {
        'department_overview': {
            'active_classes': Class.objects.filter(is_active=True).count(),
            'total_students': StudentEnrollment.objects.filter(status='active').count(),
            'active_teachers': Teacher.objects.filter(is_active=True).count(),
            'total_bookings': AuditoriumBooking.objects.filter(
                booking_date__gte=today,
                status__in=['pending', 'approved']
            ).count(),
        }
    }

    # Department-specific metrics
    data['recent_activities'] = []

    # Add recent class enrollments
    recent_enrollments = StudentEnrollment.objects.select_related(
        'student', 'class_instance'
    ).order_by('-enrollment_date')[:3]
    for enrollment in recent_enrollments:
        data['recent_activities'].append({
            'type': 'enrollment',
            'description': f"{enrollment.student.full_name} enrolled in {enrollment.class_instance.name}",
            'date': enrollment.enrollment_date,
        })

    # Add recent bookings
    recent_bookings = AuditoriumBooking.objects.filter(
        status='approved'
    ).order_by('-created_at')[:3]
    for booking in recent_bookings:
        data['recent_activities'].append({
            'type': 'booking',
            'description': f"Auditorium booked for {booking.event_name}",
            'date': booking.booking_date,
        })

    return data


def get_staff_dashboard_data():
    """Get basic staff dashboard data"""
    today = timezone.now().date()

    data = {
        'today_overview': {
            'total_members': Member.objects.filter(is_active=True).count(),
            'active_classes': Class.objects.filter(is_active=True).count(),
            'today_bookings': AuditoriumBooking.objects.filter(
                booking_date=today,
                status='approved'
            ).count(),
        },
        'quick_actions': [
            {'name': 'Add Member', 'url': '/cms/membership/member/create/', 'icon': 'user'},
            {'name': 'Record Donation', 'url': '/cms/finance/donation/create/', 'icon': 'money'},
            {'name': 'View Reports', 'url': '/membership/overdue-report/', 'icon': 'chart-bar'},
        ]
    }

    return data


@login_required
def export_report_view(request, report_type):
    """Export reports in various formats"""
    user_profile = getattr(request.user, 'profile', None)
    if not user_profile:
        return JsonResponse({'error': 'User profile not found'}, status=403)

    if report_type == 'overdue_dues':
        return export_overdue_dues_report(request)
    elif report_type == 'financial_summary':
        return export_financial_summary_report(request)
    elif report_type == 'membership_summary':
        return export_membership_summary_report(request)
    else:
        return JsonResponse({'error': 'Invalid report type'}, status=400)


def export_overdue_dues_report(request):
    """Export overdue dues report"""
    export_format = request.GET.get('format', 'csv')
    today = timezone.now().date()

    # Get overdue dues
    overdue_dues = MembershipDues.objects.filter(
        is_paid=False,
        due_date__lt=today
    ).select_related('family').order_by('due_date', 'family__name')

    if export_format == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="overdue_dues_{today}.csv"'

        writer = csv.writer(response)
        writer.writerow(['Family', 'Year', 'Month', 'Amount Due', 'Due Date', 'Days Overdue'])

        for due in overdue_dues:
            days_overdue = (today - due.due_date).days
            writer.writerow([
                due.family.name,
                due.year,
                due.month,
                due.amount_due,
                due.due_date,
                days_overdue
            ])

        return response

    elif export_format == 'pdf':
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="overdue_dues_{today}.pdf"'

        doc = SimpleDocTemplate(response, pagesize=letter)
        elements = []

        styles = getSampleStyleSheet()
        elements.append(Paragraph("Overdue Membership Dues Report", styles['Heading1']))
        elements.append(Paragraph(f"Generated on {today}", styles['Normal']))
        elements.append(Paragraph("", styles['Normal']))

        # Create table data
        data = [['Family', 'Year', 'Month', 'Amount Due', 'Due Date', 'Days Overdue']]
        for due in overdue_dues:
            days_overdue = (today - due.due_date).days
            data.append([
                due.family.name,
                str(due.year),
                str(due.month),
                f"₹{due.amount_due}",
                due.due_date.strftime('%Y-%m-%d'),
                str(days_overdue)
            ])

        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))

        elements.append(table)
        doc.build(elements)

        return response

    return JsonResponse({'error': 'Invalid format'}, status=400)


def export_financial_summary_report(request):
    """Export financial summary report"""
    export_format = request.GET.get('format', 'csv')
    today = timezone.now().date()
    current_year = today.year

    # Get financial data
    donations = Donation.objects.filter(date__year=current_year)
    expenses = Expense.objects.filter(date__year=current_year)
    payments = Payment.objects.filter(payment_date__year=current_year)

    total_donations = donations.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    total_expenses = expenses.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    total_payments = payments.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

    if export_format == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="financial_summary_{current_year}.csv"'

        writer = csv.writer(response)
        writer.writerow(['Category', 'Amount'])
        writer.writerow(['Total Donations', total_donations])
        writer.writerow(['Total Expenses', total_expenses])
        writer.writerow(['Total Membership Payments', total_payments])
        writer.writerow(['Net Income', total_donations + total_payments - total_expenses])

        return response

    return JsonResponse({'error': 'Format not implemented'}, status=400)


def export_membership_summary_report(request):
    """Export membership summary report"""
    export_format = request.GET.get('format', 'csv')
    today = timezone.now().date()

    families = Family.objects.all()
    members = Member.objects.filter(is_active=True)

    if export_format == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="membership_summary_{today}.csv"'

        writer = csv.writer(response)
        writer.writerow(['Metric', 'Count'])
        writer.writerow(['Total Families', families.count()])
        writer.writerow(['Total Active Members', members.count()])
        writer.writerow(['Male Members', members.filter(gender='M').count()])
        writer.writerow(['Female Members', members.filter(gender='F').count()])

        return response

    return JsonResponse({'error': 'Format not implemented'}, status=400)


@login_required
def live_data_feed(request):
    """API endpoint for live dashboard data"""
    user_profile = getattr(request.user, 'profile', None)
    if not user_profile:
        return JsonResponse({'error': 'User profile not found'}, status=403)

    data_type = request.GET.get('type', 'summary')

    if data_type == 'summary':
        data = {
            'total_families': Family.objects.count(),
            'total_members': Member.objects.filter(is_active=True).count(),
            'total_donations': float(Donation.objects.aggregate(total=Sum('amount'))['total'] or 0),
            'total_dues_collected': float(Payment.objects.aggregate(total=Sum('amount'))['total'] or 0),
            'active_classes': Class.objects.filter(is_active=True).count(),
            'upcoming_bookings': AuditoriumBooking.objects.filter(
                booking_date__gte=timezone.now().date(),
                status='approved'
            ).count(),
            'timestamp': timezone.now().isoformat(),
        }
    elif data_type == 'financial':
        today = timezone.now().date()
        month_start = today.replace(day=1)

        monthly_donations = Donation.objects.filter(date__gte=month_start).aggregate(total=Sum('amount'))['total'] or 0
        monthly_expenses = Expense.objects.filter(date__gte=month_start).aggregate(total=Sum('amount'))['total'] or 0
        monthly_dues = Payment.objects.filter(payment_date__gte=month_start).aggregate(total=Sum('amount'))['total'] or 0

        data = {
            'monthly_donations': float(monthly_donations),
            'monthly_expenses': float(monthly_expenses),
            'monthly_dues': float(monthly_dues),
            'monthly_net': float(monthly_dues + monthly_donations - monthly_expenses),
            'timestamp': timezone.now().isoformat(),
        }
    else:
        return JsonResponse({'error': 'Invalid data type'}, status=400)

    return JsonResponse(data)