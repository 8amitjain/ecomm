from django.http import HttpResponseRedirect
from django.views.generic import View
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.shortcuts import redirect
from django.contrib import messages
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance
from stripe.api_resources.terminal import location

from vendors.models import VendorLocation, VendorAddress, Vendor

from .forms import CheckoutForm, CouponForm, PaymentForm, ReviewForm, LocationForm, ReturnForm, CancelForm, \
                   CouponCustomerForm, PrescriptionUploadForm, CustomerAddressForm
from .models import OrderItem, Order, FavoriteItem, CompareItem, Payment, Coupon, UserProfile, Slide, Reviews, \
                    CustomerLocation, MiniOrder, CouponCustomer, CustomerAddress

from vendors.models import Item, Category, Brands
from users.models import User
from .filters import OrderFilter

import stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


def shop_view(request):
    model = Item.objects.all()

    item_filter = OrderFilter(request.GET, queryset=model)
    model = item_filter.qs
    context = {
        'object_list': model,
        'filter': item_filter
    }
    return render(request, 'store/subcategory.html', context)


def category_view(request, slug):
    model2 = Category.objects.get(title=slug)
    model = Item.objects.filter(category=model2.id)

    context = {
        'object_list': model,
    }
    return render(request, 'store/category_wise.html', context)


def product(request, slug):
    item = Item.objects.get(id=slug)
    related_item = Item.objects.filter(category=item.category)
    variations = Item.objects.filter(variation_id=item.variation_id)
    order_item = OrderItem.objects.filter(user=request.user, ordered=True, item=item)
    reviews = Reviews.objects.filter(item=item)
    try:
        user_review = Reviews.objects.get(item=item, user=request.user)
    except ObjectDoesNotExist:
        user_review = None
    number_of_reviews = len(reviews)

    total_rating = 0
    try:
        for x in reviews:
            total_rating += int(x.rating)
        average_rating = total_rating // number_of_reviews
    except ZeroDivisionError:
        average_rating = 0
    context = {'item': item,
               'variations': variations,
               'related_item': related_item,
               'order_item': order_item,
               'reviews': reviews,
               'number_of_reviews': number_of_reviews,
               'average_rating': average_rating,
               'user_review': user_review,
               }
    return render(request, 'store/product.html', context)


class CartView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            form = CouponCustomerForm()
            prescription_form = PrescriptionUploadForm(self.request.FILES)
            context = {
                'object': order,
                'form': form,
                'prescription_form': prescription_form,
            }
            return render(self.request, 'store/cart.html', context)
        except ObjectDoesNotExist:
            messages.error(self.request, "You do not have any item in cart")
            return redirect("/")

    def post(self, *args, **kwargs):
        form = CouponCustomerForm(self.request.POST)
        prescription_form = PrescriptionUploadForm(self.request.POST, self.request.FILES)
        order = Order.objects.get(user=self.request.user, ordered=False)

        if prescription_form.is_valid():
            p_form = prescription_form.save(commit=False)
            p_form.user = self.request.user
            p_form.save()
            order.prescription = p_form
            order.save()
            context = {
                'object': order,
                'form': form,
                'prescription_form': prescription_form
            }
            return render(self.request, 'store/cart.html', context)
        if form.is_valid():
                coupon = form.save(commit=False)
            # try:
                coupon = CouponCustomer.objects.get(code=coupon.code, user=self.request.user)
                if coupon.used is True:
                    messages.success(self.request, f'Code Already Used!')
                    context = {
                        'object': order,
                        'form': form,
                        'prescription_form': prescription_form
                    }
                    return render(self.request, 'store/cart.html', context)
                else:
                    coupon.discount_amount = 0
                    coupon.order_amount = order.get_total_without_coupoun()
                    coupon.save()
                    vendor_coupon = Coupon.objects.get(code=coupon.code)
                    if coupon.order_amount >= vendor_coupon.minimum_order_amount:
                        coupon.discount_amount = coupon.order_amount * (vendor_coupon.discount_percent / 100)
                        coupon.applicable = True
                        coupon.save()
                        context = {
                            'object': order,
                            'form': form,
                            'prescription_form': prescription_form
                        }
                        return render(self.request, 'store/cart.html', context)

            # except:
            #     coupon.user = self.request.user
            #     coupon.save()
            #     vendor_coupon = Coupon.objects.get(code=coupon.code)
            #     coupon.coupon = vendor_coupon
            #     coupon.discount_amount = 0
            #     coupon.order_amount = order.get_total_without_coupoun()
            #     coupon.save()
            #     if coupon.order_amount >= vendor_coupon.minimum_order_amount:
            #         coupon.discount_amount = coupon.order_amount * (vendor_coupon.discount_percent / 100)
            #         # coupon.used = True
            #         coupon.applicable = True
            #         coupon.save()
            #
            #     order.coupon_customer = coupon
            #     order.save()
            #     context = {
            #         'object': order,
            #         'form': form,
            #         'prescription_form': prescription_form
            #     }
            #     messages.success(self.request, f'Code Applied!')
            #     return render(self.request, 'store/cart.html', context)
            # finally:
            #     context = {
            #         'object': order,
            #         'form': form,
            #         'prescription_form': prescription_form
            #     }
            #     return render(self.request, 'store/cart.html', context)
        context = {
            'object': order,
            'form': form,
            'prescription_form': prescription_form,
        }
        return render(self.request, 'store/cart.html', context)


