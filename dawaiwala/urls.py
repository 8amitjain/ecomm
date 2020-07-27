from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('frontend/', include('frontend.urls')),
    path('users/', include('users.urls')),
    path('vendors/', include('vendors.urls')),
    path('api/', include('rest_api.urls')),
    path('', include('store.urls')),
]

