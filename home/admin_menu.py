from wagtail import hooks
from wagtail.admin.menu import Menu, MenuItem, SubmenuMenuItem


@hooks.register("register_admin_menu_item")
def register_administration_menu():
    """Register the main Administration menu with submenus"""

    # Create membership submenu
    membership_menu = Menu(
        items=[
            MenuItem(
                label="👥 Members",
                url=get_membership_url("MemberAdmin"),
                icon_name="user",
                order=1,
            ),
            MenuItem(
                label="🏠 Families",
                url=get_membership_url("FamilyAdmin"),
                icon_name="group",
                order=2,
            ),
            MenuItem(
                label="� Membership Dues",
                url=get_membership_url("MembershipDuesAdmin"),
                icon_name="money",
                order=3,
            ),
            MenuItem(
                label="💳 Payments",
                url=get_membership_url("PaymentAdmin"),
                icon_name="credit-card",
                order=4,
            ),
            MenuItem(
                label="📋 Vital Records",
                url=get_membership_url("VitalRecordAdmin"),
                icon_name="date",
                order=5,
            ),
            MenuItem(
                label="⚡ Bulk Payment",
                url="/membership/bulk-payment/",
                icon_name="plus",
                order=6,
            ),
            MenuItem(
                label="📊 Generate Monthly Dues",
                url="/membership/generate-monthly-dues/",
                icon_name="calendar",
                order=7,
            ),
        ]
    )

    # Create finance submenu
    finance_menu = Menu(
        items=[
            MenuItem(
                label="💰 Donations",
                url=get_finance_url("DonationAdmin"),
                icon_name="money",
                order=1,
            ),
            MenuItem(
                label="💸 Expenses",
                url=get_finance_url("ExpenseAdmin"),
                icon_name="minus",
                order=2,
            ),
            MenuItem(
                label="📊 Financial Reports",
                url=get_finance_url("FinancialReportAdmin"),
                icon_name="chart-bar",
                order=3,
            ),
            MenuItem(
                label="🏷️ Donation Categories",
                url=get_finance_url("DonationCategoryAdmin"),
                icon_name="tag",
                order=4,
            ),
            MenuItem(
                label="🏷️ Expense Categories",
                url=get_finance_url("ExpenseCategoryAdmin"),
                icon_name="tag",
                order=5,
            ),
            MenuItem(
                label="⚠️ Overdue Membership Dues",
                url="/membership/overdue-report/",
                icon_name="warning",
                order=6,
            ),
        ]
    )

    # Create education submenu
    education_menu = Menu(
        items=[
            MenuItem(
                label="👨‍🏫 Teachers",
                url=get_education_url("TeacherAdmin"),
                icon_name="user",
                order=1,
            ),
            MenuItem(
                label="📖 Classes",
                url=get_education_url("ClassAdmin"),
                icon_name="book",
                order=2,
            ),
            MenuItem(
                label="🎓 Student Enrollments",
                url=get_education_url("StudentEnrollmentAdmin"),
                icon_name="user",
                order=3,
            ),
        ]
    )

    # Create assets submenu
    assets_menu = Menu(
        items=[
            MenuItem(
                label="🏪 Shops",
                url=get_assets_url("ShopAdmin"),
                icon_name="shopping-cart",
                order=1,
            ),
            MenuItem(
                label="🏠 Property Units",
                url=get_assets_url("PropertyUnitAdmin"),
                icon_name="home",
                order=2,
            ),
        ]
    )

    # Create operations submenu
    operations_menu = Menu(
        items=[
            MenuItem(
                label="📅 Auditorium Bookings",
                url=get_operations_url("AuditoriumBookingAdmin"),
                icon_name="calendar",
                order=1,
            ),
            MenuItem(
                label="🕌 Prayer Times",
                url=get_operations_url("PrayerTimeAdmin"),
                icon_name="time",
                order=2,
            ),
            MenuItem(
                label="📺 Digital Signage",
                url=get_operations_url("DigitalSignageContentAdmin"),
                icon_name="media",
                order=3,
            ),
        ]
    )

    # Create main administration menu with submenus
    administration_menu = Menu(
        items=[
            SubmenuMenuItem(
                label="🏠 Membership", menu=membership_menu, icon_name="group", order=1
            ),
            SubmenuMenuItem(
                label="💰 Finance", menu=finance_menu, icon_name="money", order=2
            ),
            SubmenuMenuItem(
                label="👨‍🏫 Education", menu=education_menu, icon_name="user", order=3
            ),
            SubmenuMenuItem(
                label="🏢 Assets", menu=assets_menu, icon_name="home", order=4
            ),
            SubmenuMenuItem(
                label="📅 Operations",
                menu=operations_menu,
                icon_name="calendar",
                order=5,
            ),
        ]
    )

    return SubmenuMenuItem(
        label="⚙️ Administration", menu=administration_menu, icon_name="cog", order=1000
    )


# Helper functions to get URLs
def get_membership_url(admin_class_name):
    from membership import wagtail_hooks

    admin_class = getattr(wagtail_hooks, admin_class_name)
    return admin_class().url_helper.index_url


def get_finance_url(admin_class_name):
    from finance import wagtail_hooks

    admin_class = getattr(wagtail_hooks, admin_class_name)
    return admin_class().url_helper.index_url


def get_education_url(admin_class_name):
    from education import wagtail_hooks

    admin_class = getattr(wagtail_hooks, admin_class_name)
    return admin_class().url_helper.index_url


def get_assets_url(admin_class_name):
    from assets import wagtail_hooks

    admin_class = getattr(wagtail_hooks, admin_class_name)
    return admin_class().url_helper.index_url


def get_operations_url(admin_class_name):
    from operations import wagtail_hooks

    admin_class = getattr(wagtail_hooks, admin_class_name)
    return admin_class().url_helper.index_url
