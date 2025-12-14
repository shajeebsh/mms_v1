from wagtail.admin.panels import FieldPanel
from wagtail_modeladmin.options import ModelAdmin, modeladmin_register

from .models import Family, Member, MembershipDues, Payment, VitalRecord


class FamilyAdmin(ModelAdmin):
    model = Family
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
    menu_label = "Members"
    menu_icon = "user"
    add_to_admin_menu = False  # Will be included in grouped menu
    list_display = ("full_name", "family", "date_of_birth", "gender", "is_active")
    list_filter = ("gender", "is_active", "family")
    search_fields = ("first_name", "last_name", "email", "phone")
    panels = [
        FieldPanel("first_name"),
        FieldPanel("last_name"),
        FieldPanel("date_of_birth"),
        FieldPanel("gender"),
        FieldPanel("family"),
        FieldPanel("phone"),
        FieldPanel("email"),
        FieldPanel("is_active"),
    ]


class MembershipDuesAdmin(ModelAdmin):
    model = MembershipDues
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


modeladmin_register(FamilyAdmin)
modeladmin_register(MemberAdmin)
modeladmin_register(MembershipDuesAdmin)
modeladmin_register(PaymentAdmin)
modeladmin_register(VitalRecordAdmin)
