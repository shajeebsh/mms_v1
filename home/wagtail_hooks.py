from wagtail import hooks
from wagtail.admin.menu import Menu, MenuItem, SubmenuMenuItem
from django.urls import reverse
from django.utils.html import format_html
from django.templatetags.static import static

@hooks.register("construct_main_menu")
def customize_main_menu(request, menu_items):
    """Show a filtered Administration menu depending on the user's group.

    Superusers see the full Administration menu. Other users see only the
    submenus that match their primary group (membership, finance, education,
    assets, operations, hr, committee).
    """

    # Find the Administration menu item (created in `home/admin_menu.py`)
    admin_index = None
    for idx, item in enumerate(menu_items):
        label = getattr(item, "label", "")
        if "Administration" in label or "⚙️" in label:
            admin_index = idx
            admin_item = item
            break

    if admin_index is None:
        return

    user = getattr(request, "user", None)
    if not user or user.is_anonymous:
        # hide administration for anonymous users
        menu_items[:] = [m for m in menu_items if m is not admin_item]
        return

    if user.is_superuser:
        return

    # Check module configuration first
    from home.models import SystemSettings, AccessControlSettings
    
    # Map group names to submenu labels used in `home/admin_menu.py`
    # Also doubles as module_name -> label mapping
    module_to_label = {
        "membership": "🏠 Membership",
        "finance": "💰 Finance",
        "education": "👨‍🏫 Education",
        "assets": "🏢 Assets",
        "operations": "📅 Operations",
        "hr": "👥 HR & Payroll",
        "committee": "🏛️ Committee & Minutes",
    }

    # Determine allowed modules for this user based on AccessControlSettings
    allowed_labels = set()
    
    # Get user profile to determine user type
    try:
        profile = user.profile
        user_type = profile.user_type
    except Exception:
        # Fallback if no profile exists (e.g. specialized admin accounts without profiles)
        user_type = "staff"
    
    # Get settings for the current site
    try:
        # AccessControlSettings is a site setting, so we get it for the current site
        # We need to handle the case where request might not be available or associated with a site correctly in some edge cases
        # But for construct_main_menu, request is standard.
        from wagtail.models import Site
        site = Site.find_for_request(request)
        if site:
            settings = AccessControlSettings.for_site(site)
        else:
            settings = AccessControlSettings.objects.first() # specific fallback
        
        if settings:
            if user_type == "admin":
                allowed_modules = settings.admin_modules or []
            elif user_type == "executive":
                allowed_modules = settings.executive_modules or []
            else: # staff
                allowed_modules = settings.staff_modules or []
                
            # Filter allowed modules: must be in allowed list AND enabled system-wide
            for module_name in allowed_modules:
                if module_name in module_to_label:
                    if SystemSettings.is_module_enabled(module_name):
                        allowed_labels.add(module_to_label[module_name])
    except Exception:
        # In case of any error (settings not initialized, etc.), fall back to showing nothing or safe defaults
        pass
    
    if not allowed_labels:
        # If user has no access, hide the administration menu entirely
        menu_items[:] = [m for m in menu_items if m is not admin_item]
        return

    # Filter the administration submenu to only include allowed submenus
    filtered = []
    menu_obj = getattr(admin_item, "menu", None)
    if menu_obj is None:
        # nothing to do if there's no menu
        menu_items[:] = [m for m in menu_items if m is not admin_item]
        return

    # support different Wagtail versions: try common attributes, fall back to iter
    if hasattr(menu_obj, "items"):
        sub_iter = menu_obj.items
    elif hasattr(menu_obj, "menu_items"):
        sub_iter = menu_obj.menu_items
    else:
        try:
            sub_iter = list(menu_obj)
        except Exception:
            sub_iter = []
            
    for sub in sub_iter:
        sublabel = getattr(sub, "label", "")
        if sublabel in allowed_labels:
            filtered.append(sub)

    if not filtered:
        menu_items[:] = [m for m in menu_items if m is not admin_item]
        return

    # Replace the admin item with a new one that contains only the filtered menu
    new_menu = Menu(items=filtered)
    new_admin_item = SubmenuMenuItem(label=admin_item.label, menu=new_menu, icon_name=getattr(admin_item, "icon_name", None), order=getattr(admin_item, "order", None))
    menu_items[admin_index] = new_admin_item


@hooks.register("construct_main_menu")
def filter_sample_data_menu(request, menu_items):
    """Hide Sample Data Management menu for non-superusers"""
    user = getattr(request, "user", None)
    if not user or user.is_anonymous or not user.is_superuser:
        # Remove Sample Data Management menu item
        menu_items[:] = [
            item for item in menu_items
            if getattr(item, "label", "") != "📊 Sample Data Management"
        ]


from home.admin_menu import register_administration_menu
register_administration_menu()

# Register custom admin home page
from django.urls import path
from . import views

@hooks.register('register_admin_urls')
def register_dashboard_url():
    return [
        path('', views.wagtail_dashboard_view, name='wagtailadmin_home'),
    ]

@hooks.register('insert_global_admin_css')
def global_admin_css():
    return format_html('<link rel="stylesheet" href="{}?v=3">', static('home/css/admin_theme.css'))

@hooks.register('insert_global_admin_js')
def global_admin_js():
    return format_html('<script>console.log("MMS Premium Theme Loaded");</script>')
