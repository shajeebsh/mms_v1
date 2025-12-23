from wagtail_modeladmin.helpers import PermissionHelper
from home.models import AccessControlSettings
from wagtail.models import Site

class ACLPermissionHelper(PermissionHelper):
    """
    Permission helper that checks AccessControlSettings instead of standard Django permissions.
    """

    def _get_user_type(self, user):
        try:
            if hasattr(user, 'profile'):
                return user.profile.user_type
        except Exception:
            pass
        return "staff" # Default fallback

    def _is_module_allowed(self, user):
        """Check if the module (app_label) is allowed for this user."""
        if user.is_superuser:
            return True

        module_name = self.model._meta.app_label
        user_type = self._get_user_type(user)

        # Get settings
        # Note: In a helper we might not have 'request', so we try to get the default site settings
        try:
            site = Site.objects.filter(is_default_site=True).first()
            if not site:
                site = Site.objects.first()
            
            if site:
                settings = AccessControlSettings.for_site(site)
            else:
                settings = AccessControlSettings.objects.first()
        except Exception:
            # If we can't get settings, fallback to safe default (deny) or try object lookup
             settings = AccessControlSettings.objects.first()
        
        if not settings:
            # No settings defined at all, default deny for safety
            return False

        allowed_modules = []
        if user_type == "admin":
            allowed_modules = settings.admin_modules or []
        elif user_type == "executive":
            allowed_modules = settings.executive_modules or []
        else: # staff
            allowed_modules = settings.staff_modules or []

        return module_name in allowed_modules

    def user_can_list(self, user):
        return self._is_module_allowed(user)

    def user_can_create(self, user):
        return self._is_module_allowed(user)

    def user_can_edit_obj(self, user, obj):
        return self._is_module_allowed(user)

    def user_can_delete_obj(self, user, obj):
        return self._is_module_allowed(user)
