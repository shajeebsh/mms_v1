import random
from accounting.models import Account, AccountCategory, Transaction, JournalEntry
from billing.models import Invoice, InvoiceLineItem, BillingPayment
from wagtail.signal_handlers import disable_reference_index_auto_update
from datetime import date, time, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from assets.models import PropertyUnit, Shop
from education.models import Class, StudentEnrollment, Teacher
from finance.models import (Donation, DonationCategory, Expense,
                            ExpenseCategory, FinancialReport)
from membership.models import (
    City,
    Country,
    HouseRegistration,
    Member,
    MembershipDues,
    Payment,
    PostalCode,
    State,
    Taluk,
    VitalRecord,
    Ward,
)
from operations.models import AuditoriumBooking
from hr.models import (StaffPosition, StaffMember, Attendance, LeaveType,
                       LeaveRequest, SalaryComponent, StaffSalary, Payroll)
from committee.models import (CommitteeType, Committee, CommitteeMember,
                              Meeting, MeetingAttendee, Trustee, TrusteeMeeting,
                              TrusteeMeetingAttendee)


class Command(BaseCommand):
    help = 'Populate database with sample data for all MMS modules'

    def handle(self, *args, **options):
        with disable_reference_index_auto_update():
            self.stdout.write('Starting sample data population...')

            # Create sample data for each module
            self.create_membership_data()
            self.create_assets_data()
            self.create_education_data()
            self.create_finance_data()
            self.create_operations_data()
            self.create_hr_data()
            self.create_committee_data()
            self.create_accounting_data()
            self.create_billing_data()

            self.stdout.write(self.style.SUCCESS('Sample data population completed!'))


    def create_membership_data(self):
        self.stdout.write('Creating membership sample data...')

        houses = self.create_house_registration_data()

        # Create sample members
        members_data = [
            {'first_name': 'Ahmed', 'last_name': 'Mohammed', 'phone': '+1-555-0101', 'email': 'ahmed.m@example.com', 'gender': 'M', 'date_of_birth': date(1985, 5, 15)},
            {'first_name': 'Fatima', 'last_name': 'Ahmed', 'phone': '+1-555-0101', 'email': 'fatima.a@example.com', 'gender': 'F', 'date_of_birth': date(1988, 8, 20)},
            {'first_name': 'Omar', 'last_name': 'Khan', 'phone': '+1-555-0102', 'email': 'omar.k@example.com', 'gender': 'M', 'date_of_birth': date(1990, 3, 10)},
            {'first_name': 'Aisha', 'last_name': 'Khan', 'phone': '+1-555-0102', 'email': 'aisha.k@example.com', 'gender': 'F', 'date_of_birth': date(1992, 7, 25)},
            {'first_name': 'Raj', 'last_name': 'Patel', 'phone': '+1-555-0103', 'email': 'raj.p@example.com', 'gender': 'M', 'date_of_birth': date(1980, 12, 5)},
            {'first_name': 'Priya', 'last_name': 'Patel', 'phone': '+1-555-0103', 'email': 'priya.p@example.com', 'gender': 'F', 'date_of_birth': date(1983, 4, 18)},
            {'first_name': 'Hassan', 'last_name': 'Ali', 'phone': '+1-555-0104', 'email': 'hassan.a@example.com', 'gender': 'M', 'date_of_birth': date(1975, 9, 30)},
            {'first_name': 'Zara', 'last_name': 'Ali', 'phone': '+1-555-0104', 'email': 'zara.a@example.com', 'gender': 'F', 'date_of_birth': date(1978, 11, 12)},
        ]

        members = []
        for idx, member_data in enumerate(members_data):
            member = Member.objects.create(**member_data)
            if houses:
                member.house = houses[idx % len(houses)]
                member.save(update_fields=["house"])
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
        for house in houses:
            for month in range(1, 13):

                MembershipDues.objects.get_or_create(
                    house=house,
                    year=current_year,
                    month=month,
                    defaults={
                        'amount_due': Decimal('10.00'),
                        'due_date': date(current_year, month, 1),
                        'is_paid': random.choice([True, False, False])  # 33% paid
                    }
                )

        # Create sample payments
        payment_data = [
            {'member': members[0], 'amount': Decimal('20.00'), 'payment_method': 'cash', 'payment_date': date.today()},
            {'member': members[1], 'amount': Decimal('30.00'), 'payment_method': 'upi', 'payment_date': date.today()},
            {'member': members[2], 'amount': Decimal('10.00'), 'payment_method': 'bank', 'payment_date': date.today()},
        ]

        for payment_info in payment_data:
            payment = Payment.objects.create(**payment_info)
            # Associate with some dues linked to member's house
            if payment.member and payment.member.house:
                dues = MembershipDues.objects.filter(
                    house=payment.member.house,
                    is_paid=False
                )[:int(payment.amount // 10)]  # Pay for some months
                payment.membership_dues.set(dues)
                for due in dues:
                    due.is_paid = True
                    due.save()


    def create_membership_geography_data(self):
        self.stdout.write('Creating membership geography sample data...')

        wards = []
        for name in ["Ward 1", "Ward 2", "Ward 3", "Ward 4"]:
            obj, _ = Ward.objects.get_or_create(name=name)
            wards.append(obj)

        taluks = []
        for name in ["Alathur", "Chittur", "Pattambi", "Ottapalam"]:
            obj, _ = Taluk.objects.get_or_create(name=name)
            taluks.append(obj)

        cities = []
        for name in ["Palakkad", "Ottapalam", "Shoranur", "Chittur"]:
            obj, _ = City.objects.get_or_create(name=name)
            cities.append(obj)

        states = []
        for name in ["Kerala", "Tamil Nadu"]:
            obj, _ = State.objects.get_or_create(name=name)
            states.append(obj)

        countries = []
        for name in ["India"]:
            obj, _ = Country.objects.get_or_create(name=name)
            countries.append(obj)

        postal_codes = []
        for code in ["678001", "679101", "679121", "678101"]:
            obj, _ = PostalCode.objects.get_or_create(code=code)
            postal_codes.append(obj)

        return {
            "wards": wards,
            "taluks": taluks,
            "cities": cities,
            "states": states,
            "countries": countries,
            "postal_codes": postal_codes,
        }


    def create_house_registration_data(self):
        self.stdout.write('Creating house registration sample data...')

        geo = self.create_membership_geography_data()
        wards = geo["wards"]
        taluks = geo["taluks"]
        cities = geo["cities"]
        states = geo["states"]
        countries = geo["countries"]
        postal_codes = geo["postal_codes"]

        houses_data = [
            {
                'house_name': 'Ahmed House',
                'house_number': 'H-001',
                'ward': wards[0] if wards else None,
                'taluk': taluks[0] if taluks else None,
                'city': cities[0] if cities else None,
                'state': states[0] if states else None,
                'country': countries[0] if countries else None,
                'postal_code': postal_codes[0] if postal_codes else None,
            },
            {
                'house_name': 'Khan House',
                'house_number': 'H-002',
                'ward': wards[1] if len(wards) > 1 else (wards[0] if wards else None),
                'taluk': taluks[1] if len(taluks) > 1 else (taluks[0] if taluks else None),
                'city': cities[1] if len(cities) > 1 else (cities[0] if cities else None),
                'state': states[0] if states else None,
                'country': countries[0] if countries else None,
                'postal_code': postal_codes[1] if len(postal_codes) > 1 else (postal_codes[0] if postal_codes else None),
            },
            {
                'house_name': 'Patel House',
                'house_number': 'H-003',
                'ward': wards[2] if len(wards) > 2 else (wards[0] if wards else None),
                'taluk': taluks[2] if len(taluks) > 2 else (taluks[0] if taluks else None),
                'city': cities[2] if len(cities) > 2 else (cities[0] if cities else None),
                'state': states[0] if states else None,
                'country': countries[0] if countries else None,
                'postal_code': postal_codes[2] if len(postal_codes) > 2 else (postal_codes[0] if postal_codes else None),
            },
            {
                'house_name': 'Ali House',
                'house_number': 'H-004',
                'ward': wards[3] if len(wards) > 3 else (wards[0] if wards else None),
                'taluk': taluks[3] if len(taluks) > 3 else (taluks[0] if taluks else None),
                'city': cities[3] if len(cities) > 3 else (cities[0] if cities else None),
                'state': states[0] if states else None,
                'country': countries[0] if countries else None,
                'postal_code': postal_codes[3] if len(postal_codes) > 3 else (postal_codes[0] if postal_codes else None),
            },
            {
                'house_name': 'Hassan House',
                'house_number': 'H-005',
                'ward': wards[0] if wards else None,
                'taluk': taluks[0] if taluks else None,
                'city': cities[0] if cities else None,
                'state': states[0] if states else None,
                'country': countries[0] if countries else None,
                'postal_code': postal_codes[0] if postal_codes else None,
            },
        ]

        houses = []
        for house_data in houses_data:
            house, _ = HouseRegistration.objects.get_or_create(
                house_name=house_data.get("house_name", ""),
                house_number=house_data.get("house_number", ""),
                defaults=house_data,
            )
            houses.append(house)

        return houses


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

        # Create teachers with new standalone model fields
        teachers_data = [
            {
                'name': 'Abdul Rahman',
                'father_name': 'Mohammed Ali',
                'date_of_birth': date(1985, 5, 15),
                'blood_group': 'O+',
                'house_name': 'Rahman Manzil',
                'place': 'Main Street',
                'post_office': 'Central PO',
                'via': 'Market Road',
                'pin_code': '678001',
                'district': 'Palakkad',
                'state': 'Kerala',
                'lsg_name': 'Palakkad Municipality',
                'land_phone': '0491-2550101',
                'mobile_no': '9876543210',
                'teaching_level': 'primary',
                'islamic_qualification': 'Hafiz, Islamic Studies Degree',
                'general_qualification': 'BA Arabic',
                'organization': 'none'
            },
            {
                'name': 'Yusuf Khan',
                'father_name': 'Ibrahim Khan',
                'date_of_birth': date(1988, 8, 20),
                'blood_group': 'A+',
                'house_name': 'Khan Villa',
                'place': 'West Fort',
                'post_office': 'West PO',
                'via': 'Fort Road',
                'pin_code': '678002',
                'district': 'Palakkad',
                'state': 'Kerala',
                'lsg_name': 'Palakkad Municipality',
                'land_phone': '0491-2550102',
                'mobile_no': '9876543211',
                'teaching_level': 'secondary',
                'islamic_qualification': 'Arabic Literature Degree',
                'general_qualification': 'MA English',
                'organization': 'other',
                'membership_no': 'MEM123',
                'unit_name': 'West Unit',
                'unit_secretary_name': 'Hamza',
                'unit_secretary_mobile': '9876543220'
            },
            {
                'name': 'Zaid Ali',
                'father_name': 'Hassan Ali',
                'date_of_birth': date(1990, 3, 10),
                'blood_group': 'B+',
                'house_name': 'Ali House',
                'place': 'Kalpathy',
                'post_office': 'Kalpathy PO',
                'via': 'River Road',
                'pin_code': '678003',
                'district': 'Palakkad',
                'state': 'Kerala',
                'lsg_name': 'Palakkad Municipality',
                'land_phone': '0491-2550103',
                'mobile_no': '9876543212',
                'teaching_level': 'higher_secondary',
                'islamic_qualification': 'Islamic Theology Masters',
                'general_qualification': 'B.Ed',
                'organization': 'none'
            },
        ]

        teachers = []
        for teacher_data in teachers_data:
            teacher, created = Teacher.objects.get_or_create(
                name=teacher_data['name'],
                defaults=teacher_data
            )
            teachers.append(teacher)
            if created:
                self.stdout.write(f"Created teacher: {teacher.name}")

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
            cat, created = DonationCategory.objects.get_or_create(
                name=cat_data['name'],
                defaults=cat_data
            )
            donation_categories.append(cat)
            if created:
                self.stdout.write(f"Created donation category: {cat.name}")

        # Create expense categories
        expense_categories_data = [
            {'name': 'Utilities', 'description': 'Electricity, water, gas bills'},
            {'name': 'Maintenance', 'description': 'Building and facility maintenance'},
            {'name': 'Salaries', 'description': 'Staff and teacher salaries'},
            {'name': 'Supplies', 'description': 'Office and educational supplies'},
        ]

        expense_categories = []
        for cat_data in expense_categories_data:
            cat, created = ExpenseCategory.objects.get_or_create(
                name=cat_data['name'],
                defaults=cat_data
            )
            expense_categories.append(cat)
            if created:
                self.stdout.write(f"Created expense category: {cat.name}")

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

        for booking_data in bookings_data:
            AuditoriumBooking.objects.create(**booking_data)

    def create_hr_data(self):
        self.stdout.write('Creating HR sample data...')

        # Create staff positions
        positions_data = [
            {'name': 'imam', 'description': 'Lead prayer and religious guidance'},
            {'name': 'assistant_imam', 'description': 'Assist with prayers and religious duties'},
            {'name': 'muazzin', 'description': 'Call to prayer'},
            {'name': 'administrator', 'description': 'Administrative staff'},
            {'name': 'cleaner', 'description': 'Maintenance and cleaning staff'},
        ]

        positions = []
        for pos_data in positions_data:
            pos, created = StaffPosition.objects.get_or_create(
                name=pos_data['name'],
                defaults=pos_data
            )
            positions.append(pos)
            if created:
                self.stdout.write(f"Created staff position: {pos.get_name_display()}")

        # Get members to make staff (exclude those already teachers or staff)
        existing_staff_members = StaffMember.objects.values_list('member_id', flat=True)
        existing_staff_members = StaffMember.objects.values_list('member_id', flat=True)
        # Teacher is no longer a Member, so we don't need to exclude them from Staff creation
        available_members = Member.objects.exclude(
            id__in=list(existing_staff_members)
        )[:5]

        if len(available_members) < len(positions):
            self.stdout.write(self.style.WARNING('Not enough members available to create all staff positions.'))
            available_members = list(available_members)

        # Create staff members
        staff_members = []
        for i, member in enumerate(available_members[:len(positions)]):
            staff_member, created = StaffMember.objects.get_or_create(
                member=member,
                defaults={
                    'position': positions[i],
                    'employment_type': 'full_time' if i < 2 else 'part_time',
                    'hire_date': date(2023, 1, 1) + timedelta(days=i*30),
                    'base_salary': Decimal('3000.00') if i < 2 else Decimal('1500.00'),
                    'working_hours_per_week': 40 if i < 2 else 20,
                    'is_active': True
                }
            )
            staff_members.append(staff_member)
            if created:
                self.stdout.write(f"Created staff member: {staff_member.member.full_name}")

        # Create leave types
        leave_types_data = [
            {'name': 'Annual Leave', 'description': 'Annual vacation leave', 'days_allowed_per_year': 20, 'is_paid': True},
            {'name': 'Sick Leave', 'description': 'Medical leave', 'days_allowed_per_year': 10, 'is_paid': True},
            {'name': 'Personal Leave', 'description': 'Personal matters', 'days_allowed_per_year': 5, 'is_paid': False},
        ]

        leave_types = []
        for lt_data in leave_types_data:
            lt, created = LeaveType.objects.get_or_create(
                name=lt_data['name'],
                defaults=lt_data
            )
            leave_types.append(lt)
            if created:
                self.stdout.write(f"Created leave type: {lt.name}")

        # Create sample attendance records for last 7 days
        if staff_members:
            base_date = date.today() - timedelta(days=7)
            for i in range(7):
                current_date = base_date + timedelta(days=i)
                for staff in staff_members[:3]:  # Only for first 3 staff
                    if current_date.weekday() < 5:  # Weekdays only
                        Attendance.objects.get_or_create(
                            staff_member=staff,
                            date=current_date,
                            defaults={
                                'check_in_time': time(9, 0),
                                'check_out_time': time(17, 0),
                                'hours_worked': Decimal('8.00'),
                                'status': 'present'
                            }
                        )

        # Create salary components
        salary_components_data = [
            {'name': 'Basic Salary', 'component_type': 'basic', 'description': 'Base salary', 'is_taxable': True},
            {'name': 'Housing Allowance', 'component_type': 'allowance', 'description': 'Housing allowance', 'is_taxable': True},
            {'name': 'Transport Allowance', 'component_type': 'allowance', 'description': 'Transportation allowance', 'is_taxable': True},
            {'name': 'Tax Deduction', 'component_type': 'deduction', 'description': 'Income tax', 'is_taxable': False},
        ]

        salary_components = []
        for sc_data in salary_components_data:
            sc, created = SalaryComponent.objects.get_or_create(
                name=sc_data['name'],
                defaults=sc_data
            )
            salary_components.append(sc)
            if created:
                self.stdout.write(f"Created salary component: {sc.name}")

        # Create staff salaries
        if staff_members and salary_components:
            for staff in staff_members[:3]:
                # Basic salary
                basic_component = next((sc for sc in salary_components if sc.component_type == 'basic'), None)
                if basic_component:
                    StaffSalary.objects.get_or_create(
                        staff_member=staff,
                        salary_component=basic_component,
                        defaults={
                            'amount': staff.base_salary,
                            'effective_date': staff.hire_date,
                            'is_active': True
                        }
                    )

    def create_committee_data(self):
        self.stdout.write('Creating committee sample data...')

        # Create committee types
        committee_types_data = [
            {'name': 'Executive Board', 'description': 'Main governing body'},
            {'name': 'Education Committee', 'description': 'Oversees educational programs'},
            {'name': 'Finance Committee', 'description': 'Manages financial matters'},
            {'name': 'Maintenance Committee', 'description': 'Building and facility maintenance'},
        ]

        committee_types = []
        for ct_data in committee_types_data:
            ct, created = CommitteeType.objects.get_or_create(
                name=ct_data['name'],
                defaults=ct_data
            )
            committee_types.append(ct)
            if created:
                self.stdout.write(f"Created committee type: {ct.name}")

        # Get members for committees
        members = list(Member.objects.all()[:10])
        if len(members) < 5:
            self.stdout.write(self.style.WARNING('Not enough members available for committees.'))
            return

        # Create committees
        committees_data = [
            {'name': 'Executive Board', 'committee_type': committee_types[0], 'chairperson': members[0], 'secretary': members[1], 'established_date': date(2020, 1, 1)},
            {'name': 'Education Committee', 'committee_type': committee_types[1], 'chairperson': members[2], 'secretary': members[3], 'established_date': date(2021, 3, 1)},
            {'name': 'Finance Committee', 'committee_type': committee_types[2], 'chairperson': members[4], 'secretary': members[0], 'established_date': date(2021, 6, 1)},
        ]

        committees = []
        for comm_data in committees_data:
            comm, created = Committee.objects.get_or_create(
                name=comm_data['name'],
                defaults=comm_data
            )
            committees.append(comm)
            if created:
                self.stdout.write(f"Created committee: {comm.name}")

        # Create committee members
        if committees and members:
            for i, committee in enumerate(committees):
                # Add chairperson and secretary
                CommitteeMember.objects.get_or_create(
                    committee=committee,
                    member=committee.chairperson,
                    defaults={
                        'role': 'Chairperson',
                        'joined_date': committee.established_date,
                        'is_active': True
                    }
                )
                if committee.secretary:
                    CommitteeMember.objects.get_or_create(
                        committee=committee,
                        member=committee.secretary,
                        defaults={
                            'role': 'Secretary',
                            'joined_date': committee.established_date,
                            'is_active': True
                        }
                    )
                # Add a few more members
                for member in members[5:8]:
                    CommitteeMember.objects.get_or_create(
                        committee=committee,
                        member=member,
                        defaults={
                            'role': 'Member',
                            'joined_date': committee.established_date,
                            'is_active': True
                        }
                    )

        # Create trustees
        if members:
            trustee_positions = ['president', 'vice_president', 'secretary', 'treasurer']
            for i, position in enumerate(trustee_positions[:min(len(trustee_positions), len(members))]):
                Trustee.objects.get_or_create(
                    member=members[i],
                    defaults={
                        'position': position,
                        'appointed_date': date(2023, 1, 1),
                        'is_active': True
                    }
                )

        # Create sample meetings
        if committees:
            from django.contrib.auth.models import User
            admin_user = User.objects.filter(is_superuser=True).first()
            if not admin_user:
                admin_user = User.objects.first()

            meetings_data = [
                {
                    'committee': committees[0],
                    'meeting_type': 'regular',
                    'title': 'Monthly Executive Board Meeting',
                    'scheduled_date': date.today() + timedelta(days=7),
                    'scheduled_time': time(18, 0),
                    'agenda': 'Review monthly reports, budget approval, upcoming events',
                    'status': 'scheduled',
                    'created_by': admin_user
                },
                {
                    'committee': committees[1],
                    'meeting_type': 'regular',
                    'title': 'Education Committee Meeting',
                    'scheduled_date': date.today() + timedelta(days=14),
                    'scheduled_time': time(17, 30),
                    'agenda': 'Review class schedules, teacher assignments, student progress',
                    'status': 'scheduled',
                    'created_by': admin_user
                },
            ]

            for meeting_data in meetings_data:
                meeting, created = Meeting.objects.get_or_create(
                    committee=meeting_data['committee'],
                    title=meeting_data['title'],
                    scheduled_date=meeting_data['scheduled_date'],
                    defaults=meeting_data
                )
                if created:
                    self.stdout.write(f"Created meeting: {meeting.title}")

                    # Add attendees
                    committee_members = CommitteeMember.objects.filter(
                        committee=meeting.committee,
                        is_active=True
                    )[:5]
                    for cm in committee_members:
                        MeetingAttendee.objects.get_or_create(
                            meeting=meeting,
                            member=cm.member,
                            defaults={'attended': False}
                        )
    def create_accounting_data(self):
        self.stdout.write('Creating accounting sample data...')
        
        # 1. Categories
        assets, _ = AccountCategory.objects.get_or_create(name='Assets', category_type='asset')
        liabi, _ = AccountCategory.objects.get_or_create(name='Liabilities', category_type='liability')
        equity, _ = AccountCategory.objects.get_or_create(name='Equity', category_type='equity')
        revenue, _ = AccountCategory.objects.get_or_create(name='Revenue', category_type='revenue')
        expense, _ = AccountCategory.objects.get_or_create(name='Expenses', category_type='expense')

        # 2. Accounts
        accounts_data = [
            {'code': '1001', 'name': 'Main Cash', 'category': assets},
            {'code': '1002', 'name': 'Bank Account', 'category': assets},
            {'code': '4001', 'name': 'Donations Revenue', 'category': revenue},
            {'code': '4002', 'name': 'Membership Dues Revenue', 'category': revenue},
            {'code': '4003', 'name': 'Asset Rental Revenue', 'category': revenue},
            {'code': '5001', 'name': 'General Expenses', 'category': expense},
            {'code': '5002', 'name': 'Utility Expenses', 'category': expense},
            {'code': '5003', 'name': 'Salary Expenses', 'category': expense},
        ]

        accounts = {}
        for acc_data in accounts_data:
            acc, created = Account.objects.get_or_create(code=acc_data['code'], defaults=acc_data)
            accounts[acc_data['code']] = acc
            if created:
                self.stdout.write(f"Created account: {acc}")

        # 3. Some sample transactions
        tx1 = Transaction.objects.create(
            date=date.today() - timedelta(days=5),
            description="Initial Cash Deposit",
            reference="DEP001"
        )
        JournalEntry.objects.create(transaction=tx1, account=accounts['1001'], debit=Decimal('5000.00'))
        JournalEntry.objects.create(transaction=tx1, account=accounts['1002'], credit=Decimal('5000.00'))

    def create_billing_data(self):
        self.stdout.write('Creating billing sample data...')
        
        # Ensure accounts exist first
        self.create_accounting_data()
        
        houses = list(HouseRegistration.objects.all())
        if not houses:
            self.stdout.write(self.style.WARNING('No houses available for billing. Skipping.'))
            return

        shops = list(Shop.objects.all())

        # Create some invoices
        for i, house in enumerate(houses[:3]):
            invoice = Invoice.objects.create(
                invoice_number=f"INV-HOUSE-{house.id}-{random.randint(1000, 9999)}",
                house=house,
                date_issued=date.today() - timedelta(days=10),
                due_date=date.today() + timedelta(days=20),
                status='sent',
                total_amount=Decimal('50.00')
            )
            InvoiceLineItem.objects.create(
                invoice=invoice,
                description="Monthly Membership Dues - Jan 2024",
                amount=Decimal('50.00')
            )

        for i, shop in enumerate(shops[:2]):
            invoice = Invoice.objects.create(
                invoice_number=f"INV-SHP-{shop.id}-{random.randint(1000, 9999)}",
                shop=shop,
                date_issued=date.today() - timedelta(days=5),
                due_date=date.today() + timedelta(days=25),
                status='sent',
                total_amount=shop.monthly_rent
            )
            InvoiceLineItem.objects.create(
                invoice=invoice,
                description=f"Monthly Rent - {shop.name}",
                amount=shop.monthly_rent
            )
            
            # Create a partial payment
            BillingPayment.objects.create(
                invoice=invoice,
                amount=Decimal('500.00'),
                payment_date=date.today(),
                payment_method='cash',
                transaction_id=f"PAY-{random.randint(100000, 999999)}"
            )
