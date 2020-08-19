from django.views import View
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.core.exceptions import ObjectDoesNotExist

from django.core.mail import EmailMessage
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_text
from .utils import account_activation_token
from django.urls import reverse

from store.models import Order, MiniOrder, CustomerAddress
from .models import User
from .forms import UserUpdateForm, CustomerRegistrationForm, VendorRegistrationForm, CustomerUpdateForm
from vendors.forms import VendorAddressForm, LocationForm
from vendors.models import VendorLocation


def register_user(request, data):
    req_form = CustomerRegistrationForm
    if data == "vendor":
        req_form = VendorRegistrationForm

    context = {}
    if request.POST:
        form = req_form(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            phone_number = form.cleaned_data.get('phone_number ')
            # account = authenticate(username=username, phone_number=phone_number, password=password)

            current_site = get_current_site(request)
            user = User.objects.get(username=username)
            email_body = {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            }

            link = reverse('activate', kwargs={
                'uidb64': email_body['uid'], 'token': email_body['token']})

            activate_url = 'http://' + current_site.domain + link

            email_subject = 'Welcome to Dawaiwala'
            email_body = 'Hi '+user.username + ', Please click the link and login to active your account. \n\n'+activate_url

            email = EmailMessage(
                email_subject,
                email_body,
                settings.AUTH_USER_MODEL,
                [username],
            )
            email.send(fail_silently=False)
            messages.success(request, 'Account successfully created Please click the link in your mail  and login to active your account. ')
            # login(request, account)
            return redirect('store:store')
        else:
            context['register_form'] = form

    else:
        form = req_form()
        context['register_form'] = form
    return render(request, 'users/register.html', context)


class VerificationView(View):
    def get(self, request, uidb64, token):
        try:
            id = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=id)

            if not account_activation_token.check_token(user, token):
                return redirect('users-login'+'?message='+'User already activated')

            if user.is_active:
                return redirect('users-login')
            user.is_active = True
            user.save()

            messages.success(request, 'Account activated successfully')
            return redirect('users-login')

        except Exception as ex:
            pass

        return redirect('users-login')


@login_required
def account_view(request, data):
    context = {}
    if data == "vendor":
        user_model = User.objects.get(id=request.user.id)
        req_form = CustomerUpdateForm
        instance_data = request.user.vendor

        if request.method == 'POST':
            form = req_form(request.POST, instance=instance_data)
            user_form = UserUpdateForm(request.POST, instance=request.user)

            vendor_address_form = VendorAddressForm(request.POST, instance=request.user.vendor.address)
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

            if vendor_address_form.is_valid():
                address_form = form.save(commit=False)
                address_form.user = request.user
                address_form.phone_number = request.user.phone_number
                address_form.location = location_point
                address_form.save()
                messages.success(request, f'Details Updated!')
                return redirect('/')

            if form.is_valid() and user_form.is_valid():
                form.save()
                user_form.save()
                messages.success(request, f'Details Updated!')
                return redirect('/')
        else:
            form = req_form(instance=instance_data)
            user_form = UserUpdateForm(instance=request.user)
            vendor_address_form = VendorAddressForm(instance=request.user.vendor.address)
            location_form = LocationForm()

        context['form'] = form
        context['vendor_address_form'] = vendor_address_form
        context['user'] = user_model
        context['user_form'] = user_form
        context['data'] = data
        context['location_form'] = location_form
        context['title'] = 'Vendor Address'
        context['submit'] = 'Submit'

    elif data == "customer":
        user_model = User.objects.get(id=request.user.id)
        req_form = CustomerUpdateForm
        instance_data = request.user.customer

        if request.method == 'POST':
            form = req_form(request.POST, instance=instance_data)
            user_form = UserUpdateForm(request.POST, instance=request.user)

            if form.is_valid() and user_form.is_valid():
                form.save()
                user_form.save()
                messages.success(request, f'Details Updated!')
                return redirect('/')
        else:
            form = req_form(instance=instance_data)
            user_form = UserUpdateForm(instance=request.user)

        address = CustomerAddress.objects.filter(user=request.user)

        context['form'] = form
        context['user_form'] = user_form
        context['data'] = data
        context['user'] = user_model
        context['customer_address'] = address
        context['title'] = 'Customer Address'
        context['submit'] = 'Submit'

    else:
        return render(request, '/')

    return render(request, 'users/personal.html', context)


@login_required
def order(request):
    order_model = Order.objects.filter(user=request.user)
    mini_order = MiniOrder.objects.filter(user=request.user)
    return render(request, 'users/order.html', {'order': order_model,
                                                'mini_order': mini_order})


@login_required
def order_detail(request, pk):
    context = {}
    orderr = Order.objects.get(id=pk)
    context['order'] = orderr
    return render(request, 'users/order_detail.html', context)


