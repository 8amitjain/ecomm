from django import forms
from .models import Reviews, CustomerLocation, Return, Cancel, CouponCustomer, PrescriptionUpload
from mapwidgets.widgets import GooglePointFieldWidget

PAYMENT_CHOICES = (
    ('S', 'Stripe'),
    ('P', 'PayPal')
)


class LocationForm(forms.ModelForm):

    class Meta:
        model = CustomerLocation
        fields = ("location",)
        widgets = {
            'location': GooglePointFieldWidget,
            # 'name': GoogleStaticOverlayMapWidget,
        }


class CheckoutForm(forms.Form):
    shipping_address = forms.CharField(required=False)
    shipping_address2 = forms.CharField(required=False)
    shipping_city = forms.CharField(required=False)
    shipping_postal_code = forms.IntegerField(required=False)
    shipping_phone_number = forms.IntegerField(required=False)

    billing_address = forms.CharField(required=False)
    billing_address2 = forms.CharField(required=False)
    billing_city = forms.CharField(required=False)
    billing_postal_code = forms.IntegerField(required=False)
    billing_phone_number = forms.IntegerField(required=False)

    same_billing_address = forms.BooleanField(required=False)
    set_default_shipping = forms.BooleanField(required=False)
    use_default_shipping = forms.BooleanField(required=False)
    set_default_billing = forms.BooleanField(required=False)
    use_default_billing = forms.BooleanField(required=False)

    payment_option = forms.ChoiceField(
        widget=forms.RadioSelect, choices=PAYMENT_CHOICES)


class CouponForm(forms.Form):
    code = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Promo code'
    }))


class RefundForm(forms.Form):
    ref_code = forms.CharField()
    message = forms.CharField(widget=forms.Textarea(attrs={
        'rows': 4
    }))
    email = forms.EmailField()


class PaymentForm(forms.Form):
    stripeToken = forms.CharField(required=False)
    save = forms.BooleanField(required=False)
    use_default = forms.BooleanField(required=False)


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Reviews
        fields = ('title', 'review_description', 'rating')


class ReturnForm(forms.ModelForm):
    review_description = forms.Textarea()

    class Meta:
        model = Return
        fields = ('return_reason', 'request_return_type', 'review_description')


class CancelForm(forms.ModelForm):
    review_description = forms.Textarea()

    class Meta:
        model = Cancel
        fields = ('cancel_reason', 'request_cancel_type', 'review_description')


class CouponCustomerForm(forms.ModelForm):

    class Meta:
        model = CouponCustomer
        fields = ('code',)


class PrescriptionUploadForm(forms.ModelForm):

    class Meta:
        model = PrescriptionUpload
        fields = ('prescription',)
