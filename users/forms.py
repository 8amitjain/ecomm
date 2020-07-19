from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth import authenticate
from django.db import transaction

from .models import User, Customer, Vendor  # , Address


class AccountAuthenticationForm(forms.ModelForm):
    password = forms.CharField(label='Password', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('username', 'phone_number', 'password')

    def clean(self):
        if self.is_valid():
            username = self.cleaned_data['username']
            phone_number = self.cleaned_data['phone_number']
            password = self.cleaned_data['password']
            if not authenticate(username=username, phone_number=phone_number, password=password):
                raise forms.ValidationError("Invalid login")


class CustomerRegistrationForm(UserCreationForm):
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)
    phone_number = forms.IntegerField(required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'first_name', 'last_name', 'phone_number', 'password1', 'password2')

    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        user.is_customer = True
        user.username = self.cleaned_data.get('username')
        user.first_name = self.cleaned_data.get('first_name')
        user.last_name = self.cleaned_data.get('last_name')
        user.phone_number = self.cleaned_data.get('phone_number')
        user.email = user.username
        user.is_active = False
        user.save()
        customer = Customer.objects.create(user=user)
        customer.phone_number = user.phone_number
        customer.customer_ref_number = f"VRN-{100000+int(customer.user_id)}"
        customer.save()

        # address = Address.objects.create(user=user)
        # address.phone_number = user.phone_number
        # address.save()
        return user


class VendorRegistrationForm(UserCreationForm):
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)
    phone_number = forms.IntegerField(required=True)

    # shop_name = forms.CharField(required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'first_name', 'last_name', 'phone_number', 'password1', 'password2')

    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        user.is_vendor = True
        user.username = self.cleaned_data.get('username')
        user.first_name = self.cleaned_data.get('first_name')
        user.last_name = self.cleaned_data.get('last_name')
        user.phone_number = self.cleaned_data.get('phone_number')
        user.email = user.username
        user.is_active = False
        user.save()
        vendor = Vendor.objects.create(user=user)
        vendor.phone_number = user.phone_number
        vendor.vendor_ref_number = f"VRN-{100000+int(vendor.user_id)}"
        vendor.save()

        # address = Address.objects.create(user=user)
        # address.phone_number = user.phone_number
        # address.save()
        return user


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'phone_number', 'date_of_birth')

    def clean_username(self):
        username = self.cleaned_data['username']
        try:
            username = User.objects.exclude(pk=self.instance.pk).get(username=username)
        except User.DoesNotExist:
            return username
        raise forms.ValidationError('Email "%s" is already in use.' % username)

    @transaction.atomic
    def save(self):
        user = super().save()
        try:
            customer = Customer.objects.get(user=user)
            customer.phone_number = self.cleaned_data.get('phone_number')
            customer.save()
        except:
            vendor = Vendor.objects.get(user=user)
            vendor.phone_number = self.cleaned_data.get('phone_number')
            vendor.save()
        return user

    # def clean_email(self):
    #     email = self.cleaned_data['email']
    #     try:
    #         email = User.objects.exclude(pk=self.instance.pk).get(email=email)
    #     except User.DoesNotExist:
    #         return email
    #     raise forms.ValidationError('Email "%s" is already in use.' % email)


'''if import form UserChangeForm then user fields are working but also getting password reset form'''


class CustomerUpdateForm(forms.ModelForm):
    pin_code = forms.IntegerField(required=True)

    class Meta:
        model = Customer
        fields = ('pin_code',)

    @transaction.atomic
    def save(self):
        user = super().save()
        customer = Customer.objects.get(user=user)
        customer.pin_code = self.cleaned_data.get('pin_code')
        customer.save()
        return user


class VendorUpdateForm(forms.ModelForm):
    pin_code = forms.IntegerField(required=True)

    class Meta:
        model = Vendor
        fields = ('pin_code',)

    @transaction.atomic
    def save(self):
        user = super().save()
        vendor = Vendor.objects.get(user=user)
        vendor.pin_code = self.cleaned_data.get('pin_code')
        vendor.save()
        return user


# class AddressForm(forms.ModelForm):
#     b_street_address_line_2 = forms.CharField(max_length=100, required=False)
#     s_street_address_line_2 = forms.CharField(max_length=100, required=False)
#
#     class Meta:
#         model = Address
#         fields = ('b_street_address', 'b_street_address_line_2', 'b_city',  # 'b_phone_number', 'b_postal_code',
#                   's_street_address', 's_street_address_line_2', 's_city', 's_phone_number', 's_postal_code',
#                   'shipping_is_billing', 'default')
#
#         @transaction.atomic
#         def save(self):
#             user = super().save()
#             address = Address.objects.get(user=user)
#             address.user_id = user.id
#             address.b_street_address = self.cleaned_data.get('b_street_address')
#             address.b_street_address_line_2 = self.cleaned_data.get('b_street_address_line_2')
#             address.b_city = self.cleaned_data.get('b_city')
#             address.b_phone_number = user.phone_number
#             address.b_postal_code = user.postal_code
#             address.default = self.cleaned_data.get('default')
#             address.shipping_is_billing = self.cleaned_data.get('shipping_is_billing')
#
#             if address.shipping_is_billing:
#                 address.s_street_address = self.cleaned_data.get('b_street_address')
#                 address.s_street_address_line_2 = self.cleaned_data.get('b_street_address_line_2')
#                 address.s_city = self.cleaned_data.get('b_city')
#                 address.s_phone_number = self.cleaned_data.get('phone_number')
#                 address.s_postal_code = self.cleaned_data.get('postal_code')
#             else:
#                 address.s_street_address = self.cleaned_data.get('s_street_address')
#                 address.s_street_address_line_2 = self.cleaned_data.get('s_street_address_line_2')
#                 address.s_city = self.cleaned_data.get('s_city')
#                 address.s_phone_number = self.cleaned_data.get('s_phone_number')
#                 address.s_postal_code = self.cleaned_data.get('s_postal_code')
#
#             address.save()
#             return user


















