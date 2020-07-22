from django.contrib import admin
from mapwidgets.widgets import GooglePointFieldWidget
from django.contrib.gis.db import models as geo_model

from .models import Item, Category, Brands, Vendor, VendorAddress, VendorLocation, SameItem


def copy_items(modeladmin, request, queryset):
    for objects in queryset:
        objects.id = None
        objects.save()


copy_items.short_description = 'Copy Items'


class ItemAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'category',
    ]
    list_filter = ['title', 'category']
    search_fields = ['title', 'category']
    prepopulated_fields = {"slug": ("title",)}
    actions = [copy_items]


class CategoryAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'is_active'
    ]
    list_filter = ['title', 'is_active']
    search_fields = ['title', 'is_active']
    prepopulated_fields = {"slug": ("title",)}


class VendorLocationAdmin(admin.ModelAdmin):
    formfield_overrides = {
        geo_model.PointField: {"widget": GooglePointFieldWidget}
    }


admin.site.register(Item, ItemAdmin)
admin.site.register(SameItem)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Brands)
admin.site.register(Vendor)
admin.site.register(VendorAddress)
admin.site.register(VendorLocation, VendorLocationAdmin)
