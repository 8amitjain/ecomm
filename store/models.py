from django.db import models
from django.contrib.gis.db import models as geo_models
from django.db.models.signals import post_save
from django.core.validators import MaxValueValidator
from django.utils import timezone
from django.utils.timezone import timedelta

from users.models import User
from vendors.models import Item, Category, Vendor


# Create your models here.
REVIEW_RATING_CHOICES = (
    ('1', 'Terrible'),
    ('2', 'Poor'),
    ('3', 'Average'),
    ('4', 'Very Good'),
    ('5', 'Excellent'),
)


ADDRESS_CHOICES = (
    ('B', 'Billing'),
    ('S', 'Shipping'),
)

ORDER_STATUS = (
    ('Preparing Order', 'Preparing Order'),
    ('Shipping', 'Shipping'),
    ('Picked up from store', 'Picked up from store'),
    ('Out for delivery', 'Out for delivery'),
    ('Delivered', 'Delivered'),
    ('RETURNED', 'RETURNED'),
    ('CANCELED', 'CANCELED')
)


RETURN_STATUS = (
    ('', ''),
    ('Return Denied', 'Return Denied'),
    ('Processing Return Request', 'Processing Return Request'),
    ('Item Picked up', 'Item Picked up '),
    ('Item Received Vendor', 'Item Received Vendor'),
    ('Return Granted', 'Return Granted'),
    ('CANCELED', 'CANCELED')
)

REQUEST_RETURN_TYPE = (
     ('RETURN', 'RETURN'),
     ('Exchange', 'Exchange')
)


RETURN_REASON = (
    ('', ''),
    ('Not as Describe', 'Not as Describe'),
    ('Damaged', 'Damaged'),
    ('Expired', 'Expired'),
    ('Ordered Wrong Item', 'Ordered Wrong Item'),
    ('Received Wrong Item', 'Received Wrong Item'),
    ('Received Wrong Brand Item', 'Received Wrong Brand Item'),  # may be variation
    ('Other', 'Other')
)


REQUEST_CANCEL_TYPE = (
     ('CANCEL', 'CANCEL'),
     ('Exchange', 'Exchange')
)


CANCEL_REASON = (
    ('', ''),
    ('Not Needed', 'Not Needed'),
    ('Ordered Wrong Product', 'Ordered Wrong Product'),
    ('Receiving To Late', 'Receiving To Late'),
    ('Select Different Payment Method', 'Select Different Payment Method'),
    ('Other', 'Other')
)

CANCEL_STATUS = (
    ('', ''),
    ('CANCEL Denied', 'CANCEL Denied'),
    ('Processing Cancel Request', 'Processing Cancel Request'),
    ('Cancel Granted', 'Cancel Granted'),
)


class UserProfile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE)
    stripe_customer_id = models.CharField(max_length=50, blank=True, null=True)
    one_click_purchasing = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username


def userprofile_receiver(sender, instance, created, *args, **kwargs):
    if created:
        userprofile = UserProfile.objects.create(user=instance)


post_save.connect(userprofile_receiver, sender=User)


