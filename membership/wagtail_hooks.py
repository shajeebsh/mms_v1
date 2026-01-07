import re

from django import forms
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.utils.html import format_html
from wagtail.admin.panels import FieldPanel, FieldRowPanel, MultiFieldPanel
from wagtail_modeladmin.helpers import ButtonHelper
from wagtail_modeladmin.options import ModelAdmin, modeladmin_register

from .models import (
    City,
    Country,
    HouseRegistration,
    Member,
    MembershipDues,
    Payment,
    PostalCode,
    State,
    Taluk,
    VitalRecord,
    Ward,
)


class MemberButtonHelper(ButtonHelper):
    def get_buttons_for_obj(
        self, obj, exclude=None, classnames_add=None, classnames_exclude=None
    ):
        buttons = super().get_buttons_for_obj(
            obj, exclude, classnames_add, classnames_exclude
        )
        return buttons

    def add_button(self, classnames_add=None, classnames_exclude=None):
        button = super().add_button(classnames_add, classnames_exclude)
        # We can add more buttons here if needed
        return button

    def get_header_buttons_for_index(
        self, exclude=None, classnames_add=None, classnames_exclude=None
    ):
        buttons = []

        # Add Questionnaire Button - using same structure as add_button
        questionnaire_button = {
            "url": reverse("membership:preview_questionnaire"),
            "label": "Questionnaire Form",
            "classname": "button",
            "title": "Preview/Print Membership Questionnaire",
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


class HouseRegistrationForm(forms.ModelForm):
    class Meta:
        model = HouseRegistration
        fields = [
            "house_name",
            "house_number",
            "ward",
            "taluk",
            "city",
            "state",
            "country",
            "postal_code",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make all fields required
        for field_name in self.fields:
            self.fields[field_name].required = True

    def clean_house_name(self):
        value = (self.cleaned_data.get("house_name") or "").strip()
        if not value:
            raise ValidationError("House name is required.")
        return value

    def clean_house_number(self):
        value = (self.cleaned_data.get("house_number") or "").strip()
        if not value:
            raise ValidationError("House number is required.")
        return value

    def clean_ward(self):
        value = self.cleaned_data.get("ward")
        if not value:
            raise ValidationError("Ward is required.")
        return value

    def clean_taluk(self):
        value = self.cleaned_data.get("taluk")
        if not value:
            raise ValidationError("Taluk is required.")
        return value

    def clean_city(self):
        value = self.cleaned_data.get("city")
        if not value:
            raise ValidationError("City is required.")
        return value

    def clean_state(self):
        value = self.cleaned_data.get("state")
        if not value:
            raise ValidationError("State is required.")
        return value

    def clean_country(self):
        value = self.cleaned_data.get("country")
        if not value:
            raise ValidationError("Country is required.")
        return value

    def clean_postal_code(self):
        value = self.cleaned_data.get("postal_code")
        if not value:
            raise ValidationError("Postal code is required.")
        return value


class HouseRegistrationAdmin(ModelAdmin):
    model = HouseRegistration
    permission_helper_class = ACLPermissionHelper
    menu_label = "House Registrations"
    menu_icon = "home"
    add_to_admin_menu = False  # Will be included in grouped menu
    list_display = ("house_name", "house_number", "ward", "city", "state", "country")
    search_fields = ("house_name", "house_number")

    def get_form_class(self):
        return HouseRegistrationForm

    panels = [
        MultiFieldPanel(
            [
                FieldRowPanel(
                    [
                        FieldPanel("house_name", classname="col6"),
                        FieldPanel("house_number", classname="col6"),
                    ],
                    classname="compact-row",
                ),
            ],
            heading="House Details",
            classname="compact-panel",
        ),
        MultiFieldPanel(
            [
                FieldRowPanel(
                    [
                        FieldPanel("ward", classname="col6"),
                        FieldPanel("taluk", classname="col6"),
                    ],
                    classname="compact-row",
                ),
                FieldRowPanel(
                    [
                        FieldPanel("city", classname="col6"),
                        FieldPanel("state", classname="col6"),
                    ],
                    classname="compact-row",
                ),
                FieldRowPanel(
                    [
                        FieldPanel("country", classname="col6"),
                        FieldPanel("postal_code", classname="col6"),
                    ],
                    classname="compact-row",
                ),
            ],
            heading="Address",
            classname="compact-panel",
        ),
    ]


class MemberAdmin(ModelAdmin):
    model = Member
    permission_helper_class = ACLPermissionHelper
    button_helper_class = MemberButtonHelper
    menu_label = "Members"
    menu_icon = "user"
    add_to_admin_menu = False  # Will be included in grouped menu
    list_display = (
        "full_name",
        "is_head_of_family",
        "date_of_birth",
        "gender",
        "is_active",
        "print_card_link",
    )
    list_filter = ("gender", "is_active", "is_head_of_family", "house")
    search_fields = ("first_name", "last_name", "email", "phone")

    class MemberAdminForm(forms.ModelForm):
        _phone_re = re.compile(r"^\+?[0-9]{7,20}$")

        class Meta:
            model = Member
            fields = "__all__"

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            if "gender" in self.fields:
                self.fields["gender"].required = True
            if "house" in self.fields:
                self.fields["house"].required = True
            if "whatsapp_number" in self.fields:
                self.fields["whatsapp_number"].required = True
            if "phone" in self.fields:
                self.fields["phone"].required = True

        def clean_phone(self):
            value = (self.cleaned_data.get("phone") or "").strip()
            if not value:
                raise ValidationError("Phone number is required.")
            if not self._phone_re.match(value):
                raise ValidationError(
                    "Enter a valid phone number (digits only, optional leading +)."
                )
            return value

        def clean_whatsapp_number(self):
            value = (self.cleaned_data.get("whatsapp_number") or "").strip()
            if not value:
                raise ValidationError("WhatsApp number is required.")
            if not self._phone_re.match(value):
                raise ValidationError(
                    "Enter a valid WhatsApp number (digits only, optional leading +)."
                )
            return value

        def clean_gender(self):
            value = (self.cleaned_data.get("gender") or "").strip()
            if not value:
                raise ValidationError("Gender is required.")
            return value

        def clean_house(self):
            value = self.cleaned_data.get("house")
            if value is None:
                raise ValidationError("House is required.")
            return value

    base_form_class = MemberAdminForm

    panels = [
        MultiFieldPanel(
            [
                FieldRowPanel(
                    [
                        FieldPanel("first_name", classname="col4"),
                        FieldPanel("last_name", classname="col4"),
                        FieldPanel("date_of_birth", classname="col4"),
                    ]
                ),
                FieldRowPanel(
                    [
                        FieldPanel("gender", classname="col4"),
                        FieldPanel("blood_group", classname="col4"),
                        FieldPanel("marital_status", classname="col4"),
                    ]
                ),
                FieldRowPanel(
                    [
                        FieldPanel("is_head_of_family", classname="col4"),
                        FieldPanel("is_active", classname="col4"),
                        FieldPanel("house", classname="col4"),
                    ]
                ),
            ],
            heading="Personal Information",
        ),
        MultiFieldPanel(
            [
                FieldRowPanel(
                    [
                        FieldPanel("phone", classname="col4"),
                        FieldPanel("whatsapp_number", classname="col4"),
                        FieldPanel("email", classname="col4"),
                    ]
                ),
                FieldRowPanel(
                    [
                        FieldPanel("aadhaar_no", classname="col4"),
                        FieldPanel("photo", classname="col8"),
                    ]
                ),
            ],
            heading="Contact & Identification",
        ),
        MultiFieldPanel(
            [
                FieldRowPanel(
                    [
                        FieldPanel("address", classname="col12"),
                    ]
                ),
            ],
            heading="House",
        ),
    ]

    def print_card_link(self, obj):
        from django.urls import reverse

        url = reverse("membership:preview_membership_card", args=[obj.id])
        return format_html(
            '<a class="button button-small" href="{}" target="_blank">Preview ID</a>',
            url,
        )

    print_card_link.short_description = "Actions"


class MembershipDuesAdmin(ModelAdmin):
    model = MembershipDues
    permission_helper_class = ACLPermissionHelper
    menu_label = "Membership Dues"
    menu_icon = "money"
    add_to_admin_menu = False  # Will be included in grouped menu
    list_display = (
        "house",
        "year",
        "month",
        "amount_due",
        "is_paid",
        "due_date",
        "is_overdue",
    )
    list_filter = ("year", "month", "is_paid", "due_date")
    search_fields = ("house__house_name", "house__house_number")
    list_editable = ("is_paid",)
    panels = [
        FieldPanel("house"),
        FieldPanel("year"),
        FieldPanel("month"),
        FieldPanel("amount_due"),
        FieldPanel("is_paid"),
        FieldPanel("due_date"),
    ]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("house")


class PaymentAdmin(ModelAdmin):
    model = Payment
    permission_helper_class = ACLPermissionHelper
    menu_label = "Payments"
    menu_icon = "credit-card"
    add_to_admin_menu = False  # Will be included in grouped menu
    list_display = (
        "receipt_number",
        "house",
        "amount",
        "payment_method",
        "payment_date",
        "total_dues_covered",
    )
    list_filter = ("payment_method", "payment_date")
    search_fields = (
        "receipt_number",
        "house__house_name",
        "house__house_number",
        "notes",
    )
    panels = [
        FieldPanel("house"),
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
            .select_related("house")
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
modeladmin_register(HouseRegistrationAdmin)
modeladmin_register(MemberAdmin)
modeladmin_register(MembershipDuesAdmin)
modeladmin_register(PaymentAdmin)
modeladmin_register(VitalRecordAdmin)
