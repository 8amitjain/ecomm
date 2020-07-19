from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Customer, Vendor  # , Address


class UserAdmin(UserAdmin):
    list_display = ('username', 'first_name', 'date_joined', 'last_login', 'is_superuser', 'is_staff')
    search_fields = ('username', 'first_name')
    readonly_fields = ('date_joined', 'last_login')

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


class AddressAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'street_address',
        'apartment_address',
        'country',
        'postal_code',
        'address_type',
        'default'
    ]
    list_filter = ['default', 'address_type', 'country']
    search_fields = ['user', 'street_address', 'apartment_address', 'postal_code']


admin.site.register(User, UserAdmin)
# admin.site.register(Address, )
admin.site.register(Customer)
admin.site.register(Vendor)
