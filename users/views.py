from django.views import View
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.core.mail import EmailMessage
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_text, DjangoUnicodeDecodeError
from .utils import account_activation_token
from django.urls import reverse

from store.models import Order, MiniOrder, CustomerAddress
from .models import User
from .forms import UserUpdateForm, CustomerRegistrationForm, VendorRegistrationForm, CustomerUpdateForm,\
                   VendorUpdateForm


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

    if data == "vendor":
        req_form = VendorUpdateForm
        instance_data = request.user.vendor
        customer_address = ''
    elif data == "customer":
        req_form = CustomerUpdateForm
        instance_data = request.user.customer
        customer_address = CustomerAddress.objects.filter(user=request.user)

    else:
        return render(request, '/')

    user_model = User.objects.get(id=request.user.id)

    if request.method == 'POST':
        form = req_form(request.POST, instance=instance_data)
        user_form = UserUpdateForm(request.POST, instance=request.user)

        if form.is_valid() and user_form.is_valid():  # and address_form.is_valid():
            form.save()
            user_form.save()
            # address_form.user_id = request.user.id
            # address_form.save()
            messages.success(request, f'Details Updated!')
            return redirect('/')
    else:
        form = req_form(instance=instance_data)
        user_form = UserUpdateForm(instance=request.user)
        # address_form = AddressForm(instance=request.user.address)

    context = {
        'form': form,
        'user_form': user_form,
        'data': data,
        'user': user_model,
        'customer_address': customer_address,
        # 'address_form': address_form,

    }
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


