from django.core.management.base import BaseCommand
from django.utils import timezone
from decimal import Decimal
from datetime import date, time, timedelta
import random

from membership.models import Family, Member, MembershipDues, Payment, VitalRecord
from assets.models import Shop, PropertyUnit
from education.models import Teacher, Class, StudentEnrollment
from finance.models import DonationCategory, ExpenseCategory, Donation, Expense, FinancialReport
from operations.models import AuditoriumBooking, PrayerTime, DigitalSignageContent


class Command(BaseCommand):
    help = 'Populate database with sample data for all MMS modules'

    def handle(self, *args, **options):
        self.stdout.write('Starting sample data population...')

        # Create sample data for each module
        self.create_membership_data()
        self.create_assets_data()
        self.create_education_data()
        self.create_finance_data()
        self.create_operations_data()

        self.stdout.write(self.style.SUCCESS('Sample data population completed!'))


    def create_membership_data(self):
        self.stdout.write('Creating membership sample data...')

        # Create sample families
        families_data = [
            {'name': 'Ahmed Family', 'phone': '+1-555-0101', 'email': 'ahmed@example.com', 'address': '123 Main St'},
            {'name': 'Khan Family', 'phone': '+1-555-0102', 'email': 'khan@example.com', 'address': '456 Oak Ave'},
            {'name': 'Patel Family', 'phone': '+1-555-0103', 'email': 'patel@example.com', 'address': '789 Pine Rd'},
            {'name': 'Ali Family', 'phone': '+1-555-0104', 'email': 'ali@example.com', 'address': '321 Elm St'},
            {'name': 'Hassan Family', 'phone': '+1-555-0105', 'email': 'hassan@example.com', 'address': '654 Maple Dr'},
        ]

        families = []
        for family_data in families_data:
            family = Family.objects.create(**family_data)
            families.append(family)

        # Create sample members
        members_data = [
            {'first_name': 'Ahmed', 'last_name': 'Mohammed', 'family': families[0], 'phone': '+1-555-0101', 'email': 'ahmed.m@example.com', 'gender': 'M', 'date_of_birth': date(1985, 5, 15)},
            {'first_name': 'Fatima', 'last_name': 'Ahmed', 'family': families[0], 'phone': '+1-555-0101', 'email': 'fatima.a@example.com', 'gender': 'F', 'date_of_birth': date(1988, 8, 20)},
            {'first_name': 'Omar', 'last_name': 'Khan', 'family': families[1], 'phone': '+1-555-0102', 'email': 'omar.k@example.com', 'gender': 'M', 'date_of_birth': date(1990, 3, 10)},
            {'first_name': 'Aisha', 'last_name': 'Khan', 'family': families[1], 'phone': '+1-555-0102', 'email': 'aisha.k@example.com', 'gender': 'F', 'date_of_birth': date(1992, 7, 25)},
            {'first_name': 'Raj', 'last_name': 'Patel', 'family': families[2], 'phone': '+1-555-0103', 'email': 'raj.p@example.com', 'gender': 'M', 'date_of_birth': date(1980, 12, 5)},
            {'first_name': 'Priya', 'last_name': 'Patel', 'family': families[2], 'phone': '+1-555-0103', 'email': 'priya.p@example.com', 'gender': 'F', 'date_of_birth': date(1983, 4, 18)},
            {'first_name': 'Hassan', 'last_name': 'Ali', 'family': families[3], 'phone': '+1-555-0104', 'email': 'hassan.a@example.com', 'gender': 'M', 'date_of_birth': date(1975, 9, 30)},
            {'first_name': 'Zara', 'last_name': 'Ali', 'family': families[3], 'phone': '+1-555-0104', 'email': 'zara.a@example.com', 'gender': 'F', 'date_of_birth': date(1978, 11, 12)},
        ]

        members = []
        for member_data in members_data:
            member = Member.objects.create(**member_data)
            members.append(member)

        # Create sample vital records
        vital_records_data = [
            {'record_type': 'birth', 'member': members[0], 'date': date(1985, 5, 15), 'location': 'City Hospital'},
            {'record_type': 'marriage', 'member': members[0], 'date': date(2010, 6, 20), 'location': 'Grand Mosque'},
            {'record_type': 'birth', 'member': members[2], 'date': date(1990, 3, 10), 'location': 'City Hospital'},
        ]

        for record_data in vital_records_data:
            VitalRecord.objects.create(**record_data)

        # Create membership dues for current year
        current_year = timezone.now().year
        for family in families:
            for month in range(1, 13):
                MembershipDues.objects.create(
                    family=family,
                    year=current_year,
                    month=month,
                    amount_due=Decimal('10.00'),
                    due_date=date(current_year, month, 1),
                    is_paid=random.choice([True, False, False])  # 33% paid
                )

        # Create sample payments
        payment_data = [
            {'family': families[0], 'amount': Decimal('20.00'), 'payment_method': 'cash', 'payment_date': date.today()},
            {'family': families[1], 'amount': Decimal('30.00'), 'payment_method': 'upi', 'payment_date': date.today()},
            {'family': families[2], 'amount': Decimal('10.00'), 'payment_method': 'bank', 'payment_date': date.today()},
        ]

        for payment_info in payment_data:
            payment = Payment.objects.create(**payment_info)
            # Associate with some dues
            dues = MembershipDues.objects.filter(
                family=payment.family,
                is_paid=False
            )[:payment.amount // 10]  # Pay for some months
            payment.membership_dues.set(dues)
            for due in dues:
                due.is_paid = True
                due.save()


    def create_assets_data(self):
        self.stdout.write('Creating assets sample data...')

        # Create sample shops
        shops_data = [
            {'name': 'Halal Grocery Store', 'shop_type': 'food', 'owner_name': 'Ahmed Hassan', 'contact_info': 'Phone: +1-555-0201', 'location': 'Ground Floor', 'monthly_rent': Decimal('1500.00'), 'lease_start': date(2024, 1, 1), 'lease_end': date(2026, 12, 31)},
            {'name': 'Islamic Bookstore', 'shop_type': 'retail', 'owner_name': 'Fatima Khan', 'contact_info': 'Phone: +1-555-0202', 'location': 'First Floor', 'monthly_rent': Decimal('1200.00'), 'lease_start': date(2024, 3, 1), 'lease_end': date(2027, 2, 28)},
            {'name': 'Tailoring Services', 'shop_type': 'service', 'owner_name': 'Omar Ali', 'contact_info': 'Phone: +1-555-0203', 'location': 'Second Floor', 'monthly_rent': Decimal('800.00'), 'lease_start': date(2024, 6, 1), 'lease_end': date(2025, 5, 31)},
        ]

        for shop_data in shops_data:
            Shop.objects.create(**shop_data)

        # Create sample property units
        property_units_data = [
            {'name': 'Apartment 101', 'unit_type': 'apartment', 'address': '101 Mosque Complex', 'size_sqm': Decimal('75.00'), 'monthly_rent': Decimal('800.00'), 'tenant_name': 'Ahmed Family', 'tenant_contact': 'Phone: +1-555-0301', 'lease_start': date(2024, 1, 1), 'lease_end': date(2025, 12, 31), 'is_occupied': True},
            {'name': 'Office Suite A', 'unit_type': 'office', 'address': '200 Mosque Complex', 'size_sqm': Decimal('50.00'), 'monthly_rent': Decimal('600.00'), 'tenant_name': 'Islamic Center Admin', 'tenant_contact': 'Phone: +1-555-0302', 'lease_start': date(2024, 2, 1), 'lease_end': date(2026, 1, 31), 'is_occupied': True},
            {'name': 'Community Hall', 'unit_type': 'hall', 'address': 'Main Building', 'size_sqm': Decimal('200.00'), 'monthly_rent': Decimal('2000.00'), 'is_occupied': False},
        ]

        for unit_data in property_units_data:
            PropertyUnit.objects.create(**unit_data)


    def create_education_data(self):
        self.stdout.write('Creating education sample data...')

        # Get some members to make teachers
        members = list(Member.objects.all()[:3])

        # Create teachers
        teachers_data = [
            {'member': members[0], 'specialization': 'Quran Studies', 'qualifications': 'Hafiz, Islamic Studies Degree', 'hire_date': date(2020, 1, 15)},
            {'member': members[1], 'specialization': 'Arabic Language', 'qualifications': 'Arabic Literature Degree', 'hire_date': date(2021, 3, 20)},
            {'member': members[2], 'specialization': 'Islamic Studies', 'qualifications': 'Islamic Theology Masters', 'hire_date': date(2019, 9, 10)},
        ]

        teachers = []
        for teacher_data in teachers_data:
            teacher = Teacher.objects.create(**teacher_data)
            teachers.append(teacher)

        # Create classes
        classes_data = [
            {'name': 'Quran Hifz Class', 'grade_level': 'elementary', 'subject': 'quran', 'teacher': teachers[0], 'max_students': 15, 'description': 'Memorization of Holy Quran', 'schedule': 'Mon-Wed-Fri 4:00-5:30 PM', 'start_date': date(2024, 9, 1)},
            {'name': 'Arabic Reading', 'grade_level': 'middle', 'subject': 'arabic', 'teacher': teachers[1], 'max_students': 20, 'description': 'Basic Arabic reading and writing', 'schedule': 'Tue-Thu 6:00-7:30 PM', 'start_date': date(2024, 9, 1)},
            {'name': 'Islamic History', 'grade_level': 'high', 'subject': 'islamic_studies', 'teacher': teachers[2], 'max_students': 25, 'description': 'History of Islam and Muslim civilization', 'schedule': 'Sat 10:00 AM-12:00 PM', 'start_date': date(2024, 9, 1)},
        ]

        classes = []
        for class_data in classes_data:
            class_obj = Class.objects.create(**class_data)
            classes.append(class_obj)

        # Create student enrollments
        all_members = list(Member.objects.all())
        for class_obj in classes:
            # Enroll random students
            enrolled_students = random.sample(all_members, min(len(all_members), class_obj.max_students // 2))
            for student in enrolled_students:
                StudentEnrollment.objects.create(
                    student=student,
                    class_instance=class_obj,
                    enrollment_date=date(2024, 9, 1),
                    status='active'
                )


    def create_finance_data(self):
        self.stdout.write('Creating finance sample data...')

        # Create donation categories
        donation_categories_data = [
            {'name': 'Zakat', 'description': 'Islamic obligatory almsgiving'},
            {'name': 'Sadaqah', 'description': 'Voluntary charity'},
            {'name': 'Fitrah', 'description': 'Eid al-Fitr charity'},
            {'name': 'General Donation', 'description': 'General charitable contributions'},
        ]

        donation_categories = []
        for cat_data in donation_categories_data:
            cat = DonationCategory.objects.create(**cat_data)
            donation_categories.append(cat)

        # Create expense categories
        expense_categories_data = [
            {'name': 'Utilities', 'description': 'Electricity, water, gas bills'},
            {'name': 'Maintenance', 'description': 'Building and facility maintenance'},
            {'name': 'Salaries', 'description': 'Staff and teacher salaries'},
            {'name': 'Supplies', 'description': 'Office and educational supplies'},
        ]

        expense_categories = []
        for cat_data in expense_categories_data:
            cat = ExpenseCategory.objects.create(**cat_data)
            expense_categories.append(cat)

        # Get members for donations
        members = list(Member.objects.all())

        # Create donations
        donations_data = [
            {'member': random.choice(members), 'category': donation_categories[0], 'amount': Decimal('500.00'), 'donation_type': 'cash', 'date': date(2024, 12, 1), 'notes': 'Monthly Zakat'},
            {'member': random.choice(members), 'category': donation_categories[1], 'amount': Decimal('200.00'), 'donation_type': 'online', 'date': date(2024, 12, 5), 'notes': 'Sadaqah donation'},
            {'member': random.choice(members), 'category': donation_categories[2], 'amount': Decimal('100.00'), 'donation_type': 'cash', 'date': date(2024, 12, 10), 'notes': 'Eid Fitrah'},
            {'member': random.choice(members), 'category': donation_categories[3], 'amount': Decimal('1000.00'), 'donation_type': 'check', 'date': date(2024, 12, 15), 'notes': 'Annual donation'},
        ]

        for donation_data in donations_data:
            Donation.objects.create(**donation_data)

        # Create expenses
        expenses_data = [
            {'category': expense_categories[0], 'amount': Decimal('800.00'), 'date': date(2024, 12, 1), 'description': 'Monthly electricity bill', 'vendor': 'City Power Company'},
            {'category': expense_categories[1], 'amount': Decimal('500.00'), 'date': date(2024, 12, 5), 'description': 'Roof repair maintenance', 'vendor': 'ABC Contractors'},
            {'category': expense_categories[2], 'amount': Decimal('3000.00'), 'date': date(2024, 12, 10), 'description': 'Monthly staff salaries', 'approved_by': 'Board Chairman'},
            {'category': expense_categories[3], 'amount': Decimal('200.00'), 'date': date(2024, 12, 15), 'description': 'Office supplies and stationery', 'vendor': 'Office Depot'},
        ]

        for expense_data in expenses_data:
            Expense.objects.create(**expense_data)

        # Create a sample financial report
        FinancialReport.objects.create(
            period='monthly',
            start_date=date(2024, 12, 1),
            end_date=date(2024, 12, 31),
            total_donations=Decimal('1800.00'),
            total_expenses=Decimal('4500.00'),
            net_amount=Decimal('-2700.00'),
            generated_by='System Admin'
        )


    def create_operations_data(self):
        self.stdout.write('Creating operations sample data...')

        # Create auditorium bookings
        bookings_data = [
            {'event_name': 'Community Iftar', 'organizer': 'Mosque Committee', 'contact_person': 'Ahmed Hassan', 'contact_email': 'ahmed@mosque.org', 'contact_phone': '+1-555-0401', 'booking_date': date.today() + timedelta(days=7), 'start_time': time(19, 0), 'end_time': time(21, 0), 'expected_attendees': 150, 'purpose': 'Ramadan Iftar gathering', 'status': 'approved'},
            {'event_name': 'Islamic Lecture Series', 'organizer': 'Education Committee', 'contact_person': 'Dr. Fatima Khan', 'contact_email': 'fatima@mosque.org', 'contact_phone': '+1-555-0402', 'booking_date': date.today() + timedelta(days=14), 'start_time': time(18, 30), 'end_time': time(20, 30), 'expected_attendees': 80, 'purpose': 'Monthly Islamic knowledge session', 'status': 'approved'},
            {'event_name': 'Wedding Reception', 'organizer': 'Ali Family', 'contact_person': 'Hassan Ali', 'contact_email': 'hassan.ali@email.com', 'contact_phone': '+1-555-0403', 'booking_date': date.today() + timedelta(days=21), 'start_time': time(16, 0), 'end_time': time(22, 0), 'expected_attendees': 200, 'purpose': 'Family wedding celebration', 'status': 'pending'},
        ]

        for booking_data in bookings_data:
            AuditoriumBooking.objects.create(**booking_data)

        # Create prayer times for next 7 days
        prayer_times_data = []
        base_date = date.today()

        for i in range(7):
            current_date = base_date + timedelta(days=i)
            prayers = [
                ('fajr', time(5, 30)),
                ('dhuhr', time(12, 30)),
                ('asr', time(15, 45)),
                ('maghrib', time(18, 15)),
                ('isha', time(19, 45)),
            ]

            # Add Jumah on Friday
            if current_date.weekday() == 4:  # Friday
                prayers.append(('jumah', time(13, 30)))

            for prayer_name, prayer_time in prayers:
                prayer_times_data.append({
                    'date': current_date,
                    'prayer': prayer_name,
                    'time': prayer_time,
                    'is_jumah': prayer_name == 'jumah',
                    'location': 'Main Mosque'
                })

        for prayer_data in prayer_times_data:
            PrayerTime.objects.create(**prayer_data)

        # Create digital signage content
        signage_data = [
            {'title': 'Ramadan Mubarak', 'content_type': 'announcement', 'content': 'Ramadan Kareem! Join us for Taraweeh prayers every night at 8:00 PM.', 'display_start': timezone.now(), 'display_end': timezone.now() + timedelta(days=30), 'priority': 10},
            {'title': 'Friday Prayer Times', 'content_type': 'prayer_times', 'content': 'Jumah prayers start at 1:30 PM. Please arrive early.', 'display_start': timezone.now(), 'display_end': timezone.now() + timedelta(days=7), 'priority': 8},
            {'title': 'Community Meeting', 'content_type': 'event', 'content': 'Monthly community meeting this Saturday at 4:00 PM in the main hall.', 'display_start': timezone.now(), 'display_end': timezone.now() + timedelta(days=3), 'priority': 7},
            {'title': 'Quran Verse of the Day', 'content_type': 'quran_verse', 'content': '"And whoever puts all his trust in Allah, He will be enough for him." (Quran 65:3)', 'display_start': timezone.now(), 'display_end': timezone.now() + timedelta(days=1), 'priority': 5},
        ]

        for content_data in signage_data:
            DigitalSignageContent.objects.create(**content_data)