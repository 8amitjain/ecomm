import django_filters
from django_filters import DateFilter, CharFilter, NumberFilter, NumericRangeFilter, RangeFilter, ChoiceFilter

from store.models import Item


class OrderFilter(django_filters.FilterSet):
    discount_price = RangeFilter(field_name="discount_price")
    # too = NumberFilter(field_name="discount_price", lookup_expr='lt')
    note = CharFilter(field_name='title', lookup_expr='icontains')

    class Meta:
        model = Item
        fields = ['price', 'discount_price', 'category', 'is_active', 'brand']
