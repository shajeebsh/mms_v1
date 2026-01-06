import csv
import json
import logging
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

logger = logging.getLogger(__name__)
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, SimpleDocTemplate, Table, TableStyle

from assets.models import PropertyUnit, Shop
from education.models import Class, StudentEnrollment, Teacher
from finance.models import Donation, DonationCategory, Expense, ExpenseCategory
from membership.models import HouseRegistration, Member, MembershipDues, Payment
from operations.models import (AuditoriumBooking, DigitalSignageContent,
                               PrayerTime)
from home.admin_menu import get_modeladmin_url

from .models import DashboardWidget, ReportExport, UserProfile





def get_dashboard_actions(user):
    """Return a list of dashboard action groups (category, icon, actions) based on user roles."""
    action_groups = []
    if not user or user.is_anonymous:
        return action_groups

    if user.is_superuser:
        return [
            {
                'category': 'System',
                'icon': 'cog',
                'actions': [
                    {'name': 'Site Admin', 'url': '/django-admin/', 'icon': 'cog'},
                    {'name': 'Wagtail CMS', 'url': '/cms/', 'icon': 'pencil'},
                    {'name': 'Run Migrations', 'url': '/admin/db/', 'icon': 'database'},
                ]
            }
        ]

    group_names = set(g.name.lower() for g in user.groups.all())

    # Membership
    if 'membership' in group_names:
        action_groups.append({
            'category': 'Membership',
            'icon': 'group',
            'actions': [
                {'name': 'Members', 'url': get_modeladmin_url('membership', 'member'), 'icon': 'user'},
                {'name': 'Families', 'url': get_modeladmin_url('membership', 'family'), 'icon': 'group'},
                {'name': 'Overdue Dues', 'url': '/membership/overdue-report/', 'icon': 'warning'},
            ]
        })

    # Finance
    if 'finance' in group_names:
        action_groups.append({
            'category': 'Finance',
            'icon': 'money-bill-wave',
            'actions': [
                {'name': 'Donations', 'url': get_modeladmin_url('finance', 'donation'), 'icon': 'money-bill'},
                {'name': 'Expenses', 'url': get_modeladmin_url('finance', 'expense'), 'icon': 'minus-circle'},
                {'name': 'Financial Reports', 'url': get_modeladmin_url('finance', 'financialreport'), 'icon': 'chart-bar'},
            ]
        })

    # Education
    if 'education' in group_names:
        action_groups.append({
            'category': 'Education',
            'icon': 'graduation-cap',
            'actions': [
                {'name': 'Classes', 'url': get_modeladmin_url('education', 'class'), 'icon': 'book'},
                {'name': 'Teachers', 'url': get_modeladmin_url('education', 'teacher'), 'icon': 'user-tie'},
                {'name': 'Enroll Student', 'url': '/education/enroll/', 'icon': 'user-plus'},
            ]
        })

    # Assets
    if 'assets' in group_names:
        action_groups.append({
            'category': 'Assets',
            'icon': 'building',
            'actions': [
                {'name': 'Shops', 'url': get_modeladmin_url('assets', 'shop'), 'icon': 'shopping-cart'},
                {'name': 'Property Units', 'url': get_modeladmin_url('assets', 'propertyunit'), 'icon': 'home'},
            ]
        })

    # Operations
    if 'operations' in group_names:
        action_groups.append({
            'category': 'Operations',
            'icon': 'calendar-alt',
            'actions': [
                {'name': 'Auditorium Bookings', 'url': get_modeladmin_url('operations', 'auditoriumbooking'), 'icon': 'calendar-check'},
                {'name': 'Digital Signage', 'url': '/operations/signage/', 'icon': 'tv'},
                {'name': 'Prayer Times', 'url': get_modeladmin_url('operations', 'prayertime'), 'icon': 'clock'},
            ]
        })

    # HR
    if 'hr' in group_names:
        action_groups.append({
            'category': 'HR & Payroll',
            'icon': 'users-cog',
            'actions': [
                {'name': 'Staff Directory', 'url': get_modeladmin_url('hr', 'staffmember'), 'icon': 'users'},
                {'name': 'Attendance', 'url': '/hr/attendance/', 'icon': 'clipboard-check'},
                {'name': 'Payroll', 'url': get_modeladmin_url('hr', 'payroll'), 'icon': 'money-check-alt'},
            ]
        })

    # Committee
    if 'committee' in group_names:
        action_groups.append({
            'category': 'Committee & Minutes',
            'icon': 'university',
            'actions': [
                {'name': 'Trustees', 'url': get_modeladmin_url('committee', 'trustee'), 'icon': 'user-shield'},
                {'name': 'Meetings', 'url': get_modeladmin_url('committee', 'meeting'), 'icon': 'calendar-alt'},
                {'name': 'Attachments', 'url': '/committee/attachments/', 'icon': 'paperclip'},
            ]
        })

    return action_groups