class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            user = User.objects.get(id=self.request.user.id)
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'object': order,
                'user': user,
            }
            return render(self.request, 'store/checkout.html', context)
        except ObjectDoesNotExist:
            messages.error(self.request, "You do not have any item in cart")
            return redirect("/")


@login_required
def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False,
    )
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__slug=item.slug).exists():
            if order_item.quantity >= order_item.item.total_stock:
                order_item.quantity = order_item.item.total_stock
            else:
                order_item.quantity += 1
                order_item.save()
                # m_order = MiniOrder.objects.filter(order_ref_number=order.order_ref_number)
                messages.info(request, "Item qty was updated.")
                return redirect("store:store-cart")
        else:
            order.items.add(order_item)
            # order_item.save()
            order.save()

            ordered_date = timezone.datetime.now().strftime('%Y-%m-%d')
            ordered_time = timezone.datetime.now().strftime('%H:%M:%S')

            m_order = MiniOrder.objects.create(
                ordered_date=ordered_date, ordered_time=ordered_time, vendor=item.vendors.first(), user=request.user,
                order_ref_number=order.order_ref_number, order_item=order_item)
            m_order.mini_order_ref_number = f"MORN-{100000 + int(m_order.id)}"
            m_order.save()

            order.mini_order.add(m_order)
            order.save()

    else:
        ordered_date = timezone.datetime.now().strftime('%Y-%m-%d')
        ordered_time = timezone.datetime.now().strftime('%H:%M:%S')
        order = Order.objects.create(
            user=request.user, ordered_date=ordered_date, ordered_time=ordered_time)  # vendor=item.sold_by
        ORN = f"ORN-{100000 + int(order.id)}"
        order.order_ref_number = ORN
        order.items.add(order_item)
        # order_item.save()
        order.save()

        m_order = MiniOrder.objects.create(
            ordered_date=ordered_date, ordered_time=ordered_time, vendor=item.vendors.first(), user=request.user,
            order_ref_number=ORN, order_item=order_item)
        m_order.mini_order_ref_number = f"MORN-{100000 + int(m_order.id)}"
        m_order.save()

        order.mini_order.add(m_order)
        order.save()

        messages.info(request, "Item was added to your cart.")
    return redirect('store:store-product', slug=item.id)

#  return redirect("store:store-cart")


