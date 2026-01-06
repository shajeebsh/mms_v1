from django.utils.html import format_html
from wagtail.admin.panels import FieldPanel, FieldRowPanel, MultiFieldPanel
from wagtail_modeladmin.options import ModelAdmin, modeladmin_register

from .models import Family, Member, MembershipDues, Payment, VitalRecord, Ward, Taluk, City, State, Country, PostalCode


from wagtail_modeladmin.helpers import ButtonHelper
from django.urls import reverse


class MemberButtonHelper(ButtonHelper):
    def get_buttons_for_obj(self, obj, exclude=None, classnames_add=None, classnames_exclude=None):
        buttons = super().get_buttons_for_obj(obj, exclude, classnames_add, classnames_exclude)
        return buttons

    def add_button(self, classnames_add=None, classnames_exclude=None):
        button = super().add_button(classnames_add, classnames_exclude)
        # We can add more buttons here if needed
        return button

    def get_header_buttons_for_index(self, exclude=None, classnames_add=None, classnames_exclude=None):
        buttons = []
        
        # Add Questionnaire Button - using same structure as add_button
        questionnaire_button = {
            'url': reverse('membership:preview_questionnaire'),
            'label': 'Questionnaire Form',
            'classname': 'button',
            'title': 'Preview/Print Membership Questionnaire',
        }
        buttons.append(questionnaire_button)
        return buttons


from home.permission_helpers import ACLPermissionHelper

class WardAdmin(ModelAdmin):
    model = Ward
    permission_helper_class = ACLPermissionHelper
    menu_label = "Wards"
    menu_icon = "tag"
    add_to_admin_menu = False  # Will be included in grouped menu
    list_display = ("name", "created_at")
    search_fields = ("name",)
    panels = [
        FieldPanel("name"),
        FieldPanel("created_at"),
    ]

class TalukAdmin(ModelAdmin):
    model = Taluk
    permission_helper_class = ACLPermissionHelper
    menu_label = "Taluks"
    menu_icon = "tag"
    add_to_admin_menu = False  # Will be included in grouped menu
    list_display = ("name", "created_at")
    search_fields = ("name",)
    panels = [
        FieldPanel("name"),
        FieldPanel("created_at"),
    ]

class CityAdmin(ModelAdmin):
    model = City
    permission_helper_class = ACLPermissionHelper
    menu_label = "Cities"
    menu_icon = "tag"
    add_to_admin_menu = False  # Will be included in grouped menu
    list_display = ("name", "created_at")
    search_fields = ("name",)
    panels = [
        FieldPanel("name"),
        FieldPanel("created_at"),
    ]

class StateAdmin(ModelAdmin):
    model = State
    permission_helper_class = ACLPermissionHelper
    menu_label = "States"
    menu_icon = "tag"
    add_to_admin_menu = False  # Will be included in grouped menu
    list_display = ("name", "created_at")
    search_fields = ("name",)
    panels = [
        FieldPanel("name"),
        FieldPanel("created_at"),
    ]

class CountryAdmin(ModelAdmin):
    model = Country
    permission_helper_class = ACLPermissionHelper
    menu_label = "Countries"
    menu_icon = "tag"
    add_to_admin_menu = False  # Will be included in grouped menu
    list_display = ("name", "created_at")
    search_fields = ("name",)
    panels = [
        FieldPanel("name"),
        FieldPanel("created_at"),
    ]

class PostalCodeAdmin(ModelAdmin):
    model = PostalCode
    permission_helper_class = ACLPermissionHelper
    menu_label = "Postal Codes"
    menu_icon = "tag"
    add_to_admin_menu = False  # Will be included in grouped menu
    list_display = ("code", "created_at")
    search_fields = ("code",)
    panels = [
        FieldPanel("code"),
        FieldPanel("created_at"),
    ]

class FamilyAdmin(ModelAdmin):
    model = Family
    permission_helper_class = ACLPermissionHelper
    menu_label = "Families"
    menu_icon = "group"
    add_to_admin_menu = False  # Will be included in grouped menu
    list_display = ("name", "phone", "email", "created_at")
    search_fields = ("name", "phone", "email")
    panels = [
        FieldPanel("name"),
        FieldPanel("address"),
        FieldPanel("phone"),
        FieldPanel("email"),
    ]


