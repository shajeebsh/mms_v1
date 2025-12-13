from wagtail.admin.menu import MenuItem
from wagtail import hooks


# Membership menu items
@hooks.register('register_admin_menu_item')
def register_families_menu():
    from membership.wagtail_hooks import FamilyAdmin
    return MenuItem(label='🏠 Families', url=FamilyAdmin().url_helper.index_url, icon_name='group', order=100)

@hooks.register('register_admin_menu_item')
def register_members_menu():
    from membership.wagtail_hooks import MemberAdmin
    return MenuItem(label='👥 Members', url=MemberAdmin().url_helper.index_url, icon_name='user', order=101)

@hooks.register('register_admin_menu_item')
def register_vital_records_menu():
    from membership.wagtail_hooks import VitalRecordAdmin
    return MenuItem(label='📋 Vital Records', url=VitalRecordAdmin().url_helper.index_url, icon_name='date', order=102)


# Finance menu items
@hooks.register('register_admin_menu_item')
def register_donations_menu():
    from finance.wagtail_hooks import DonationAdmin
    return MenuItem(label='💰 Donations', url=DonationAdmin().url_helper.index_url, icon_name='money', order=200)

@hooks.register('register_admin_menu_item')
def register_expenses_menu():
    from finance.wagtail_hooks import ExpenseAdmin
    return MenuItem(label='💸 Expenses', url=ExpenseAdmin().url_helper.index_url, icon_name='minus', order=201)

@hooks.register('register_admin_menu_item')
def register_financial_reports_menu():
    from finance.wagtail_hooks import FinancialReportAdmin
    return MenuItem(label='📊 Financial Reports', url=FinancialReportAdmin().url_helper.index_url, icon_name='chart-bar', order=202)

@hooks.register('register_admin_menu_item')
def register_donation_categories_menu():
    from finance.wagtail_hooks import DonationCategoryAdmin
    return MenuItem(label='🏷️ Donation Categories', url=DonationCategoryAdmin().url_helper.index_url, icon_name='tag', order=203)

@hooks.register('register_admin_menu_item')
def register_expense_categories_menu():
    from finance.wagtail_hooks import ExpenseCategoryAdmin
    return MenuItem(label='🏷️ Expense Categories', url=ExpenseCategoryAdmin().url_helper.index_url, icon_name='tag', order=204)


# Education menu items
@hooks.register('register_admin_menu_item')
def register_teachers_menu():
    from education.wagtail_hooks import TeacherAdmin
    return MenuItem(label='👨‍🏫 Teachers', url=TeacherAdmin().url_helper.index_url, icon_name='user', order=300)

@hooks.register('register_admin_menu_item')
def register_classes_menu():
    from education.wagtail_hooks import ClassAdmin
    return MenuItem(label='📖 Classes', url=ClassAdmin().url_helper.index_url, icon_name='book', order=301)

@hooks.register('register_admin_menu_item')
def register_student_enrollments_menu():
    from education.wagtail_hooks import StudentEnrollmentAdmin
    return MenuItem(label='🎓 Student Enrollments', url=StudentEnrollmentAdmin().url_helper.index_url, icon_name='user', order=302)


# Assets menu items
@hooks.register('register_admin_menu_item')
def register_shops_menu():
    from assets.wagtail_hooks import ShopAdmin
    return MenuItem(label='🏪 Shops', url=ShopAdmin().url_helper.index_url, icon_name='shopping-cart', order=400)

@hooks.register('register_admin_menu_item')
def register_property_units_menu():
    from assets.wagtail_hooks import PropertyUnitAdmin
    return MenuItem(label='🏠 Property Units', url=PropertyUnitAdmin().url_helper.index_url, icon_name='home', order=401)


# Operations menu items
@hooks.register('register_admin_menu_item')
def register_auditorium_bookings_menu():
    from operations.wagtail_hooks import AuditoriumBookingAdmin
    return MenuItem(label='📅 Auditorium Bookings', url=AuditoriumBookingAdmin().url_helper.index_url, icon_name='calendar', order=500)

@hooks.register('register_admin_menu_item')
def register_prayer_times_menu():
    from operations.wagtail_hooks import PrayerTimeAdmin
    return MenuItem(label='🕌 Prayer Times', url=PrayerTimeAdmin().url_helper.index_url, icon_name='time', order=501)

@hooks.register('register_admin_menu_item')
def register_digital_signage_menu():
    from operations.wagtail_hooks import DigitalSignageContentAdmin
    return MenuItem(label='📺 Digital Signage', url=DigitalSignageContentAdmin().url_helper.index_url, icon_name='media', order=502)