@login_required
def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            order_item.quantity = 1
            order_item.save()
            order.items.remove(order_item)
            try:
                mini_order = MiniOrder.objects.filter(order_item=order_item, ordered=False)
                mini_order.delete()
            except ObjectDoesNotExist:
                pass
            messages.info(request, "Item was removed from your cart.")
            return redirect("store:store-cart")
        else:
            # add a message saying the user dosent have an order
            messages.info(request, "Item was not in your cart.")
            return redirect("store:store-cart", slug=slug)
    else:

        # add a message saying the user dosent have an order
        messages.info(request, "You don't have an active order.")
        return redirect("store:store-cart", slug=slug)


@login_required
def remove_single_item_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.items.remove(order_item)
                try:
                    mini_order = MiniOrder.objects.get(order_item=order_item, ordered=False)
                    mini_order.delete()
                except ObjectDoesNotExist:
                    pass
            messages.info(request, "This item quantity was updated.")
            return redirect("store:store-cart")
        else:
            # add a message saying the user dosent have an order
            messages.info(request, "Item was not in your cart.")
            return redirect("store:store-cart", slug=slug)
    else:
        # add a message saying the user dosent have an order
        messages.info(request, "You don't have an active order.")
        return redirect("store:store-cart", slug=slug)


@login_required
def favorites(request):
    try:
        user = User.objects.get(id=request.user.id)
        order = FavoriteItem.objects.filter(user=request.user, ordered=False)
        context = {
            'item': order,
            'user': user,
        }
        return render(request, 'store/favorites.html', context)
    except ObjectDoesNotExist:
        messages.error(request, "You do not have any item in favorite")
        return redirect("/")


@login_required
def add_to_favorite(request, slug):

    item = get_object_or_404(Item, slug=slug)

    fav_item, created = FavoriteItem.objects.get_or_create(item=item,
                                                           user=request.user,
                                                           ordered=False
                                                           )
    if not fav_item.is_fav:
        fav_item.is_fav = True
        fav_item.save()
        messages.info(request, "Item was added to your Favorite.")
        return redirect("store:store-favorites")

    return redirect("store:store-favorites")


@login_required
def compare(request):
    try:
        user = User.objects.get(id=request.user.id)
        order = CompareItem.objects.filter(user=request.user, ordered=False)
        context = {
            'item': order,
            'user': user,
        }
        return render(request, 'store/compare.html', context)
    except ObjectDoesNotExist:
        messages.error(request, "You do not have any item in compare")
        return redirect("/")


@login_required
def add_to_compare(request, slug):

    item = get_object_or_404(Item, slug=slug)

    compare_item, created = CompareItem.objects.get_or_create(item=item,
                                                              user=request.user,
                                                              ordered=False
                                                              )
    if not compare_item.is_cmp:
        compare_item.is_cmp = True
        compare_item.save()
        messages.info(request, "Item was added to your Compare.")
        return redirect("store:store-compare")

    return redirect("store:store-compare")


# def create_ref_code():
#     return ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))


def is_valid_form(values):
    valid = True
    for field in values:
        if field == '':
            valid = False
    return valid


def checkout(request):
    customer_address_ = CustomerAddress.objects.filter(user=request.user)

    context = {
        'customer_address_': customer_address_
    }
    return render(request, 'store/checkout.html', context)