class MemberAdmin(ModelAdmin):
    model = Member
    permission_helper_class = ACLPermissionHelper
    button_helper_class = MemberButtonHelper
    menu_label = "Members"
    menu_icon = "user"
    add_to_admin_menu = False  # Will be included in grouped menu
    list_display = ("full_name", "is_head_of_family", "date_of_birth", "gender", "is_active", "print_card_link")
    list_filter = ("gender", "is_active", "is_head_of_family", "city", "state")
    search_fields = ("first_name", "last_name", "email", "phone")
    panels = [
        MultiFieldPanel([
            FieldRowPanel([
                FieldPanel("first_name", classname="col4"),
                FieldPanel("last_name", classname="col4"),
                FieldPanel("date_of_birth", classname="col4"),
            ]),
            FieldRowPanel([
                FieldPanel("gender", classname="col4"),
                FieldPanel("blood_group", classname="col4"),
                FieldPanel("marital_status", classname="col4"),
            ]),
            FieldRowPanel([
                FieldPanel("is_head_of_family", classname="col4"),
                FieldPanel("is_active", classname="col4"),
            ]),
        ], heading="Personal Information"),
        
        MultiFieldPanel([
            FieldRowPanel([
                FieldPanel("phone", classname="col4"),
                FieldPanel("whatsapp_number", classname="col4"),
                FieldPanel("email", classname="col4"),
            ]),
            FieldRowPanel([
                FieldPanel("aadhaar_no", classname="col4"),
                FieldPanel("photo", classname="col8"),
            ]),
        ], heading="Contact & Identification"),
        
        MultiFieldPanel([
            FieldRowPanel([
                FieldPanel("ward_no_dropdown", classname="col4"),
                FieldPanel("address", classname="col8"),
            ]),
            FieldRowPanel([
                FieldPanel("taluk_dropdown", classname="col4"),
                FieldPanel("city_dropdown", classname="col4"),
                FieldPanel("postal_code_dropdown", classname="col4"),
            ]),
            FieldRowPanel([
                FieldPanel("state_dropdown", classname="col6"),
                FieldPanel("country_dropdown", classname="col6"),
            ]),
        ], heading="Location Information"),
    ]

    def print_card_link(self, obj):
        from django.urls import reverse
        url = reverse('membership:preview_membership_card', args=[obj.id])
        return format_html('<a class="button button-small" href="{}" target="_blank">Preview ID</a>', url)
    print_card_link.short_description = 'Actions'


class MembershipDuesAdmin(ModelAdmin):
    model = MembershipDues
    permission_helper_class = ACLPermissionHelper
    menu_label = "Membership Dues"
    menu_icon = "money"
    add_to_admin_menu = False  # Will be included in grouped menu
    list_display = (
        "family",
        "year",
        "month",
        "amount_due",
        "is_paid",
        "due_date",
        "is_overdue",
    )
    list_filter = ("year", "month", "is_paid", "due_date")
    search_fields = ("family__name",)
    list_editable = ("is_paid",)
    panels = [
        FieldPanel("family"),
        FieldPanel("year"),
        FieldPanel("month"),
        FieldPanel("amount_due"),
        FieldPanel("is_paid"),
        FieldPanel("due_date"),
    ]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("family")


class PaymentAdmin(ModelAdmin):
    model = Payment
    permission_helper_class = ACLPermissionHelper
    menu_label = "Payments"
    menu_icon = "credit-card"
    add_to_admin_menu = False  # Will be included in grouped menu
    list_display = (
        "receipt_number",
        "family",
        "amount",
        "payment_method",
        "payment_date",
        "total_dues_covered",
    )
    list_filter = ("payment_method", "payment_date")
    search_fields = ("receipt_number", "family__name", "notes")
    panels = [
        FieldPanel("family"),
        FieldPanel("amount"),
        FieldPanel("payment_method"),
        FieldPanel("payment_date"),
        FieldPanel("membership_dues"),
        FieldPanel("notes"),
    ]

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("family")
            .prefetch_related("membership_dues")
        )


class VitalRecordAdmin(ModelAdmin):
    model = VitalRecord
    permission_helper_class = ACLPermissionHelper
    menu_label = "Vital Records"
    menu_icon = "date"
    add_to_admin_menu = False  # Will be included in grouped menu
    list_display = ("record_type", "member", "date", "location")
    list_filter = ("record_type", "date")
    search_fields = ("member__first_name", "member__last_name", "location", "details")
    panels = [
        FieldPanel("record_type"),
        FieldPanel("date"),
        FieldPanel("member"),
        FieldPanel("details"),
        FieldPanel("location"),
    ]


modeladmin_register(WardAdmin)
modeladmin_register(TalukAdmin)
modeladmin_register(CityAdmin)
modeladmin_register(StateAdmin)
modeladmin_register(CountryAdmin)
modeladmin_register(PostalCodeAdmin)
modeladmin_register(FamilyAdmin)
modeladmin_register(MemberAdmin)
modeladmin_register(MembershipDuesAdmin)
modeladmin_register(PaymentAdmin)
modeladmin_register(VitalRecordAdmin)
