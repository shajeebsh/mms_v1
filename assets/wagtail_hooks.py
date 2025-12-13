from wagtail.admin.panels import FieldPanel
from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register

from .models import Shop, PropertyUnit


class ShopAdmin(ModelAdmin):
    model = Shop
    menu_label = 'Shops'
    menu_icon = 'shop'
    add_to_admin_menu = False  # Will be included in grouped menu
    list_display = ('name', 'shop_type', 'owner_name', 'monthly_rent', 'is_active')
    list_filter = ('shop_type', 'is_active')
    search_fields = ('name', 'owner_name', 'location')
    panels = [
        FieldPanel('name'),
        FieldPanel('shop_type'),
        FieldPanel('owner_name'),
        FieldPanel('contact_info'),
        FieldPanel('location'),
        FieldPanel('monthly_rent'),
        FieldPanel('lease_start'),
        FieldPanel('lease_end'),
        FieldPanel('is_active'),
    ]


class PropertyUnitAdmin(ModelAdmin):
    model = PropertyUnit
    menu_label = 'Property Units'
    menu_icon = 'home'
    add_to_admin_menu = False  # Will be included in grouped menu
    list_display = ('name', 'unit_type', 'tenant_name', 'monthly_rent', 'is_occupied', 'is_active')
    list_filter = ('unit_type', 'is_occupied', 'is_active')
    search_fields = ('name', 'tenant_name', 'address')
    panels = [
        FieldPanel('name'),
        FieldPanel('unit_type'),
        FieldPanel('address'),
        FieldPanel('size_sqm'),
        FieldPanel('monthly_rent'),
        FieldPanel('tenant_name'),
        FieldPanel('tenant_contact'),
        FieldPanel('lease_start'),
        FieldPanel('lease_end'),
        FieldPanel('is_occupied'),
        FieldPanel('is_active'),
    ]


modeladmin_register(ShopAdmin)
modeladmin_register(PropertyUnitAdmin)