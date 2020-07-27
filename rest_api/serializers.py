from rest_framework import serializers

from users.models import User, Customer
from vendors.models import Vendor, VendorAddress


# User Serializer
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'phone_number')


# Customer Register Serializer
class CustomerRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'phone_number', 'first_name', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            validated_data['username'], validated_data['password'],
            phone_number=validated_data['phone_number'],
            email=validated_data['username'],
            first_name=validated_data['first_name'],
            is_customer=True,
            is_active=True,
            is_verified=False,
        )
        customer = Customer.objects.create(user=user)
        customer.phone_number = user.phone_number
        customer.customer_ref_number = f"VRN-{100000 + int(customer.user_id)}"
        customer.save()
        return user


# Vendor Register Serializer
class VendorRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'phone_number', 'first_name', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            validated_data['username'], validated_data['password'],
            phone_number=validated_data['phone_number'],
            email=validated_data['username'],
            first_name=validated_data['first_name'],
            is_vendor=True
            # is_active=False
        )
        address = VendorAddress.objects.create(user=user)
        address.save()
        vendor = Vendor.objects.create(user=user)
        vendor.address = address
        vendor.phone_number = user.phone_number
        vendor.vendor_ref_number = f"VRN-{100000 + int(vendor.user_id)}"
        vendor.save()
        return user


class ChangePasswordSerializer(serializers.Serializer):
    model = User

    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