class PaymentView(View):
    def get(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        address = CustomerAddress.objects.get(id=kwargs['pk'])
        order.address = address
        order.save()
        if address:
            context = {
                'order': order,
                'DISPLAY_COUPON_FORM': False
            }
            userprofile = self.request.user.userprofile
            if userprofile.one_click_purchasing:
                # fetch the users card list
                cards = stripe.Customer.list_sources(
                    userprofile.stripe_customer_id,
                    limit=3,
                    object='card'
                )
                card_list = cards['data']
                if len(card_list) > 0:
                    # update the context with the default card
                    context.update({
                        'card': card_list[0]
                    })
            return render(self.request, "store/payment.html", context)
        else:
            messages.warning(
                self.request, "You have not added a billing address")
            return redirect("store:store-checkout")

    def post(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        form = PaymentForm(self.request.POST)
        userprofile = UserProfile.objects.get(user=self.request.user)
        if form.is_valid():
            token = form.cleaned_data.get('stripeToken')
            save = form.cleaned_data.get('save')
            use_default = form.cleaned_data.get('use_default')

            if save:
                if userprofile.stripe_customer_id != '' and userprofile.stripe_customer_id is not None:
                    customer = stripe.Customer.retrieve(
                        userprofile.stripe_customer_id)
                    customer.sources.create(source=token)

                else:
                    customer = stripe.Customer.create(
                        email=self.request.user.email,
                    )
                    customer.sources.create(source=token)
                    userprofile.stripe_customer_id = customer['id']
                    userprofile.one_click_purchasing = True
                    userprofile.save()

            amount = int(order.get_total() * 100)

            # try:

            if use_default or save:
                # charge the customer because we cannot charge the token more than once
                charge = stripe.Charge.create(
                    amount=amount,  # cents
                    currency="inr",
                    customer=userprofile.stripe_customer_id
                )
            else:
                # charge once off on the token
                charge = stripe.Charge.create(
                    amount=amount,  # cents
                    currency="inr",
                    source=token
                )

            # create the payment
            payment = Payment()
            payment.stripe_charge_id = charge['id']
            payment.user = self.request.user
            payment.amount = order.get_total()
            payment.save()

            order_items = order.items.all()

            for x in order_items:
                x.item.stock_no = int(x.item.stock_no) - x.quantity
                x.item.save()

            order.item_url = ''
            total_qty = 0
            for item in order_items:
                order.item_url = order.item_url + item.item.get_absolute_url() + '  *  ' + str(item.quantity) + '\n'
                total_qty += item.quantity
                item.save()

            ordered_date = timezone.datetime.now().strftime('%Y-%m-%d')
            ordered_time = timezone.datetime.now().strftime('%H:%M:%S')
            mini_order = order.mini_order.all()  #

            location_model = order.address.location
            latitude = location_model.location.y
            longitude = location_model.location.x
            user_location = Point(longitude, latitude, srid=4326)
            queryset = VendorLocation.objects.annotate(
                distance=Distance("location", user_location)
            ).order_by("distance")[0:]

            for vendor_location in queryset:
                mini_order = MiniOrder.objects.filter(order_ref_number=order.order_ref_number, ordered=False)
                if mini_order:
                    vendor_address = VendorAddress.objects.get(location=vendor_location)

                    vendorr = Vendor.objects.get(address=vendor_address) # nearest vendor is this
                    items = vendorr.item_set.all()
                    # items = Item.objects.filter(vendors=vendorr)

                    for m_order in mini_order:
                        item_title = m_order.order_item.item.title
                        m_order.return_window = timezone.datetime.now() + timezone.timedelta(days=10)
                        m_order.save()
                        for item in items:
                            if item_title == item.title:
                                m_order.vendor = vendorr
                                m_order.ordered = True
                                m_order.save()
                                break

            order.ordered_date = ordered_date
            order.ordered_time = ordered_time

            order.total_items = total_qty
            order.payment = payment

            if order.coupon_customer:
                order.coupon_customer.used = True
                coupon_customer = CouponCustomer.objects.get(id=order.coupon_customer.id)
                coupon_customer.save()

            order_items.update(ordered=True)
            mini_order.update(ordered=True)  #

            order.ordered = True
            order.save()

            messages.success(self.request, "Your order was successful!")
            return redirect("users-order")
'''
            except stripe.error.CardError as e:
                body = e.json_body
                err = body.get('error', {})
                messages.warning(self.request, f"{err.get('message')}")
                return redirect("users-order")

            except stripe.error.RateLimitError as e:
                # Too many requests made to the API too quickly
                messages.warning(self.request, "Rate limit error")
                return redirect("users-order")

            except stripe.error.InvalidRequestError as e:
                # Invalid parameters were supplied to Stripe's API
                print(e)
                messages.warning(self.request, "Invalid parameters")
                return redirect("users-order")

            except stripe.error.AuthenticationError as e:
                # Authentication with Stripe's API failed
                # (maybe you changed API keys recently)
                messages.warning(self.request, "Not authenticated")
                return redirect("/")

            except stripe.error.APIConnectionError as e:
                # Network communication with Stripe failed
                messages.warning(self.request, "Network error")
                return redirect("users-order")

            except stripe.error.StripeError as e:
                # Display a very generic error to the user, and maybe send
                # yourself an email
                messages.warning(
                    self.request, "Something went wrong. You were not charged. Please try again.")
                return redirect("users-order")

            except Exception as e:
                # send an email to ourselves
                messages.warning(
                    self.request, "A serious error occurred. We have been notifed.")
                return redirect("users-order")

        messages.warning(self.request, "Invalid data received")
        return redirect("/payment/stripe/")
# '''


def home(request):
    trend_qs = Item.objects.filter(trending=True)
    brand = Brands.objects.all()
    categorys = Category.objects.all()
    slide = Slide.objects.all()
    context = {
        'trend': trend_qs,
        'title': 'Home',
        'brand': brand,
        'category': categorys,
        'slide': slide
    }
    return render(request, 'store/index.html', context)


@login_required
def review(request, pk):
    item = Item.objects.get(pk=pk)
    try:
        instance = Reviews.objects.get(user=request.user, item=item)
    except ObjectDoesNotExist:
        instance = None
    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=instance)

        if form.is_valid():
            revieww = form.save(commit=False)
            revieww.user = request.user
            revieww.item = item
            revieww.reviewed = True
            revieww.save()
            messages.success(request, f'Details Updated!')
            return redirect('/')
    else:
        form = ReviewForm(instance=instance)

    context = {
        'form': form
    }
    return render(request, 'store/form.html', context)


@login_required
def review_delete(request, pk):
    item = Item.objects.get(pk=pk)
    try:
        Reviews.objects.get(user=request.user, item=item).delete()
    except ObjectDoesNotExist:
        return redirect('/')
    return redirect('/')


@login_required
def product_refund(request, pk, status):
    m_order = MiniOrder.objects.get(pk=pk)
    if m_order.return_window >= timezone.now():
        if m_order.received:
            if status == 'cancel':
                m_order.return_requested = False
                m_order.return_status = 'Not as Describe'
                m_order.save()
                return HttpResponseRedirect("/")
            elif status == 'return':
                if request.method == 'POST':
                    form = ReturnForm(request.POST)

                    if form.is_valid():
                        returnn = form.save(commit=False)
                        returnn.user = request.user
                        returnn.mini_order = m_order
                        returnn.return_date = timezone.datetime.now()
                        returnn.save()

                        m_order.return_requested = True
                        m_order.return_status = 'Processing Return Request'
                        m_order.save()
                        messages.success(request, f'Request Initiated!')
                        return redirect('/')
                else:
                    form = ReturnForm()

                context = {
                    'form': form
                }
                return render(request, 'store/form.html', context)
        else:
            redirect("/")

    else:
        redirect("/")


@login_required
def product_canceled(request, pk):
    m_order = MiniOrder.objects.get(pk=pk)
    if m_order.return_window >= timezone.now():
        if request.method == 'POST':
            form = CancelForm(request.POST)

            if form.is_valid():
                cancel = form.save(commit=False)
                cancel.user = request.user
                cancel.mini_order = m_order
                cancel.cancel_date = timezone.datetime.now()
                cancel.save()

                m_order.cancel_requested = True
                m_order.cancel_status = 'Processing Cancel Request'
                m_order.save()
                messages.success(request, 'Request Initiated!')
                return redirect('/')
        else:
            form = CancelForm()

        context = {
            'form': form
        }
        return render(request, 'store/form.html', context)
    messages.info(request, 'Refund Window Closed!')
    return redirect('/')


@login_required
def prescription_upload(request):
    if request.method == 'POST':
        form = PrescriptionUploadForm(request.POST, request.FILES)

        if form.is_valid():
            prescription = form.save(commit=False)
            prescription.user = request.user
            prescription.save()

            messages.success(request, f'Prescription Uploaded!')
            return redirect('/')
    else:
        form = PrescriptionUploadForm()

    context = {
        'form': form
    }

    return render(request, 'store/form.html', context)


@login_required
def customer_address_add(request):
    if request.method == 'POST':
        form = CustomerAddressForm(request.POST)
        location_form = LocationForm(request.POST)

        if location_form.is_valid():
            location_form = location_form.save(commit=False)
            location_form.user = request.user
            try:
                locationn = CustomerLocation.objects.get(location=location_form.location)
            except :
                locationn = CustomerLocation.objects.filter(location=location_form.location).first()
            location_form.save()

        if form.is_valid():
            address_form = form.save(commit=False)
            if address_form.shipping_is_billing is True:
                address_form.user = request.user
                address_form.location = locationn
                address_form.billing_street_address = address_form.shipping_street_address
                address_form.billing_street_address_line_2 = address_form.shipping_street_address_line_2
                address_form.billing_city = address_form.shipping_city
                address_form.billing_phone_number = address_form.shipping_phone_number
                address_form.billing_postal_code = address_form.shipping_postal_code
            else:
                address_form.user = request.user
                address_form.location = locationn
            address_form.save()
            messages.success(request, f'Details Updated!')
            return redirect('/')
    else:
        form = CustomerAddressForm()
        location_form = LocationForm(request.POST)

    context = {
        'form': form,
        'location_form': location_form,
        'title': 'Address',
        'submit': 'Submit'
    }
    return render(request, 'store/location_form.html', context)


@login_required
def customer_address_update(request, pk):
    customer_addres = CustomerAddress.objects.get(id=pk)
    if request.method == 'POST':
        form = CustomerAddressForm(request.POST, instance=customer_addres)
        location_form = LocationForm(request.POST, instance=customer_addres.location)

        if location_form.is_valid():
            location_form = location_form.save(commit=False)
            locationn = CustomerLocation.objects.get(location=location_form.location)
            location_form.save()

        if form.is_valid():
            address_form = form.save(commit=False)
            address_form.user = request.user
            address_form.phone_number = request.user.phone_number
            address_form.location = locationn
            address_form.save()
            messages.success(request, f'Details Updated!')
            return redirect('/')
    else:
        form = CustomerAddressForm(instance=customer_addres)
        location_form = LocationForm(request.POST, instance=customer_addres.location)

    context = {
        'form': form,
        'location_form': location_form,
        'title': 'Address Update',
        'submit': 'Update'
    }
    return render(request, 'store/location_form.html', context)


def blog(request):
    return render(request, 'store/blog.html', {'title': 'Home'})


def contacts(request):
    return render(request, 'store/contacts.html', {'title': 'Home'})


def about(request):
    return render(request, 'store/about.html', {'title': 'Home'})


def brands(request):
    return render(request, 'store/brand.html', {'title': 'Home'})


def catalog(request):
    return render(request, 'store/catalog.html', {'title': 'Home'})


def category(request):
    return render(request, 'store/category.html', {'title': 'Home'})


def delivery(request):
    return render(request, 'store/delivery.html', {'title': 'Home'})


def faq(request):
    return render(request, 'store/faq.html', {'title': 'Home'})


def news(request):
    return render(request, 'store/news.html', {'title': 'Home'})


def settings(request):
    return render(request, 'store/settings.html', {'title': 'Home'})


# @login_required
# def product_promo_code(request, pk):
#     order = Order.objects.get(pk=pk)
#     if request.method == 'POST':
#         form = CouponCustomerForm(request.POST)
#
#         if form.is_valid():
#             coupon = form.save(commit=False)
#             try:
#                 coupon = CouponCustomer.objects.get(code=coupon.code, user=request.user)
#                 if coupon.used is True:
#                     messages.success(request, f'Code Already Used!')
#                 else:
#                     coupon.discount_amount = 0
#                     coupon.order_amount = order.get_total_without_coupoun()
#                     coupon.save()
#                     vendor_coupon = Coupon.objects.get(code=coupon.code)
#                     if coupon.order_amount >= vendor_coupon.minimum_order_amount:
#                         coupon.discount_amount = coupon.order_amount * (vendor_coupon.discount_percent / 100)
#                         coupon.applicable = True
#                         coupon.save()
#                 return redirect('store:store-cart')
#
#             except:
#                 coupon.user = request.user
#                 coupon.save()
#                 vendor_coupon = Coupon.objects.get(code=coupon.code)
#                 coupon.coupon = vendor_coupon
#                 coupon.discount_amount = 0
#                 coupon.order_amount = order.get_total_without_coupoun()
#                 coupon.save()
#                 if coupon.order_amount >= vendor_coupon.minimum_order_amount:
#                     coupon.discount_amount = coupon.order_amount * (vendor_coupon.discount_percent / 100)
#                     # coupon.used = True
#                     coupon.applicable = True
#                     coupon.save()
#
#                 order.coupon_customer = coupon
#                 order.save()
#                 messages.success(request, f'Code Applied!')
#                 return redirect('store:store-cart')
#     else:
#         form = CouponCustomerForm()
#
#     context = {
#         'form': form
#     }
#
#     return render(request, 'store/form.html', context)



# class CheckoutView(View):
#     def get(self, *args, **kwargs):
#         try:
#             order = Order.objects.get(user=self.request.user, ordered=False)
#             form = CheckoutForm()
#             location_form = LocationForm()
#             context = {
#                 'form': form,
#                 'couponform': CouponForm(),
#                 'location_form': location_form,
#                 'order': order,
#                 'DISPLAY_COUPON_FORM': True
#             }
#
#             shipping_address_qs = Addresss.objects.filter(
#                 user=self.request.user,
#                 address_type='S',
#                 default=True
#             )
#             if shipping_address_qs.exists():
#                 context.update(
#                     {'default_shipping_address': shipping_address_qs[0],
#                      'shipping_address_qs': shipping_address_qs
#                      })
#
#             billing_address_qs = Addresss.objects.filter(
#                 user=self.request.user,
#                 address_type='B',
#                 default=True
#             )
#             if billing_address_qs.exists():
#                 context.update(
#                     {'default_billing_address': billing_address_qs[0]})
#
#             return render(self.request, "store/checkout.html", context)
#         except ObjectDoesNotExist:
#             messages.info(self.request, "You do not have an active order")
#             return redirect("store:checkout")
#
#     def post(self, *args, **kwargs):
#         form = CheckoutForm(self.request.POST or None)
#         location_form = LocationForm(self.request.POST or None)
#         try:
#             order = Order.objects.get(user=self.request.user, ordered=False)
#             if location_form.is_valid():
#                 try:
#                     location_point = CustomerLocation.objects.get(order_ref_number=order.order_ref_number)
#                 except ObjectDoesNotExist:
#                     location_point = location_form.save(commit=False)
#                     location_point.order_ref_number = order.order_ref_number
#                     location_point.save()
#                     location_point = CustomerLocation.objects.get(order_ref_number=order.order_ref_number)
#             if form.is_valid():
#
#                 use_default_shipping = form.cleaned_data.get(
#                     'use_default_shipping')
#                 if use_default_shipping:
#                     address_qs = Addresss.objects.filter(
#                         user=self.request.user,
#                         address_type='S',
#                         default=True
#                     )
#                     if address_qs.exists():
#                         shipping_address = address_qs[0]
#                         order.shipping_address = shipping_address
#                         order.save()
#                     else:
#                         messages.info(
#                             self.request, "No default shipping address available")
#                         return redirect('store:checkout')
#                 else:
#                     shipping_address1 = form.cleaned_data.get(
#                         'shipping_address')
#                     shipping_address2 = form.cleaned_data.get(
#                         'shipping_address2')
#                     shipping_city = form.cleaned_data.get(
#                         'shipping_city')
#                     shipping_postal_code = form.cleaned_data.get('shipping_postal_code')
#
#                     shipping_phone_number = form.cleaned_data.get('shipping_phone_number')
#
#                     if is_valid_form([shipping_address1, shipping_city, shipping_postal_code, shipping_phone_number]):
#                         shipping_address = Addresss(
#                             user=self.request.user,
#                             street_address=shipping_address1,
#                             apartment_address=shipping_address2,
#                             city=shipping_city,
#                             postal_code=shipping_postal_code,
#                             phone_number=shipping_phone_number,
#                             location=location_point,
#                             address_type='S'
#                         )
#                         shipping_address.save()
#
#                         order.shipping_address = shipping_address
#                         order.save()
#
#                         set_default_shipping = form.cleaned_data.get(
#                             'set_default_shipping')
#                         if set_default_shipping:
#                             shipping_address.default = True
#                             shipping_address.save()
#
#                     else:
#                         messages.info(
#                             self.request, "Please fill in the required shipping address fields")
#
#                 use_default_billing = form.cleaned_data.get(
#                     'use_default_billing')
#                 same_billing_address = form.cleaned_data.get(
#                     'same_billing_address')
#
#                 if same_billing_address:
#                     billing_address = shipping_address
#                     billing_address.pk = None
#                     billing_address.save()
#                     billing_address.address_type = 'B'
#                     billing_address.save()
#                     order.billing_address = billing_address
#                     order.save()
#
#                 elif use_default_billing:
#                     address_qs = Addresss.objects.filter(
#                         user=self.request.user,
#                         address_type='B',
#                         default=True
#                     )
#                     if address_qs.exists():
#                         billing_address = address_qs[0]
#                         order.billing_address = billing_address
#                         order.save()
#                     else:
#                         messages.info(
#                             self.request, "No default billing address available")
#                         return redirect('store:checkout')
#                 else:
#                     billing_address1 = form.cleaned_data.get(
#                         'billing_address')
#                     billing_address2 = form.cleaned_data.get(
#                         'billing_address2')
#                     billing_city = form.cleaned_data.get(
#                         'billing_city')
#                     billing_postal_code = form.cleaned_data.get('billing_postal_code')
#
#                     billing_phone_number = form.cleaned_data.get('billing_phone_number')
#
#                     if is_valid_form([billing_address1, billing_city, billing_postal_code, billing_phone_number]):
#                         billing_address = Addresss(
#                             user=self.request.user,
#                             street_address=billing_address1,
#                             apartment_address=billing_address2,
#                             city=billing_city,
#                             postal_code=billing_postal_code,
#                             phone_number=billing_phone_number,
#                             address_type='B'
#                         )
#                         billing_address.save()
#
#                         order.billing_address = billing_address
#                         order.save()
#
#                         set_default_billing = form.cleaned_data.get(
#                             'set_default_billing')
#                         if set_default_billing:
#                             billing_address.default = True
#                             billing_address.save()
#
#                     else:
#                         messages.info(
#                             self.request, "Please fill in the required billing address fields")
#
#                 payment_option = form.cleaned_data.get('payment_option')
#
#                 if payment_option == 'S':
#                     return redirect('store:store-payment', payment_option='stripe')
#                 elif payment_option == 'P':
#                     return redirect('store:store-payment', payment_option='paypal')
#                 else:
#                     messages.warning(
#                         self.request, "Invalid payment option selected")
#                     return redirect('store:store-checkout')
#         except ObjectDoesNotExist:
#             messages.warning(self.request, "You do not have an active order")
#             return redirect("store:order-summary")














