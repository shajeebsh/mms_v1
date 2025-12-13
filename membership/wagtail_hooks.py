from wagtail.admin.panels import FieldPanel
from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register

from .models import Family, Member, VitalRecord


class FamilyAdmin(ModelAdmin):
    model = Family
    menu_label = 'Families'
    menu_icon = 'group'
    list_display = ('name', 'phone', 'email', 'created_at')
    search_fields = ('name', 'phone', 'email')
    panels = [
        FieldPanel('name'),
        FieldPanel('address'),
        FieldPanel('phone'),
        FieldPanel('email'),
    ]


class MemberAdmin(ModelAdmin):
    model = Member
    menu_label = 'Members'
    menu_icon = 'user'
    list_display = ('full_name', 'family', 'date_of_birth', 'gender', 'is_active')
    list_filter = ('gender', 'is_active', 'family')
    search_fields = ('first_name', 'last_name', 'email', 'phone')
    panels = [
        FieldPanel('first_name'),
        FieldPanel('last_name'),
        FieldPanel('date_of_birth'),
        FieldPanel('gender'),
        FieldPanel('family'),
        FieldPanel('phone'),
        FieldPanel('email'),
        FieldPanel('is_active'),
    ]


class VitalRecordAdmin(ModelAdmin):
    model = VitalRecord
    menu_label = 'Vital Records'
    menu_icon = 'date'
    list_display = ('record_type', 'member', 'date', 'location')
    list_filter = ('record_type', 'date')
    search_fields = ('member__first_name', 'member__last_name', 'location', 'details')
    panels = [
        FieldPanel('record_type'),
        FieldPanel('date'),
        FieldPanel('member'),
        FieldPanel('details'),
        FieldPanel('location'),
    ]


modeladmin_register(FamilyAdmin)
modeladmin_register(MemberAdmin)
modeladmin_register(VitalRecordAdmin)