from wagtail.admin.panels import FieldPanel
from wagtail_modeladmin.options import ModelAdmin, modeladmin_register

from .models import AuditoriumBooking


from home.permission_helpers import ACLPermissionHelper

class AuditoriumBookingAdmin(ModelAdmin):
    model = AuditoriumBooking
    permission_helper_class = ACLPermissionHelper
    menu_label = 'Auditorium Bookings'
    menu_icon = 'date'
    add_to_admin_menu = False  # Will be included in grouped menu
    list_display = ('event_name', 'booking_date', 'start_time', 'end_time', 'status', 'organizer')
    list_filter = ('status', 'booking_date')
    search_fields = ('event_name', 'organizer', 'contact_person')
    panels = [
        FieldPanel('event_name'),
        FieldPanel('organizer'),
        FieldPanel('contact_person'),
        FieldPanel('contact_email'),
        FieldPanel('contact_phone'),
        FieldPanel('booking_date'),
        FieldPanel('start_time'),
        FieldPanel('end_time'),
        FieldPanel('expected_attendees'),
        FieldPanel('purpose'),
        FieldPanel('special_requirements'),
        FieldPanel('status'),
        FieldPanel('approved_by'),
    ]


modeladmin_register(AuditoriumBookingAdmin)