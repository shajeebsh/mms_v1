from wagtail.admin.panels import FieldPanel
from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register

from .models import AuditoriumBooking, PrayerTime, DigitalSignageContent


class AuditoriumBookingAdmin(ModelAdmin):
    model = AuditoriumBooking
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


class PrayerTimeAdmin(ModelAdmin):
    model = PrayerTime
    menu_label = 'Prayer Times'
    menu_icon = 'time'
    add_to_admin_menu = False  # Will be included in grouped menu
    list_display = ('prayer', 'date', 'time', 'location', 'is_jumah')
    list_filter = ('prayer', 'is_jumah', 'location')
    search_fields = ('prayer', 'location')
    panels = [
        FieldPanel('date'),
        FieldPanel('prayer'),
        FieldPanel('time'),
        FieldPanel('is_jumah'),
        FieldPanel('location'),
    ]


class DigitalSignageContentAdmin(ModelAdmin):
    model = DigitalSignageContent
    menu_label = 'Digital Signage'
    menu_icon = 'media'
    add_to_admin_menu = False  # Will be included in grouped menu
    list_display = ('title', 'content_type', 'display_start', 'display_end', 'is_active', 'priority')
    list_filter = ('content_type', 'is_active')
    search_fields = ('title', 'content')
    panels = [
        FieldPanel('title'),
        FieldPanel('content_type'),
        FieldPanel('content'),
        FieldPanel('image'),
        FieldPanel('video_url'),
        FieldPanel('display_start'),
        FieldPanel('display_end'),
        FieldPanel('is_active'),
        FieldPanel('priority'),
        FieldPanel('created_by'),
    ]


modeladmin_register(AuditoriumBookingAdmin)
modeladmin_register(PrayerTimeAdmin)
modeladmin_register(DigitalSignageContentAdmin)