class CustomerLocation(geo_models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order_ref_number = models.CharField(unique=True, max_length=15, null=True)  # or vendor name here
    location = geo_models.PointField(help_text="Use map widget for point the house location")

    def __str__(self):
        return f"{self.location} point location"

    class Meta:
        verbose_name_plural = 'Customer Locations'


class Addresss(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    location = models.ForeignKey(CustomerLocation, on_delete=models.CASCADE, null=True)

    street_address = models.CharField(max_length=100)
    apartment_address = models.CharField(max_length=100)

    city = models.TextField(default='Jalgaon')
    phone_number = models.BigIntegerField(validators=[MaxValueValidator(9999999999)], blank=True)
    postal_code = models.IntegerField(validators=[MaxValueValidator(9999999999)])

    address_type = models.CharField(max_length=1, choices=ADDRESS_CHOICES)
    default = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user} Address"

    class Meta:
        verbose_name_plural = 'Addresses'


class CustomerAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    location = models.ForeignKey(CustomerLocation, on_delete=models.CASCADE, null=True)

    billing_street_address = models.CharField(max_length=100, null=True)
    billing_street_address_line_2 = models.CharField(max_length=100, null=True)
    billing_city = models.CharField(max_length=100, null=True)
    billing_phone_number = models.BigIntegerField(validators=[MaxValueValidator(9999999999)], null=True)
    billing_postal_code = models.IntegerField(validators=[MaxValueValidator(9999999999)], null=True)

    shipping_street_address = models.CharField(max_length=100, null=True)
    shipping_street_address_line_2 = models.CharField(max_length=100, null=True)
    shipping_city = models.CharField(max_length=100, null=True)
    shipping_phone_number = models.BigIntegerField(validators=[MaxValueValidator(9999999999)], null=True)
    shipping_postal_code = models.IntegerField(validators=[MaxValueValidator(9999999999)], null=True)

    shipping_is_billing = models.BooleanField(default=True)
    default = models.BooleanField(default=True)

    def __str__(self):
        try:
            return f"{self.user.first_name}_Address"
        except:
            return f"{self.user}_Address"


class Slide(models.Model):
    caption1 = models.CharField(max_length=100)
    caption2 = models.CharField(max_length=100)
    link = models.CharField(max_length=100)
    image = models.ImageField(help_text="Size: 1920x570")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return "{} - {}".format(self.caption1, self.caption2)


class OrderItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    ordered = models.BooleanField(default=False)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} of {self.item.title}"

    def get_total_item_price(self):
        return self.quantity * self.item.price

    def get_total_discount_item_price(self):
        return self.quantity * self.item.discount_price

    def get_amount_saved(self):
        return self.get_total_item_price() - self.get_total_discount_item_price()

    def get_final_price(self):
        if self.item.discount_price:
            return self.get_total_discount_item_price()
        return self.get_total_item_price()

    def get_total_quantity(self):
        return self.quantity


