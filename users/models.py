from __future__ import unicode_literals
from django.db import models
from django.core.mail import send_mail
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.core.validators import MaxValueValidator

from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    username = models.EmailField(_('email address'), unique=True, help_text='Provide an email for Registration')
    email = models.EmailField(_('user address'), blank=True)
    first_name = models.CharField(_('first name'), max_length=30)
    last_name = models.CharField(_('last name'), max_length=30, blank=True)
    date_joined = models.DateTimeField(_('date joined'), auto_now_add=True)
    is_active = models.BooleanField(_('active'), default=True)
    is_staff = models.BooleanField(_('staff'), default=False)

    is_customer = models.BooleanField(_('customer'), default=False)
    is_vendor = models.BooleanField(_('vendor'), default=False)
    phone_number = models.IntegerField(blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    # profile_pic = models.ImageField(default='default.jpg', upload_to='profile_pics', blank=True)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    EMAIL_FIELD = 'username'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def get_full_name(self):
        '''
        Returns the first_name plus the last_name, with a space in between.
        '''
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        '''
        Returns the short name for the user.
        '''
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        '''
        Sends an email to this User.
        '''
        send_mail(subject, message, from_email, [self.username], **kwargs)


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    phone_number = models.IntegerField(null=True)
    pin_code = models.IntegerField(null=True)
    customer_ref_number = models.CharField(unique=True, default='CRN-100000', max_length=15)

    def __str__(self):
        return self.user.username


class Vendor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    # item = models.ForeignKey(Item, on_delete=models.CASCADE)

    # shop_name = models.CharField()
    phone_number = models.IntegerField(null=True)
    pin_code = models.IntegerField(null=True)
    vendor_ref_number = models.CharField(unique=True, default='VRN-100000', max_length=15)

    def __str__(self):
        return self.user.username




# class Address(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
#     b_street_address = models.CharField(max_length=100, null=True)
#     b_street_address_line_2 = models.CharField(max_length=100, null=True)
#     b_city = models.CharField(max_length=100, null=True)
#     b_phone_number = models.IntegerField(validators=[MaxValueValidator(9999999999)], null=True)
#     b_postal_code = models.IntegerField(validators=[MaxValueValidator(9999999999)], null=True)
#
#     s_street_address = models.CharField(max_length=100, null=True)
#     s_street_address_line_2 = models.CharField(max_length=100, null=True)
#     s_city = models.CharField(max_length=100, null=True)
#     s_phone_number = models.IntegerField(validators=[MaxValueValidator(9999999999)], null=True)
#     s_postal_code = models.IntegerField(validators=[MaxValueValidator(9999999999)], null=True)
#
#     shipping_is_billing = models.BooleanField(default=True)
#     default = models.BooleanField(default=False)
#
#     def __str__(self):
#         return self.user.username
#
#     class Meta:
#         verbose_name_plural = 'Addresses'



