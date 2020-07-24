from django import forms
from .models import VendorLocation
from mapwidgets.widgets import GooglePointFieldWidget

from .models import Item, Category, Brands, VendorAddress, SameItem
from store.models import Order, MiniOrder


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


class SameItemForm(forms.ModelForm):

    class Meta:
        model = SameItem
        fields = ('stock_no', )


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
        model = MiniOrder
        fields = ('order_status',)


class ReturnForm(forms.ModelForm):

    class Meta:
        model = MiniOrder
        fields = ('return_status', 'return_granted')


class CancelForm(forms.ModelForm):

    class Meta:
        model = MiniOrder
        fields = ('cancel_status', 'cancel_granted')


class BrandsForm(forms.ModelForm):
    brand_image = forms.ImageField(required=False)

    class Meta:
        model = Brands
        fields = ('brand_name', 'brand_image')


class LocationForm(forms.ModelForm):

    class Meta:
        model = VendorLocation
        fields = ("location",)
        widgets = {
            'location': GooglePointFieldWidget,
            # 'name': GoogleStaticOverlayMapWidget,
        }


class VendorAddressForm(forms.ModelForm):
    class Meta:
        model = VendorAddress
        fields = ('street_address', 'apartment_address', 'city', 'postal_code')