class FavoriteItem(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    is_fav = models.BooleanField(default=False)

    def __str__(self):
        return f"Favorite {self.quantity} of {self.item.title}"

    def get_total_item_price(self):
        return self.quantity * self.item.price

    def get_total_discount_item_price(self):
        return self.quantity * self.item.discount_price

    def get_amount_saved(self):
        return self.get_total_item_price() - self.get_total_discount_item_price()

    def get_final_price(self):
        if self.item.discount_price:
            return self.get_total_discount_item_price()
        return self.get_total_item_price()

    def get_total_quantity(self):
        return self.quantity


class CompareItem(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE)

    ordered = models.BooleanField(default=False)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    is_cmp = models.BooleanField(default=False)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"Compare {self.quantity} of {self.item.title}"

    def get_total_item_price(self):
        return self.quantity * self.item.price

    def get_total_discount_item_price(self):
        return self.quantity * self.item.discount_price

    def get_amount_saved(self):
        return self.get_total_item_price() - self.get_total_discount_item_price()

    def get_final_price(self):
        if self.item.discount_price:
            return self.get_total_discount_item_price()
        return self.get_total_item_price()

    def get_total_quantity(self):
        return self.quantity


class Coupon(models.Model):
    code = models.CharField(max_length=15, unique=True)
    discount_percent = models.FloatField()
    minimum_order_amount = models.FloatField()

    def __str__(self):
        return self.code


class MiniOrder(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)

    order_item = models.ForeignKey(OrderItem, on_delete=models.CASCADE)

    order_ref_number = models.CharField(default='ORD-100000', max_length=15)
    mini_order_ref_number = models.CharField(unique=True, default='MORN-100000', max_length=15)

    ordered_date = models.DateField()
    ordered_time = models.TimeField()
    ordered = models.BooleanField(default=False)
    order_status = models.CharField(choices=ORDER_STATUS, max_length=50, default='Preparing Order')

    # received_by_customer = models.BooleanField(default=False, blank=True, null=True)
    delivered = models.BooleanField(default=False, blank=True, null=True)
    return_requested = models.BooleanField(default=False)
    return_granted = models.BooleanField(default=False)

    return_window = models.DateTimeField(default=timezone.now) # () + timedelta(days=10)
    return_status = models.CharField(choices=RETURN_STATUS, max_length=50, default='')

    cancel_status = models.CharField(choices=CANCEL_STATUS, max_length=50, default='')
    cancel_requested = models.BooleanField(default=False)
    cancel_granted = models.BooleanField(default=False)

    payment_method = models.CharField(default='Online by card', max_length=30)

    def __str__(self):
        return f"{self.order_item.user} Mini_Order"


class CouponCustomer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, null=True)
    code = models.CharField(max_length=15)
    discount_amount = models.FloatField(null=True)
    order_amount = models.FloatField(null=True)
    used = models.BooleanField(default=False)
    applicable = models.BooleanField(default=False)

    class Meta:
        unique_together = ('code', 'user')

    def __str__(self):
        return f"{self.code}_{self.user}"


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    coupon_customer = models.ForeignKey(CouponCustomer, on_delete=models.CASCADE, null=True)
    mini_order = models.ManyToManyField(MiniOrder)
    items = models.ManyToManyField(OrderItem)

    order_ref_number = models.CharField(unique=True, default='ORD-100000', max_length=15)
    ordered_date = models.DateField()
    ordered_time = models.TimeField()
    ordered = models.BooleanField(default=False)

    # shipping_address = models.ForeignKey(
    #     'Addresss', related_name='shipping_address', on_delete=models.SET_NULL, blank=True, null=True)
    # billing_address = models.ForeignKey(
    #     'Addresss', related_name='billing_address', on_delete=models.SET_NULL, blank=True, null=True)
    address = models.ForeignKey(CustomerAddress, on_delete=models.SET_NULL, blank=True, null=True)
    payment = models.ForeignKey(
        'Payment', on_delete=models.SET_NULL, blank=True, null=True)

    item_url = models.TextField(default='', blank=True, null=True)

    received = models.BooleanField(default=False, blank=True, null=True)

    payment_method = models.CharField(default='Online by card', max_length=30)
    total_items = models.IntegerField(blank=True, null=True)
    taxes = models.FloatField(default=0)

    # itemss = models.ForeignKey(Item, on_delete=models.SET_NULL, blank=True, null=True)

    '''
    1. Item added to cart
    2. Adding a billing address
    (Failed checkout)
    3. Payment
    (Preprocessing, processing, packaging etc.)
    4. Being delivered
    5. Received
    6. Refunds
    '''

    def __str__(self):
        return f"{self.user} Order"

    def get_total(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_final_price()
        if self.coupon_customer:
            total -= self.coupon_customer.discount_amount
        return total

    def get_sub_total(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_total_item_price()
        return total

    def get_discounted_total(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_amount_saved()
        return total


class Payment(models.Model):
    stripe_charge_id = models.CharField(max_length=50)
    user = models.ForeignKey(User,
                             on_delete=models.SET_NULL, blank=True, null=True)
    amount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user}_Payment"


class Reviews(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    item = models.ForeignKey(Item, on_delete=models.SET_NULL, null=True)
    date = models.DateTimeField(default=timezone.now)
    title = models.CharField(max_length=300)
    review_description = models.TextField()
    rating = models.CharField(choices=REVIEW_RATING_CHOICES, max_length=1)
    reviewed = models.BooleanField(default=False)

    def __str__(self):
        try:
            return f"{self.user.first_name}_{self.title}"
        except:
            return f"{self.user}_{self.title}"


class Return(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    mini_order = models.ForeignKey(MiniOrder, on_delete=models.SET_NULL, null=True)
    return_date = models.DateTimeField(default=timezone.now)
    return_reason = models.CharField(choices=RETURN_REASON, max_length=50, default='')
    request_return_type = models.CharField(choices=REQUEST_RETURN_TYPE, max_length=50, default='RETURN')
    review_description = models.TextField(null=True)

    def __str__(self):
        try:
            return f"{self.user.first_name}_{self.return_reason}_RETURNED"
        except:
            return f"{self.user}_{self.return_reason}_RETURNED"


class Cancel(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    mini_order = models.ForeignKey(MiniOrder, on_delete=models.SET_NULL, null=True)

    cancel_date = models.DateTimeField(default=timezone.now)
    cancel_reason = models.CharField(choices=CANCEL_REASON, max_length=50, default='')
    request_cancel_type = models.CharField(choices=REQUEST_CANCEL_TYPE, max_length=50, default='CANCEL')
    review_description = models.TextField(null=True)

    def __str__(self):
        try:
            return f"{self.user.first_name}_{self.cancel_reason}_CANCELED"
        except:
            return f"{self.user}_{self.cancel_reason}_CANCELED"


class PrescriptionUpload(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    prescription = models.ImageField()

    def __str__(self):
        return f"{self.user}_PrescriptionUpload"

