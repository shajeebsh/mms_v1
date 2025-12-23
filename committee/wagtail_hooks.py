from wagtail import hooks
from wagtail.admin.menu import MenuItem
from wagtail.admin.search import SearchArea
from wagtail_modeladmin.options import ModelAdmin, modeladmin_register
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from .models import (
    CommitteeType, Committee, CommitteeMember, Meeting, MeetingAttendee,
    MeetingAttachment, Trustee, TrusteeMeeting, TrusteeMeetingAttendee,
    TrusteeMeetingAttachment
)


from home.permission_helpers import ACLPermissionHelper

class CommitteeTypeAdmin(ModelAdmin):
    model = CommitteeType
    permission_helper_class = ACLPermissionHelper
    menu_label = 'Committee Types'
    menu_icon = 'group'
    add_to_admin_menu = False
    list_display = ('name', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')


class CommitteeAdmin(ModelAdmin):
    model = Committee
    permission_helper_class = ACLPermissionHelper
    menu_label = 'Committees'
    menu_icon = 'group'
    add_to_admin_menu = False
    list_display = ('name', 'committee_type', 'chairperson', 'is_active')
    list_filter = ('committee_type', 'is_active')
    search_fields = ('name', 'description')
    raw_id_fields = ('chairperson', 'secretary')


class CommitteeMemberAdmin(ModelAdmin):
    model = CommitteeMember
    permission_helper_class = ACLPermissionHelper
    menu_label = 'Committee Members'
    menu_icon = 'user'
    add_to_admin_menu = False
    list_display = ('committee', 'member', 'role', 'joined_date', 'is_active')
    list_filter = ('committee', 'is_active', 'joined_date')
    search_fields = ('member__first_name', 'member__last_name', 'committee__name')
    raw_id_fields = ('committee', 'member')


class MeetingAdmin(ModelAdmin):
    model = Meeting
    permission_helper_class = ACLPermissionHelper
    menu_label = 'Committee Meetings'
    menu_icon = 'date'
    add_to_admin_menu = False
    list_display = ('committee', 'title', 'scheduled_date', 'status')
    list_filter = ('committee', 'status', 'scheduled_date', 'meeting_type')
    search_fields = ('title', 'committee__name')
    raw_id_fields = ('committee', 'chairperson', 'minute_taker', 'created_by')


class MeetingAttendeeAdmin(ModelAdmin):
    model = MeetingAttendee
    permission_helper_class = ACLPermissionHelper
    menu_label = 'Meeting Attendees'
    menu_icon = 'tick'
    add_to_admin_menu = False
    list_display = ('meeting', 'member', 'attended')
    list_filter = ('attended', 'meeting__scheduled_date')
    search_fields = ('member__first_name', 'member__last_name', 'meeting__title')
    raw_id_fields = ('meeting', 'member')


class MeetingAttachmentAdmin(ModelAdmin):
    model = MeetingAttachment
    permission_helper_class = ACLPermissionHelper
    menu_label = 'Meeting Attachments'
    menu_icon = 'doc-full'
    add_to_admin_menu = False
    list_display = ('meeting', 'title', 'attachment_type', 'uploaded_by', 'uploaded_at')
    list_filter = ('attachment_type', 'uploaded_at')
    search_fields = ('title', 'meeting__title')
    raw_id_fields = ('meeting', 'uploaded_by')


class TrusteeAdmin(ModelAdmin):
    model = Trustee
    permission_helper_class = ACLPermissionHelper
    menu_label = 'Trustees'
    menu_icon = 'user'
    add_to_admin_menu = False
    list_display = ('member', 'position', 'appointed_date', 'is_active')
    list_filter = ('position', 'is_active', 'appointed_date')
    search_fields = ('member__first_name', 'member__last_name')
    raw_id_fields = ('member',)


class TrusteeMeetingAdmin(ModelAdmin):
    model = TrusteeMeeting
    permission_helper_class = ACLPermissionHelper
    menu_label = 'Trustee Meetings'
    menu_icon = 'date'
    add_to_admin_menu = False
    list_display = ('title', 'scheduled_date', 'status')
    list_filter = ('status', 'scheduled_date')
    search_fields = ('title', 'description')
    raw_id_fields = ('chairperson', 'minute_taker', 'created_by')


class TrusteeMeetingAttendeeAdmin(ModelAdmin):
    model = TrusteeMeetingAttendee
    permission_helper_class = ACLPermissionHelper
    menu_label = 'Trustee Meeting Attendees'
    menu_icon = 'tick'
    add_to_admin_menu = False
    list_display = ('trustee_meeting', 'trustee', 'attended')
    list_filter = ('attended', 'trustee_meeting__scheduled_date')
    search_fields = ('trustee__member__first_name', 'trustee__member__last_name')
    raw_id_fields = ('trustee_meeting', 'trustee')


class TrusteeMeetingAttachmentAdmin(ModelAdmin):
    model = TrusteeMeetingAttachment
    permission_helper_class = ACLPermissionHelper
    menu_label = 'Trustee Meeting Attachments'
    menu_icon = 'doc-full'
    add_to_admin_menu = False
    list_display = ('trustee_meeting', 'title', 'attachment_type', 'uploaded_by', 'uploaded_at')
    list_filter = ('attachment_type', 'uploaded_at')
    search_fields = ('title', 'trustee_meeting__title')
    raw_id_fields = ('trustee_meeting', 'uploaded_by')


# Register all ModelAdmin classes
modeladmin_register(CommitteeTypeAdmin)
modeladmin_register(CommitteeAdmin)
modeladmin_register(CommitteeMemberAdmin)
modeladmin_register(MeetingAdmin)
modeladmin_register(MeetingAttendeeAdmin)
modeladmin_register(MeetingAttachmentAdmin)
modeladmin_register(TrusteeAdmin)
modeladmin_register(TrusteeMeetingAdmin)
modeladmin_register(TrusteeMeetingAttendeeAdmin)
modeladmin_register(TrusteeMeetingAttachmentAdmin)





@hooks.register('register_admin_search_area')
def register_committee_search_area():
    return SearchArea(
        _('Committee & Minutes'),
        reverse('wagtailadmin_home'),
        icon_name='group',
        order=1100
    )