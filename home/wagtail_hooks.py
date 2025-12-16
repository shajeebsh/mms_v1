from wagtail import hooks
from wagtail.admin.menu import Menu, SubmenuMenuItem

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

    # Map group names to submenu labels used in `home/admin_menu.py`
    group_to_label = {
        "membership": "🏠 Membership",
        "finance": "💰 Finance",
        "education": "👨‍🏫 Education",
        "assets": "🏢 Assets",
        "operations": "📅 Operations",
        "hr": "👥 HR & Payroll",
        "committee": "🏛️ Committee & Minutes",
    }

    user_groups = set(g.name.lower() for g in user.groups.all())
    allowed_labels = set(group_to_label[g] for g in user_groups if g in group_to_label)

    if not allowed_labels:
        # If user has no matching group, hide the administration menu entirely
        menu_items[:] = [m for m in menu_items if m is not admin_item]
        return

    # Filter the administration submenu to only include allowed submenus
    filtered = []
    for sub in admin_item.menu.items:
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
