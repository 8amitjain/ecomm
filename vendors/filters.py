import django_filters
from django_filters import DateFilter, CharFilter

from .models import Item, Category
from store.models import Order


class ProductOrderFilter(django_filters.FilterSet):
    start_date = DateFilter(field_name="ordered_date", lookup_expr='gte')
    end_date = DateFilter(field_name="ordered_date", lookup_expr='lte')
    # note = CharFilter(field_name='shipping_address', lookup_expr='icontains')

    class Meta:
        model = Order
        fields = ['order_ref_number', 'ordered_date', 'payment_method', 'order_status', 'items', 'received']


class ItemFilter(django_filters.FilterSet):
    note = CharFilter(field_name='title', lookup_expr='icontains')

    class Meta:
        model = Item
        fields = ['item_ref_number', 'title', 'category', 'price', 'discount_price', 'label', 'stock_no']


class CategoryFilter(django_filters.FilterSet):
    note = CharFilter(field_name='title', lookup_expr='icontains')

    class Meta:
        model = Category
        fields = ['title', 'description', 'is_active']
