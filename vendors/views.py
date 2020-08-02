from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.shortcuts import render, redirect
from django.template.defaultfilters import slugify
from django.utils import timezone
# from stripe.api_resources import order

from .forms import ItemForm, CategoryForm, OrderForm, ItemVariationsForm, BrandsForm, VendorAddressForm, LocationForm,\
                   SameItemForm, ReturnForm, CancelForm
from .filters import ProductOrderFilter, ItemFilter, CategoryFilter, VendorItemFilter, ProductReturnedFilter, \
                     ProductCanceledFilter, BrandsFilter
from .models import Item, Category, VendorLocation, SameItem, Brands
from users.models import User
from store.models import Order, OrderItem, MiniOrder
from .models import Vendor
from store.filters import OrderFilter


@login_required
def products_add(request):
    context = {'title': 'Add Products',
               'submit': 'Add'}
    if request.user.vendor.adding_product:
        if request.POST:
            form = ItemForm(request.POST, request.FILES)
            if form.is_valid():
                item = form.save(commit=False)
                # item.sold_by = request.user.vendor
                item.slug = slugify(item.title)
                item.save()
                item.vendors.add(request.user.vendor)
                item.variation_id = f"IVRN-{100000 + item.id}"
                item.item_ref_number = f"IRN-{100000 + int(item.id)}"
                item.slug = slugify(f"{str(item.title)}+{'-'}+{str(item.item_ref_number)}")
                item.save()

                same_items = SameItem.objects.create(vendor=request.user.vendor, item_ref_number=item.item_ref_number,
                                                     stock_no=item.stock_no)
                same_items.save()

                item.same_item.add(same_items)
                item.save()

                return redirect('store:store')
            else:
                context['form'] = form

        else:
            form = ItemForm()
            context['form'] = form
        return render(request, 'vendors/form.html', context)

    else:
        model = Item.objects.all()

        item_filter = VendorItemFilter(request.GET, queryset=model)
        model = item_filter.qs
        context['filter'] = item_filter
        context['object_list'] = model
    return render(request, 'vendors/vendor_item_select.html', context)


@login_required
def products_update(request, pk):
    context = {'title': 'Update Products',
               'submit': 'Update'}
    if request.user.vendor.adding_product:
        item = Item.objects.get(id=pk)
        if request.POST:
            form = ItemForm(request.POST, request.FILES, instance=item)
            if form.is_valid():
                item = form.save(commit=False)
                # item.sold_by = request.user.vendor
                item.slug = slugify(item.title)
                item.save()
                # item.vendors.add(request.user.vendor)
                # item.variation_id = f"IVRN-{100000 + item.id}"
                # item.item_ref_number = f"IRN-{100000 + int(item.id)}"
                item.slug = slugify(f"{str(item.title)}+{'-'}+{str(item.item_ref_number)}")
                item.save()

                same_items = SameItem.objects.get(vendor=request.user.vendor, item_ref_number=item.item_ref_number)
                same_items.stock_no = item.stock_no
                same_items.save()

                # item.same_item.add(same_items)
                # item.save()

                return redirect('store:store')
            else:
                context['form'] = form
                context['product'] = item

        else:
            form = ItemForm(instance=item)
            context['form'] = form
            context['product'] = item
        return render(request, 'vendors/products_update.html', context)

    else:
        context = {}
        item = Item.objects.get(id=pk)
        if request.POST:
            form = SameItemForm(request.POST)
            try:
                if form.is_valid():
                    item_form = form.save(commit=False)
                    item_form.vendor = request.user.vendor
                    item_form.item_ref_number = item.item_ref_number
                    item_form.save()
                    item.same_item.add(item_form)
                    item.vendors.add(request.user.vendor)
                    item.save()
            except IntegrityError:
                if form.is_valid():
                    item_form = form.save(commit=False)
                    same_items = SameItem.objects.get(vendor=request.user.vendor, item_ref_number=item.item_ref_number)
                    same_items.stock_no = item_form.stock_no
                    same_items.save()
                return redirect('vendors-products')
            else:
                context['form'] = form

        else:
            form = SameItemForm()
            context['form'] = form

        return render(request, 'vendors/form.html', context)


@login_required
def product_delete(request, pk):
    try:
        item = Item.objects.get(id=pk)
        item.vendors.remove(request.user.vendor)
        if not item.vendors.all():
            item.delete()
        SameItem.objects.get(vendor=request.user.vendor, item_ref_number=item.item_ref_number).delete()

    except ObjectDoesNotExist:
        pass
    return redirect('vendors-products')


