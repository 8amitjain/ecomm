from django.db import models
from django.db.models.signals import post_save
from django.core.validators import MaxValueValidator
from django.utils import timezone

from users.models import User, Vendor
from vendors.models import Item, Category


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
    ('CANCELED', 'CANCELED'),
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


class Addresss(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    street_address = models.CharField(max_length=100)
    apartment_address = models.CharField(max_length=100)

    city = models.TextField(default='Jalgaon')
    phone_number = models.IntegerField(validators=[MaxValueValidator(9999999999)], blank=True)
    postal_code = models.IntegerField(validators=[MaxValueValidator(9999999999)])

    address_type = models.CharField(max_length=1, choices=ADDRESS_CHOICES)
    default = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user} Address"

    class Meta:
        verbose_name_plural = 'Addresses'


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


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    # itemss = models.ForeignKey(OrderItem, on_delete=models.CASCADE)

    # ref_code = models.CharField(max_length=20, blank=True, null=True, unique=True)
    order_ref_number = models.CharField(unique=True, default='ORD-100000', max_length=15)
    items = models.ManyToManyField(OrderItem)
    ordered_date = models.DateField()
    ordered_time = models.TimeField()
    ordered = models.BooleanField(default=False)

    shipping_address = models.ForeignKey(
        'Addresss', related_name='shipping_address', on_delete=models.SET_NULL, blank=True, null=True)
    billing_address = models.ForeignKey(
        'Addresss', related_name='billing_address', on_delete=models.SET_NULL, blank=True, null=True)
    payment = models.ForeignKey(
        'Payment', on_delete=models.SET_NULL, blank=True, null=True)
    coupon = models.ForeignKey(
        'Coupon', on_delete=models.SET_NULL, blank=True, null=True)

    # being_delivered = models.BooleanField(default=False, blank=True, null=True)

    refund_requested = models.BooleanField(default=False)
    refund_granted = models.BooleanField(default=False)
    item_url = models.TextField(default='', blank=True, null=True)

    order_status = models.CharField(choices=ORDER_STATUS, max_length=50, default='Preparing Order')
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
        if self.coupon:
            total -= self.coupon.amount
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
        return self.user.username


class Coupon(models.Model):
    code = models.CharField(max_length=15)
    amount = models.FloatField()

    def __str__(self):
        return self.code


class Refund(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    reason = models.TextField()
    accepted = models.BooleanField(default=False)
    email = models.EmailField()

    def __str__(self):
        return f"{self.pk}"


class Reviews(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    item = models.ForeignKey(Item, on_delete=models.SET_NULL, null=True)
    date = models.DateTimeField(default=timezone.now())
    title = models.CharField(max_length=300)
    review_description = models.TextField()
    rating = models.CharField(choices=REVIEW_RATING_CHOICES, max_length=1)
    reviewed = models.BooleanField(default=False)

    def __str__(self):
        try:
            return f"{self.user.first_name}_{self.title}"
        except:
            return f"{self.user}_{self.title}"



