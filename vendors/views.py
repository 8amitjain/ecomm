from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect
from django.template.defaultfilters import slugify
from django.utils import timezone
from stripe.api_resources import order

from .forms import ItemForm, CategoryForm, OrderForm, ItemVariationsForm, BrandsForm, VendorAddressForm, LocationForm
from .filters import ProductOrderFilter, ItemFilter, CategoryFilter
from .models import Item, Category, VendorLocation
from users.models import User
from store.models import Order, OrderItem
from .models import Vendor


@login_required
def item_add(request):
    context = {}
    if request.POST:
        form = ItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.sold_by = request.user.vendor
            item.slug = slugify(item.title)
            item.save()
            item.variation_id = f"IVRN-{100000 + item.id}"
            item.slug = slugify(f"{str(item.title)}+{'-'}+{str(item.item_ref_number)}")
            item.item_ref_number = f"IRN-{100000 + int(item.id)}"

            item.save()
            return redirect('store:store')
        else:
            context['form'] = form

    else:
        form = ItemForm()
        context['form'] = form
    return render(request, 'vendors/form.html', context)


@login_required
def varient_item_add(request, var_id):
    context = {}
    itemss = Item.objects.filter(variation_id=var_id).first()
    if request.POST:
        form = ItemVariationsForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.category = itemss.category
            item.brand = itemss.brand
            item.has_variation = True
            item.sold_by = request.user.vendor
            item.slug = slugify(item.title)
            item.variation_id = var_id
            item.save()

            item.slug = slugify(f"{str(item.title)}+{'-'}+{str(item.item_ref_number)}")
            item.item_ref_number = f"IRN-{100000 + int(item.id)}"
            item.save()

            return redirect('store:store')
        else:
            context['form'] = form
    else:
        form = ItemVariationsForm()
        context['form'] = form
    return render(request, 'vendors/form.html', context)


@login_required
def category_add(request):
    context = {}
    if request.POST:
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.slug = slugify(item.title)
            item.save()
            return redirect('vendors-category')
        else:
            context['form'] = form

    else:
        form = CategoryForm()
        context['form'] = form
    return render(request, 'vendors/form.html', context)


@login_required
def products_ordered_update(request, pk):
    context = {}
    # vendor = Vendor.objects.get(user_id=request.user.vendor.user_id)
    order = Order.objects.get(ordered=True, vendor=request.user.vendor, id=pk)
    order_item = OrderItem.objects.filter(ordered=True, order=order)

    if request.POST:
        form = OrderForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            return redirect('vendors-products-ordered')
        else:
            context['form'] = form
            context['order_item'] = order_item
            context['order'] = order

    else:
        form = OrderForm(instance=order)
        context['form'] = form
        context['order_item'] = order_item
        context['order'] = order
    return render(request, 'vendors/products_ordered_detail.html', context)


@login_required
def products_ordered(request):
    orders = Order.objects.filter(ordered=True, vendor=request.user.vendor)  # add delivered is False
    filters = ProductOrderFilter(request.GET, queryset=orders)
    orders = filters.qs
    context = {
        'orders': orders,
        'filters': filters
    }
    return render(request, 'vendors/products_ordered.html', context)


@login_required
def category_display(request):
    category = Category.objects.all()
    filters = CategoryFilter(request.GET, queryset=category)
    category = filters.qs
    context = {
        'category': category,
        'filters': filters
    }
    return render(request, 'vendors/category.html', context)


@login_required
def products_display(request):
    products = Item.objects.filter(sold_by=request.user.vendor)
    filters = ItemFilter(request.GET, queryset=products)
    products = filters.qs
    context = {
        'products': products,
        'filters': filters
    }
    return render(request, 'vendors/products.html', context)


@login_required
def sales(request):
    orders = Order.objects.filter(vendor=request.user.vendor)
    orders_today = Order.objects.filter(vendor=request.user.vendor, ordered_date=timezone.datetime.now().strftime('%Y-%m-%d'))
    print(timezone.datetime.now().strftime('%Y-%m-%d'), 'date')
    total_sales = 0
    total_orders = len(orders)
    pending_order = 0
    for order in orders:
        total_sales = total_sales + int(order.get_total())

        if order.received is False:
            pending_order += 1

    today_total_sales = 0
    today_total_orders = len(orders_today)
    for order in orders_today:
        today_total_sales = today_total_sales + int(order.get_total())

    context = {
        'total_sales': total_sales,
        'total_orders': total_orders,
        'today_total_sales': today_total_sales,
        'today_total_orders': today_total_orders,
        'pending_order': pending_order,
    }
    return render(request, 'vendors/sales.html', context)


@login_required
def brand_add(request):
    context = {}
    if request.POST:
        form = BrandsForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('/')
        else:
            context['form'] = form

    else:
        form = BrandsForm()
        context['form'] = form
    return render(request, 'vendors/form.html', context)


@login_required
def vendor_address(request):
    if request.method == 'POST':
        form = VendorAddressForm(request.POST, instance=request.user.vendor.address)
        location_form = LocationForm(request.POST)
        if location_form.is_valid():
            try:
                location_point = VendorLocation.objects.get(
                    vendor_ref_id=f"{request.user.first_name}_{request.user.id}")
            except ObjectDoesNotExist:
                location_point = location_form.save(commit=False)
                location_point.vendor_ref_id = f"{request.user.first_name}_{request.user.id}"
                location_point.save()
                location_point = VendorLocation.objects.get(vendor_ref_id=location_point.vendor_ref_id)

        if form.is_valid():
            address_form = form.save(commit=False)
            address_form.user = request.user
            address_form.phone_number = request.user.phone_number
            address_form.location = location_point
            address_form.save()
            messages.success(request, f'Details Updated!')
            return redirect('/')
    else:
        form = VendorAddressForm(instance=request.user.vendor.address)
        location_form = LocationForm()

    context = {
        'form': form,
        'location_form': location_form,
    }
    return render(request, 'vendors/form.html', context)