@login_required
def product_sell(request, pk):
    if not request.user.vendor.adding_product:
        context = {'title': 'Add Products',
                   'submit': 'Add'}
        item = Item.objects.get(id=pk)
        if request.POST:
            form = SameItemForm(request.POST)
            try:
                if form.is_valid():
                    item_form = form.save(commit=False)
                    item_form.vendor = request.user.vendor
                    item_form.item_ref_number = item.item_ref_number
                    item_form.save()
                    item.same_item.add(item_form)
                    item.vendors.add(request.user.vendor)
                    item.save()
            except IntegrityError:
                if form.is_valid():
                    item_form = form.save(commit=False)
                    same_items = SameItem.objects.get(vendor=request.user.vendor, item_ref_number=item.item_ref_number)
                    same_items.stock_no = item_form.stock_no
                    same_items.save()
                return redirect('vendors-products')
            else:
                context['form'] = form

        else:
            form = SameItemForm()
            context['form'] = form

        return render(request, 'vendors/form.html', context)
    else:
        redirect("/")


@login_required
def product_varient_add(request, var_id):
    context = {'title': 'Add Product Varient',
               'submit': 'Add'}
    if request.user.vendor.adding_product:
        itemss = Item.objects.filter(variation_id=var_id).first()
        if request.POST:
            form = ItemVariationsForm(request.POST, request.FILES)
            if form.is_valid():
                item = form.save(commit=False)
                item.category = itemss.category
                item.brand = itemss.brand
                item.has_variation = True
                # item.sold_by = request.user.vendor
                item.slug = slugify(item.title)
                item.variation_id = var_id
                item.save()
                item.vendors.add(request.user.vendor)
                item.item_ref_number = f"IRN-{100000 + int(item.id)}"
                item.slug = slugify(f"{str(item.title)}+{'-'}+{str(item.item_ref_number)}")
                item.save()

                same_items = SameItem.objects.create(vendor=request.user.vendor, item_ref_number=item.item_ref_number,
                                                     stock_no=item.stock_no)
                same_items.save()

                item.same_item.add(same_items)
                item.save()

                return redirect('store:store')
            else:
                context['form'] = form
        else:
            form = ItemVariationsForm()
            context['form'] = form
        return render(request, 'vendors/form.html', context)
    else:
        redirect("/")
   

@login_required
def category_add(request):
    context = {'title': 'Add Category',
               'submit': 'Add Category'}
    if request.user.vendor.adding_product:
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
    else:
        return redirect("/")


@login_required
def brand_add(request):
    context = {'title': 'Add Brand',
               'submit': 'Add'}
    if request.user.vendor.adding_product:
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
    else:
        return redirect("/")


@login_required
def brand_display(request):
    if request.user.vendor.adding_product:
        brand = Brands.objects.all()
        filters = BrandsFilter(request.GET, queryset=brand)
        len_brand = len(brand)
        print(filters.form)
        brand = filters.qs
        context = {
            'brands': brand,
            'len_brands': len_brand,
            'filter': filters,

        }
        return render(request, 'vendors/brand.html', context)
    else:
        return redirect("/")


@login_required
def category_display(request):
    if request.user.vendor.adding_product:
        category = Category.objects.all()
        filters = CategoryFilter(request.GET, queryset=category)
        len_category = len(category)
        print(filters.form)
        category = filters.qs
        context = {
            'category': category,
            'len_category': len_category,
            'filter': filters,

        }
        return render(request, 'vendors/category.html', context)
    else:
        return redirect("/")


@login_required
def products_ordered_update(request, pk):
    context = {'title': 'Order Update',
               'submit': 'Update'}
    # vendor = Vendor.objects.get(user_id=request.user.vendor.user_id)
    mini_order = MiniOrder.objects.get(id=pk)
    order = Order.objects.get(order_ref_number=mini_order.order_ref_number)
    order_item = OrderItem.objects.filter(ordered=True, order=order)

    if request.POST:
        form = OrderForm(request.POST, instance=mini_order)
        print(form)
        if form.is_valid():
            form.save()
            return redirect('vendors-products-ordered')
        else:
            context['form'] = form
            context['order_item'] = order_item
            context['order'] = order
            context['mini_order'] = mini_order

    else:
        form = OrderForm(instance=mini_order)
        context['form'] = form
        context['order_item'] = order_item
        context['order'] = order
        context['mini_order'] = mini_order
    return render(request, 'vendors/products_ordered_detail.html', context)


@login_required
def products_ordered(request):
    m_orders = MiniOrder.objects.filter(ordered=True, vendor=request.user.vendor, delivered=False)
    len_m_orders = len(m_orders)
    try:
        orderr = Order.objects.get(mini_order=m_orders.first().id)
    except:
        orderr = ''
    filters = ProductOrderFilter(request.GET, queryset=m_orders)

    m_orders = filters.qs
    context = {
        'orders': m_orders,
        'len_m_orders': len_m_orders,
        'orderr': orderr,
        'filter': filters,
    }
    return render(request, 'vendors/products_ordered.html', context)


