from django.conf import settings
from django.contrib.auth import login
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.dispatch import receiver
from django_rest_passwordreset.signals import reset_password_token_created
from django.urls import reverse
import jwt
from knox.models import AuthToken
from knox.views import LoginView as KnoxLoginView
from rest_framework.views import APIView
from rest_framework import authentication, generics, permissions, status
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from users.models import User
from .utils import Util
from .serializers import UserSerializer, CustomerRegisterSerializer, ChangePasswordSerializer, VendorRegisterSerializer


# Users
class ListUsers(APIView):
    # authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.AllowAny]

    def get(self, request, format=None):
        """
        Return a list of all users.
        """
        usernames = [user.username for user in User.objects.all()]
        return Response(usernames)


# Customer Register API
class CustomerRegisterAPI(generics.GenericAPIView):
    serializer_class = CustomerRegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        # print(user)
        # user_obj = User.objects.get(username=user['username'])

        token = RefreshToken.for_user(user).access_token

        current_site = get_current_site(request)
        relative_link = reverse('login-verify-email')
        absolute_url = 'http://' + str(current_site) + relative_link + '?token=' + str(token)
        email_body = f"Hi {user.first_name} user the link below to active your account \n {absolute_url}"

        data = {'to_email': user.email, 'email_subject': 'Verify your email', 'email_body': email_body}
        Util.send_email(data)

        return Response({
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            "token": AuthToken.objects.create(user)[1]
        })


# Vendor Register API
class VendorRegisterAPI(generics.GenericAPIView):
    serializer_class = VendorRegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        # print(user)
        # user_obj = User.objects.get(username=user['username'])

        token = RefreshToken.for_user(user).access_token

        current_site = get_current_site(request)
        relative_link = reverse('login-verify-email')
        absolute_url = 'http://' + str(current_site) + relative_link + '?token=' + str(token)
        email_body = f"Hi {user.first_name} click the link below to active your Vendor account \n {absolute_url}"

        data = {'to_email': user.email, 'email_subject': 'Verify your email', 'email_body': email_body}
        Util.send_email(data)

        return Response({
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            "token": AuthToken.objects.create(user)[1]
        })


class VerifyUserEmail(generics.GenericAPIView):
    def get(self, request):
        token = request.GET.get('token')
        try:
            payload = jwt.decode(token, settings.SECRET_KEY)
            user = User.objects.get(id=payload['user_id'])
            print(user)
            print(user.is_verified)
            if not user.is_verified:
                user.is_verified = True
                user.save()

            response = {
                'status': 'Success',
                'code': status.HTTP_200_OK,
                'message': 'Email Verified',
            }
        except jwt.ExpiredSignatureError as identifer:

            response = {
                'status': 'Fail',
                'code': status.HTTP_400_BAD_REQUEST,
                'message': 'Activation Link Expired',
            }
        except jwt.exceptions.DecodeError as identifer:
            response = {
                'status': 'Fail',
                'code': status.HTTP_400_BAD_REQUEST,
                'message': 'Invalid Token',
            }

        return Response(response)


class LoginAPI(KnoxLoginView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        serializer = AuthTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        if not user.is_verified:
            token = RefreshToken.for_user(user).access_token

            current_site = get_current_site(request)
            relative_link = reverse('login-verify-email')
            absolute_url = 'http://' + str(current_site) + relative_link + '?token=' + str(token)
            email_body = f"Hi {user.first_name} user the link below to active your account \n {absolute_url}"

            data = {'to_email': user.email, 'email_subject': 'Verify your email', 'email_body': email_body}
            Util.send_email(data)
            response = {
                'status': 'Fail',
                'code': status.HTTP_400_BAD_REQUEST,
                'message': 'User Not verified',
            }

            return Response(response)
        else:
            login(request, user)
            return super(LoginAPI, self).post(request, format=None)


class ChangePasswordView(generics.UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    model = User
    permission_classes = (IsAuthenticated,)

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj

    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            # Check old password
            if not self.object.check_password(serializer.data.get("old_password")):
                return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)
            # set_password also hashes the password that the user will get
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
            response = {
                'status': 'success',
                'code': status.HTTP_200_OK,
                'message': 'Password updated successfully',
                'data': []
            }

            return Response(response)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):

    email_plaintext_message = "{}?token={}".format(reverse('password_reset:reset-password-request'),
                                                   reset_password_token.key)

    send_mail(
        # title:
        "Password Reset for {title}".format(title="Some website title"),
        # message:
        email_plaintext_message,
        # from:
        "visionboard.help@gmail.com",
        # to:
        [reset_password_token.user.email]
    )
