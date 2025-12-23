from wagtail import hooks
from wagtail.admin.menu import Menu, MenuItem, SubmenuMenuItem
from django.urls import reverse_lazy


def get_modeladmin_url(app, model):
    """Get the URL for a ModelAdmin index page lazily to avoid circular imports."""
    return reverse_lazy(f"{app}_{model}_modeladmin_index")


def register_administration_menu():
    """Register the main Administration menu with submenus"""

    # Create membership submenu
    membership_menu = Menu(
        items=[
            MenuItem(
                label="👥 Members",
                url=get_modeladmin_url("membership", "member"),
                icon_name="user",
                order=1,
            ),
            MenuItem(
                label="🏠 Families",
                url=get_modeladmin_url("membership", "family"),
                icon_name="group",
                order=2,
            ),
            MenuItem(
                label=" Membership Dues",
                url=get_modeladmin_url("membership", "membershipdues"),
                icon_name="money",
                order=3,
            ),
            MenuItem(
                label="💳 Payments",
                url=get_modeladmin_url("membership", "payment"),
                icon_name="credit-card",
                order=4,
            ),
            MenuItem(
                label="📋 Vital Records",
                url=get_modeladmin_url("membership", "vitalrecord"),
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
            MenuItem(
                label="📄 Membership Questionnaire",
                url=reverse_lazy("membership:download_questionnaire"),
                icon_name="doc-full",
                order=8,
            ),
        ]
    )

    # Create finance submenu
    finance_menu = Menu(
        items=[
            MenuItem(
                label="💰 Donations",
                url=get_modeladmin_url("finance", "donation"),
                icon_name="money",
                order=1,
            ),
            MenuItem(
                label="💸 Expenses",
                url=get_modeladmin_url("finance", "expense"),
                icon_name="minus",
                order=2,
            ),
            MenuItem(
                label="📊 Financial Reports",
                url=get_modeladmin_url("finance", "financialreport"),
                icon_name="chart-bar",
                order=3,
            ),
            MenuItem(
                label="🏷️ Donation Categories",
                url=get_modeladmin_url("finance", "donationcategory"),
                icon_name="tag",
                order=4,
            ),
            MenuItem(
                label="🏷️ Expense Categories",
                url=get_modeladmin_url("finance", "expensecategory"),
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
                url=get_modeladmin_url("education", "teacher"),
                icon_name="user",
                order=1,
            ),
            MenuItem(
                label="📖 Classes",
                url=get_modeladmin_url("education", "class"),
                icon_name="book",
                order=2,
            ),
            MenuItem(
                label="🎓 Student Enrollments",
                url=get_modeladmin_url("education", "studentenrollment"),
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
                url=get_modeladmin_url("assets", "shop"),
                icon_name="shopping-cart",
                order=1,
            ),
            MenuItem(
                label="🏠 Property Units",
                url=get_modeladmin_url("assets", "propertyunit"),
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
                url=get_modeladmin_url("operations", "auditoriumbooking"),
                icon_name="calendar",
                order=1,
            ),
            MenuItem(
                label="🕌 Prayer Times",
                url=get_modeladmin_url("operations", "prayertime"),
                icon_name="time",
                order=2,
            ),
            MenuItem(
                label="📺 Digital Signage",
                url=get_modeladmin_url("operations", "digitalsignagecontent"),
                icon_name="media",
                order=3,
            ),
        ]
    )

    # Create HR submenu
    hr_menu = Menu(
        items=[
            MenuItem(
                label="👥 Staff Directory",
                url=get_modeladmin_url("hr", "staffmember"),
                icon_name="user",
                order=1,
            ),
            MenuItem(
                label="📋 Staff Positions",
                url=get_modeladmin_url("hr", "staffposition"),
                icon_name="user",
                order=2,
            ),
            MenuItem(
                label="📅 Attendance Records",
                url=get_modeladmin_url("hr", "attendance"),
                icon_name="date",
                order=3,
            ),
            MenuItem(
                label="🏖️ Leave Requests",
                url=get_modeladmin_url("hr", "leaverequest"),
                icon_name="time",
                order=4,
            ),
            MenuItem(
                label="📝 Leave Types",
                url=get_modeladmin_url("hr", "leavetype"),
                icon_name="doc-full",
                order=5,
            ),
            MenuItem(
                label="💰 Payroll Records",
                url=get_modeladmin_url("hr", "payroll"),
                icon_name="money",
                order=6,
            ),
            MenuItem(
                label="⚙️ Salary Components",
                url=get_modeladmin_url("hr", "salarycomponent"),
                icon_name="cog",
                order=7,
            ),
            MenuItem(
                label="💵 Staff Salaries",
                url=get_modeladmin_url("hr", "staffsalary"),
                icon_name="download",
                order=8,
            ),
        ]
    )

    # Create committee submenu
    committee_menu = Menu(
        items=[
            MenuItem(
                label="🏛️ Trustees",
                url=get_modeladmin_url("committee", "trustee"),
                icon_name="user",
                order=1,
            ),
            MenuItem(
                label="📋 Trustee Meetings",
                url=get_modeladmin_url("committee", "trusteemeeting"),
                icon_name="date",
                order=2,
            ),
            MenuItem(
                label="👥 Committees",
                url=get_modeladmin_url("committee", "committee"),
                icon_name="group",
                order=3,
            ),
            MenuItem(
                label="📅 Committee Meetings",
                url=get_modeladmin_url("committee", "meeting"),
                icon_name="calendar",
                order=4,
            ),
            MenuItem(
                label="📝 Committee Types",
                url=get_modeladmin_url("committee", "committeetype"),
                icon_name="tag",
                order=5,
            ),
            MenuItem(
                label="👤 Committee Members",
                url=get_modeladmin_url("committee", "committeemember"),
                icon_name="user",
                order=6,
            ),
            MenuItem(
                label="✅ Meeting Attendees",
                url=get_modeladmin_url("committee", "meetingattendee"),
                icon_name="tick",
                order=7,
            ),
            MenuItem(
                label="📎 Meeting Attachments",
                url=get_modeladmin_url("committee", "meetingattachment"),
                icon_name="doc-full",
                order=8,
            ),
            MenuItem(
                label="📋 Trustee Meeting Attendees",
                url=get_modeladmin_url("committee", "trusteemeetingattendee"),
                icon_name="tick",
                order=9,
            ),
            MenuItem(
                label="📎 Trustee Meeting Attachments",
                url=get_modeladmin_url("committee", "trusteemeetingattachment"),
                icon_name="doc-full",
                order=10,
            ),
        ]
    )
    # Check module configuration - only include enabled modules
    from home.models import SystemSettings
    
    # Separate registration for each module to ensure they are top-level
    # and to comply with Wagtail's expectation of a single MenuItem from each hook function.
    
    class GroupRestrictedSubmenuMenuItem(SubmenuMenuItem):
        def __init__(self, label, menu, name=None, icon_name=None, classname=None, order=1000, required_groups=None):
            self.required_groups = required_groups or []
            super().__init__(label, menu, name=name, icon_name=icon_name, classname=classname, order=order)

        def is_shown(self, request):
            user = request.user
            if user.is_superuser:
                return True
                
            # Determine user type
            try:
                # Handle case where user might not have a profile
                if hasattr(user, 'profile'):
                    user_type = user.profile.user_type
                else:
                    user_type = "staff"
            except Exception:
                user_type = "staff"

            # Get Access Control Settings
            from home.models import AccessControlSettings
            from wagtail.models import Site
            
            settings = None
            try:
                site = Site.find_for_request(request)
                if site:
                    settings = AccessControlSettings.for_site(site)
            except Exception:
                pass
            
            if not settings:
                # Try getting the first site or any settings object
                try:
                    settings = AccessControlSettings.objects.first()
                except Exception:
                    pass

            # If still no settings, we can either default to ALLOWING nothing or defaulting to legacy groups.
            # Given the user wants ACL Control, defaulting to legacy groups as fallback seems reasonable 
            # OR finding a way to force-create settings? 
            # For now, if no settings exist at all, we fall back to groups.
            if not settings:
                if not self.required_groups:
                    return True
                return user.groups.filter(name__in=self.required_groups).exists()

            # Determine allowed modules for this user type
            allowed_modules = []
            if user_type == "admin":
                allowed_modules = settings.admin_modules or []
            elif user_type == "executive":
                allowed_modules = settings.executive_modules or []
            else: # staff
                allowed_modules = settings.staff_modules or []
            
            # Check if this menu item's module is allowed
            if self.required_groups:
                module_name = self.required_groups[0]
                if module_name in allowed_modules:
                    return True
            
            return False

    menu_items = []
    order = 1
    
    if SystemSettings.is_module_enabled("membership"):
        menu_items.append(
            GroupRestrictedSubmenuMenuItem(
                label="🏠 Membership", 
                menu=membership_menu, 
                icon_name="group", 
                order=order,
                required_groups=['membership']
            )
        )
        order += 1
    
    if SystemSettings.is_module_enabled("finance"):
        menu_items.append(
            GroupRestrictedSubmenuMenuItem(
                label="💰 Finance", 
                menu=finance_menu, 
                icon_name="money", 
                order=order,
                required_groups=['finance']
            )
        )
        order += 1
    
    if SystemSettings.is_module_enabled("education"):
        menu_items.append(
            GroupRestrictedSubmenuMenuItem(
                label="👨‍🏫 Education", 
                menu=education_menu, 
                icon_name="user", 
                order=order,
                required_groups=['education']
            )
        )
        order += 1
    
    if SystemSettings.is_module_enabled("assets"):
        menu_items.append(
            GroupRestrictedSubmenuMenuItem(
                label="🏢 Assets", 
                menu=assets_menu, 
                icon_name="home", 
                order=order,
                required_groups=['assets']
            )
        )
        order += 1
    
    if SystemSettings.is_module_enabled("operations"):
        menu_items.append(
            GroupRestrictedSubmenuMenuItem(
                label="📅 Operations",
                menu=operations_menu,
                icon_name="calendar",
                order=order,
                required_groups=['operations']
            )
        )
        order += 1
    
    if SystemSettings.is_module_enabled("hr"):
        menu_items.append(
            GroupRestrictedSubmenuMenuItem(
                label="👥 HR & Payroll", 
                menu=hr_menu, 
                icon_name="user", 
                order=order,
                required_groups=['hr']
            )
        )
        order += 1
    
    if SystemSettings.is_module_enabled("committee"):
        menu_items.append(
            GroupRestrictedSubmenuMenuItem(
                label="🏛️ Committee & Minutes",
                menu=committee_menu,
                icon_name="group",
                order=order,
                required_groups=['committee']
            )
        )
        order += 1

    # We define a helper to register each submenu
    def register_submenu(item):
        def hook():
            return item
        hooks.register("register_admin_menu_item", hook)

    for item in menu_items:
        register_submenu(item)
    
    return None # The original hook function now returns nothing as it did the registration


@hooks.register("register_admin_menu_item")
def register_sample_data_management_menu():
    """Register Sample Data Management menu item (admin-only)"""
    from django.urls import reverse
    return MenuItem(
        "📊 Sample Data Management",
        reverse("home_admin:sample_data_management"),
        icon_name="cog",
        order=2000,
    )
