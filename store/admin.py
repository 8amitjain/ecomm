from django.contrib import admin
from django.db import models
from mapwidgets.widgets import GooglePointFieldWidget
from django.contrib.gis.db import models as geo_model

from .models import OrderItem, FavoriteItem, CompareItem, Order, Payment, Coupon, Slide, UserProfile, Addresss,\
                    Reviews, CustomerLocation, MiniOrder, Return, CouponCustomer, PrescriptionUpload


class CustomerLocationAdmin(admin.ModelAdmin):
    formfield_overrides = {
        geo_model.PointField: {"widget": GooglePointFieldWidget}
    }


def make_refund_accepted(modeladmin, request, queryset):
    queryset.update(refund_requested=False, refund_granted=True)


make_refund_accepted.short_description = 'Update orders to refund granted'


class OrderAdmin(admin.ModelAdmin):
    list_display = ['user',
                    'ordered',
                    'received',
                    'shipping_address',
                    'billing_address',
                    'payment',
                    # 'coupon'
                    ]
    list_display_links = [
        'user',
        'shipping_address',
        'billing_address',
        'payment',
        # 'coupon'
    ]
    list_filter = ['user',
                   'ordered',
                   'received',
                   ]
    search_fields = [
        'user__username',
        'ref_code'
    ]
    # formfield_overrides = {
    #     models.ManyToManyField: {'widget': CheckboxSelectMultiple},
    # }
    actions = [make_refund_accepted]


def copy_items(modeladmin, request, queryset):
    for objects in queryset:
        objects.id = None
        objects.save()


copy_items.short_description = 'Copy Items'


admin.site.register(Slide)
admin.site.register(UserProfile)
admin.site.register(OrderItem)
admin.site.register(FavoriteItem)
admin.site.register(CompareItem)
admin.site.register(Order, OrderAdmin)
admin.site.register(Payment)
admin.site.register(Coupon)
admin.site.register(Addresss)
admin.site.register(Reviews)
admin.site.register(CustomerLocation, CustomerLocationAdmin)
admin.site.register(MiniOrder)
admin.site.register(Return)
admin.site.register(CouponCustomer)
admin.site.register(PrescriptionUpload)

# admin.site.register(Address, AddressAdmin)

