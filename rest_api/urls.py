from knox import views as knox_views
from django.urls import path, include

from .views import CustomerRegisterAPI, VendorRegisterAPI, LoginAPI, ChangePasswordView, VerifyUserEmail, ListUsers


urlpatterns = [
    # Users
    path('users/all/', ListUsers.as_view(), name='list-users'),

    # Register
    path('register/customer/', CustomerRegisterAPI.as_view(), name='register'),
    path('register/vendor/', VendorRegisterAPI.as_view(), name='register'),

    # Login
    path('login/', LoginAPI.as_view(), name='login'),
    path('login/verify/email/', VerifyUserEmail.as_view(), name='login-verify-email'),

    # Logout
    path('logout/', knox_views.LogoutView.as_view(), name='logout'),
    path('logoutall/', knox_views.LogoutAllView.as_view(), name='logoutall'),

    # Passwords
    path('password/change/', ChangePasswordView.as_view(), name='password-change'),
    path('password/reset/', include('django_rest_passwordreset.urls', namespace='password-reset')),



]
