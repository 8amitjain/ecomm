import django_filters
from django_filters import DateFilter, CharFilter, RangeFilter

from .models import Item, Category, Brands
from store.models import MiniOrder


class ProductOrderFilter(django_filters.FilterSet):
    start_date = DateFilter(field_name="ordered_date", lookup_expr='gte')
    end_date = DateFilter(field_name="ordered_date", lookup_expr='lte')
    mini_order_ref_number = CharFilter(field_name='mini_order_ref_number', lookup_expr='icontains')
    payment_method = CharFilter(field_name='payment_method', lookup_expr='icontains')

    class Meta:
        model = MiniOrder
        fields = ['order_status']


class ItemFilter(django_filters.FilterSet):
    discount_price = RangeFilter(field_name="discount_price")
    note = CharFilter(field_name='title', lookup_expr='icontains')
    irn = CharFilter(field_name='item_ref_number', lookup_expr='icontains')

    class Meta:
        model = Item
        fields = ['category', 'is_active', 'brand', 'label', 'stock_no']


class CategoryFilter(django_filters.FilterSet):
    note = CharFilter(field_name='title', lookup_expr='icontains')

    class Meta:
        model = Category
        fields = ['is_active']


class BrandsFilter(django_filters.FilterSet):
    note = CharFilter(field_name='brand_name', lookup_expr='icontains')

    class Meta:
        model = Brands
        fields = []


class VendorItemFilter(django_filters.FilterSet):
    title = CharFilter(field_name='title', lookup_expr='icontains')
    categoryy = CharFilter(field_name='category', lookup_expr='icontains')
    brandd = CharFilter(field_name='brand', lookup_expr='icontains')
    discount_price = RangeFilter(field_name="discount_price")

    class Meta:
        model = Item
        fields = ['title', 'category', 'discount_price', 'brand']


class ProductReturnedFilter(django_filters.FilterSet):
    start_date = DateFilter(field_name="ordered_date", lookup_expr='gte')
    end_date = DateFilter(field_name="ordered_date", lookup_expr='lte')
    mini_order_ref_number = CharFilter(field_name='mini_order_ref_number', lookup_expr='icontains')
    payment_method = CharFilter(field_name='payment_method', lookup_expr='icontains')

    class Meta:
        model = MiniOrder
        fields = ['order_status', 'return_status']


class ProductCanceledFilter(django_filters.FilterSet):
    start_date = DateFilter(field_name="ordered_date", lookup_expr='gte')
    end_date = DateFilter(field_name="ordered_date", lookup_expr='lte')
    mini_order_ref_number = CharFilter(field_name='mini_order_ref_number', lookup_expr='icontains')
    payment_method = CharFilter(field_name='payment_method', lookup_expr='icontains')

    class Meta:
        model = MiniOrder
        fields = ['order_status', 'cancel_status']