@login_required
def products_display(request):
    # same_item = SameItem.objects.filter(vendor=request.user.vendor)

    products = request.user.vendor.item_set.all()
    same_item = SameItem.objects.filter(vendor=request.user.vendor)
    len_same_item = len(same_item)
    filters = ItemFilter(request.GET, queryset=products)
    products = filters.qs
    context = {
        'products': products,
        'same_item': same_item,
        'len_same_item': len_same_item,
        'filter': filters
    }
    return render(request, 'vendors/products.html', context)


@login_required
def products_returned(request):
    orders = MiniOrder.objects.filter(ordered=True, vendor=request.user.vendor, return_requested=True,
                                      )  # return_granted=False
    try:
        orderr = Order.objects.get(mini_order=orders.first().id)
    except AttributeError:
        orderr = ''
    filters = ProductReturnedFilter(request.GET, queryset=orders)
    len_returned_products = len(orders)

    orders = filters.qs
    context = {
        'orders': orders,
        'orderr': orderr,
        'len_returned_products': len_returned_products,
        'filter': filters,
    }
    return render(request, 'vendors/products_returned.html', context)


@login_required
def products_returned_update(request, pk):
    context = {}
    mini_order = MiniOrder.objects.get(id=pk)
    order = Order.objects.get(order_ref_number=mini_order.order_ref_number)
    order_item = OrderItem.objects.filter(ordered=True, order=order)

    if request.POST:
        form = ReturnForm(request.POST, instance=mini_order)
        if form.is_valid():
            form.save()
            return redirect('vendors-products-returned')
        else:
            context['form'] = form
            context['order_item'] = order_item
            context['order'] = order
            context['mini_order'] = mini_order

    else:
        form = ReturnForm(instance=mini_order)
        context['form'] = form
        context['order_item'] = order_item
        context['order'] = order
        context['mini_order'] = mini_order
    return render(request, 'vendors/products_return_detail.html', context)


@login_required
def products_canceled(request):
    orders = MiniOrder.objects.filter(ordered=True, vendor=request.user.vendor, cancel_requested=True,
                                      )  # return_granted=False
    try:
        orderr = Order.objects.get(mini_order=orders.first().id)
    except AttributeError:
        orderr = ''
    filters = ProductCanceledFilter(request.GET, queryset=orders)
    len_cancel_products = len(orders)
    orders = filters.qs
    context = {
        'orders': orders,
        'orderr': orderr,
        'len_cancel_products': len_cancel_products,
        'filter': filters,
    }
    return render(request, 'vendors/products_canceled.html', context)


@login_required
def products_cancel_update(request, pk):
    context = {}
    mini_order = MiniOrder.objects.get(id=pk)
    order = Order.objects.get(order_ref_number=mini_order.order_ref_number)
    order_item = OrderItem.objects.filter(ordered=True, order=order)

    if request.POST:
        form = CancelForm(request.POST, instance=mini_order)
        if form.is_valid():
            form.save()
            return redirect('vendors-products-canceled')
        else:
            context['form'] = form
            context['order_item'] = order_item
            context['order'] = order
            context['mini_order'] = mini_order

    else:
        form = CancelForm(instance=mini_order)
        context['form'] = form
        context['order_item'] = order_item
        context['order'] = order
        context['mini_order'] = mini_order
    return render(request, 'vendors/products_canceled_detail.html', context)


@login_required
def sales(request):
    orders = MiniOrder.objects.filter(vendor=request.user.vendor, ordered=True, return_granted=False)
    orders_today = MiniOrder.objects.filter(vendor=request.user.vendor, ordered=True, return_granted=False,
                                            ordered_date=timezone.datetime.now().strftime('%Y-%m-%d'))
    total_sales = 0
    total_orders = len(orders)
    pending_order = 0
    for order in orders:
        total_sales = total_sales + int(order.order_item.get_final_price())

        if order.delivered is False:
            pending_order += 1

    today_total_sales = 0
    today_total_orders = len(orders_today)
    for order in orders_today:
        today_total_sales = today_total_sales + int(order.order_item.get_final_price())

    item_out_of_stock = SameItem.objects.filter(vendor=request.user.vendor, stock_no=0)
    len_item_out_of_stock = len(item_out_of_stock)
    context = {
        'total_sales': total_sales,
        'total_orders': total_orders,
        'today_total_sales': today_total_sales,
        'today_total_orders': today_total_orders,
        'pending_order': pending_order,
        'len_item_out_of_stock ': len_item_out_of_stock,
    }
    return render(request, 'vendors/sales.html', context)


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
        'title': 'Vendor Address',
        'submit': 'Submit'
    }
    return render(request, 'vendors/location_form.html', context)

