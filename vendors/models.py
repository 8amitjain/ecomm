from django.db import models
from django.shortcuts import reverse
from django.contrib.gis.db import models as geo_models

from users.models import User

LABEL_CHOICES = (
    ('Sale', 'Sale'),
    ('New', 'New'),
    ('Promotion', 'Promotion'),
    ('Trending', 'Trending'),
    ('Top Selling', 'Top Selling'),
)


class VendorLocation(geo_models.Model):
    vendor_ref_id = models.CharField(unique=True, max_length=15)  # or vendor name here
    location = geo_models.PointField(help_text="Use map widget for point the house location")

    def __str__(self):
        return f"{self.location} point location"

    class Meta:
        verbose_name_plural = 'Vendor Locations'


class VendorAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    location = models.ForeignKey(VendorLocation, on_delete=models.CASCADE, null=True)

    street_address = models.CharField(max_length=100, null=True)
    apartment_address = models.CharField(max_length=100, null=True)

    city = models.TextField(default='Jalgaon')
    postal_code = models.IntegerField(null=True)

    def __str__(self):
        return f"{self.user} Address"

    class Meta:
        verbose_name_plural = 'Vendor Addresses'


class Vendor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    address = models.ForeignKey(VendorAddress, on_delete=models.CASCADE, null=True)
    adding_product = models.BooleanField(default=False)

    # shop_name = models.CharField()
    phone_number = models.BigIntegerField(null=True)
    pin_code = models.IntegerField(null=True)
    vendor_ref_number = models.CharField(unique=True, default='VRN-100000', max_length=15)

    def __str__(self):
        return self.user.username


class Brands(models.Model):
    brand_name = models.CharField(max_length=50, unique=True)
    brand_image = models.ImageField(null=True, blank=True)

    def __str__(self):
        return self.brand_name


class Category(models.Model):
    title = models.CharField(max_length=100, unique=True)
    slug = models.SlugField()
    description = models.TextField()
    image = models.ImageField(null=True)  # image of slide ...
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("store:category", kwargs={
            'slug': self.slug
        })


class SameItem(models.Model):
    item_ref_number = models.CharField(default='IRN-100000', max_length=15)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    stock_no = models.IntegerField(null=True)  # number of products in stock
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['item_ref_number']
        unique_together = ('item_ref_number', 'vendor')

    def __str__(self):
        return f"{self.vendor}_{self.item_ref_number}"


class Item(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    # sold_by = models.OneToOneField(Vendor, on_delete=models.CASCADE)
    vendors = models.ManyToManyField(Vendor)
    same_item = models.ManyToManyField(SameItem)

    brand = models.ForeignKey(Brands, on_delete=models.CASCADE)

    item_ref_number = models.CharField(unique=True, default='IRN-100000', max_length=15)
    title = models.CharField(max_length=100)
    price = models.FloatField(null=True)
    discount_price = models.FloatField(blank=True, null=True)
    label = models.CharField(choices=LABEL_CHOICES, max_length=11, null=True)
    slug = models.SlugField(unique=True)

    stock_no = models.IntegerField()  # number of products in stock

    short_description = models.TextField(help_text='To describe product in short', null=True)
    description = models.TextField(help_text='Overview product', null=True)
    key_benefits = models.TextField(help_text='Describe product\'s Benefits', null=True)
    direction_for_use = models.TextField(help_text='Describe product\'s Direction for use / Dosage', null=True)
    safety_information = models.TextField(help_text='Describe product\'s Safety information', null=True)

    image_main = models.ImageField(null=True)
    image_2 = models.ImageField(null=True)
    image_3 = models.ImageField(null=True)
    image_4 = models.ImageField(null=True)
    image_5 = models.ImageField(null=True)

    is_active = models.BooleanField(default=True)
    trending = models.BooleanField(default=False)
    has_variation = models.BooleanField(default=False,
                                        help_text='If this is ticked, You can add variation later to this product.')
    variation_id = models.CharField(null=True, max_length=20)

    class Meta:
        ordering = ['item_ref_number']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("store:store-product", kwargs={
            'slug': self.slug
        })

    def get_add_to_cart_url(self):
        return reverse("store:add-to-cart", kwargs={
            'slug': self.slug
        })

    def get_remove_from_cart_url(self):
        return reverse("store:remove-single-item-from-cart", kwargs={
            'slug': self.slug
        })

    def get_remove_single_item_from_cart_url(self):
        return reverse("store:get_remove_single_item_from_cart_url", kwargs={
            'slug': self.slug
        })

    def get_add_to_favorite_url(self):
        return reverse("store:add-to-favorite", kwargs={
            'slug': self.slug
        })

    def get_add_to_compare_url(self):
        return reverse("store:add-to-compare", kwargs={
            'slug': self.slug
        })