def get_admin_dashboard_data():
    """Get comprehensive dashboard data for administrators"""
    today = timezone.now().date()
    current_year = today.year

    # Basic counts
    data = {
        'total_houses': HouseRegistration.objects.count(),
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
        member_count = Member.objects.filter(created_at__lte=month_end, is_active=True).count()

        monthly_data.append({
            'month': month_date.strftime('%b %Y'),
            'donations': float(donations),
            'expenses': float(expenses),
            'dues': float(dues),
            'members': member_count,
        })

    # Recent activities
    data['recent_donations'] = Donation.objects.select_related('member', 'category').order_by('-date')[:5]
    data['recent_payments'] = Payment.objects.select_related('house').prefetch_related('membership_dues').order_by('-payment_date')[:5]
    data['upcoming_bookings'] = AuditoriumBooking.objects.filter(
        booking_date__gte=today,
        status='approved'
    ).order_by('booking_date')[:5]

    # Chart Data: Expenses by Category
    expenses_by_category_raw = Expense.objects.select_related('category').values('category__name').annotate(
        total=Sum('amount')
    ).order_by('-total')
    expenses_by_category = [
        {'category__name': e['category__name'], 'total': float(e['total'] or 0)} 
        for e in expenses_by_category_raw
    ]
    data['expenses_by_category'] = json.dumps(expenses_by_category)

    # Chart Data: Revenue Sources
    donations_by_type = Donation.objects.values('donation_type').annotate(
        total=Sum('amount')
    ).order_by('-total')
    # Map display names
    donation_type_display = dict(Donation.DONATION_TYPES)
    payment_method_display = dict(Payment.PAYMENT_METHOD_CHOICES)

    revenue_sources = [
        {'label': donation_type_display.get(d['donation_type'], d['donation_type']), 'total': float(d['total'])}
        for d in donations_by_type
    ]
    
    payments_by_method = Payment.objects.values('payment_method').annotate(
        total=Sum('amount')
    ).order_by('-total')
    
    revenue_sources.extend([
        {'label': f"Payment: {payment_method_display.get(p['payment_method'], p['payment_method'])}", 'total': float(p['total'])}
        for p in payments_by_method
    ])

    data['monthly_trends'] = json.dumps(monthly_data)
    data['revenue_sources'] = json.dumps(revenue_sources)

    return data


def get_executive_dashboard_data():
    """Get executive dashboard data with KPIs and trends"""
    today = timezone.now().date()
    current_year = today.year

    # Key Performance Indicators
    total_members = Member.objects.filter(is_active=True).count()
    total_houses = HouseRegistration.objects.count()

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

    data['monthly_income_trends'] = json.dumps(monthly_income_data)

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
        'student', 'student__family', 'class_instance', 'class_instance__teacher'
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
    ).select_related('house').order_by('due_date', 'house__house_name', 'house__house_number')

    if export_format == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="overdue_dues_{today}.csv"'

        writer = csv.writer(response)
        writer.writerow(['House', 'Year', 'Month', 'Amount Due', 'Due Date', 'Days Overdue'])

        for due in overdue_dues:
            days_overdue = (today - due.due_date).days
            writer.writerow([
                str(due.house),
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
        data = [['House', 'Year', 'Month', 'Amount Due', 'Due Date', 'Days Overdue']]
        for due in overdue_dues:
            days_overdue = (today - due.due_date).days
            data.append([
                str(due.house),
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


def redirect_finance_donation_create(request):
    """Redirect legacy frontend finance donation create URL to ModelAdmin index."""
    try:
        return redirect(get_modeladmin_url('finance', 'donation'))
    except (AttributeError, KeyError) as e:
        logger.warning(f"Could not get finance URL for DonationAdmin: {e}")
        return redirect('/cms/')
    except Exception as e:
        logger.error(f"Unexpected error redirecting to finance donation create: {e}", exc_info=True)
        return redirect('/cms/')


def redirect_finance_expense_create(request):
    """Redirect legacy frontend finance expense create URL to ModelAdmin index."""
    try:
        return redirect(get_modeladmin_url('finance', 'expense'))
    except (AttributeError, KeyError) as e:
        logger.warning(f"Could not get finance URL for ExpenseAdmin: {e}")
        return redirect('/cms/')
    except Exception as e:
        logger.error(f"Unexpected error redirecting to finance expense create: {e}", exc_info=True)
        return redirect('/cms/')


def redirect_finance_reports(request):
    """Redirect legacy frontend finance reports URL to ModelAdmin index."""
    try:
        return redirect(get_modeladmin_url('finance', 'financialreport'))
    except (AttributeError, KeyError) as e:
        logger.warning(f"Could not get finance URL for FinancialReportAdmin: {e}")
        return redirect('/cms/')
    except Exception as e:
        logger.error(f"Unexpected error redirecting to finance reports: {e}", exc_info=True)
        return redirect('/cms/')


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

    houses = HouseRegistration.objects.all()
    members = Member.objects.filter(is_active=True)

    if export_format == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="membership_summary_{today}.csv"'

        writer = csv.writer(response)
        writer.writerow(['Metric', 'Count'])
        writer.writerow(['Total Houses', houses.count()])
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
            'total_houses': HouseRegistration.objects.count(),
            'total_members': Member.objects.filter(is_active=True).count(),
            'total_donations': float(Donation.objects.aggregate(total=Sum('amount'))['total'] or 0),
            'total_dues_collected': float(Payment.objects.aggregate(total=Sum('amount'))['total'] or 0),
            'active_classes': Class.objects.filter(is_active=True).count(),
            'upcoming_bookings': AuditoriumBooking.objects.filter(
                booking_date__gte=timezone.now().date(),
                status='approved'
            ).count(),  # Count query doesn't need select_related
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


@login_required
def wagtail_dashboard_view(request):
    """Wagtail admin home page with dashboard data"""
    user_profile = getattr(request.user, 'profile', None)
    if not user_profile:
        # Create default profile for existing users
        # Default superusers to admin, others to staff
        u_type = 'admin' if request.user.is_superuser else 'staff'
        user_profile = UserProfile.objects.create(
            user=request.user,
            user_type=u_type
        )

    user_type = user_profile.user_type

    # Get dashboard data based on user type
    context = {
        'user_profile': user_profile,
        'user_type': user_type,
        'now': timezone.now(),
    }

    if user_type == 'admin':
        context.update(get_admin_dashboard_data())
    elif user_type == 'executive':
        context.update(get_executive_dashboard_data())
    else:  # staff
        context.update(get_staff_dashboard_data())

    # Add quick actions
    context['sidebar_actions'] = get_dashboard_actions(request.user)
    context['quick_actions'] = context['sidebar_actions']
    
    return render(request, 'home/wagtail_dashboard.html', context)