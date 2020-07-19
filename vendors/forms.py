from django import forms
from django.db import transaction

from .models import Item, Category, Brands
from store.models import Order


class ItemForm(forms.ModelForm):
    image_2 = forms.ImageField(required=False)
    image_3 = forms.ImageField(required=False)
    image_4 = forms.ImageField(required=False)
    image_5 = forms.ImageField(required=False)
    short_description = forms.CharField(required=False)
    description = forms.Textarea()
    key_benefits = forms.Textarea()
    direction_for_use = forms.Textarea()
    safety_information = forms.Textarea()

    class Meta:
        model = Item
        fields = ('category', 'brand', 'title', 'price', 'discount_price', 'label', 'stock_no', 'short_description',
                  'description', 'key_benefits', 'direction_for_use', 'safety_information', 'is_active', 'image_main',
                  'image_2', 'image_3', 'image_4', 'image_5', 'has_variation')


class ItemVariationsForm(forms.ModelForm):
    image_2 = forms.ImageField(required=False)
    image_3 = forms.ImageField(required=False)
    image_4 = forms.ImageField(required=False)
    image_5 = forms.ImageField(required=False)

    class Meta:
        model = Item
        fields = ('title', 'price', 'discount_price', 'label', 'stock_no', 'short_description', 'description',
                  'key_benefits', 'direction_for_use', 'safety_information', 'is_active', 'image_main', 'image_2',
                  'image_3', 'image_4', 'image_5')


class CategoryForm(forms.ModelForm):
    image = forms.ImageField(required=False)  # image of slide ...

    class Meta:
        model = Category
        fields = ('title', 'description', 'is_active', 'image')


class OrderForm(forms.ModelForm):

    class Meta:
        model = Order
        fields = ('order_status',)


class BrandsForm(forms.ModelForm):
    brand_image = forms.ImageField(required=False)

    class Meta:
        model = Brands
        fields = ('brand_name', 'brand_image')

