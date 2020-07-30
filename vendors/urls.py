from django.urls import path
from django.conf.urls.static import static
from django.conf import settings

from . import views

urlpatterns = [
    path('sales/', views.sales, name='vendors-sales'),

    path('products/', views.products_display, name='vendors-products'),
    path('products/add/', views.products_add, name='vendors-products-add'),
    path('products/add/<str:var_id>', views.product_varient_add, name='vendors-products-add-varient'),
    path('products/update/<int:pk>', views.products_update, name='vendors-products-update'),
    path('products/delete/<int:pk>', views.product_delete, name='vendors-products-delete'),

    path('product/<int:pk>/', views.product_sell, name='vendor-product-sell'),

    path('products/ordered/', views.products_ordered, name='vendors-products-ordered'),
    path('products/ordered/update/<int:pk>/', views.products_ordered_update, name='vendors-products-ordered-update'),

    path('products/returned/', views.products_returned, name='vendors-products-returned'),
    path('products/returned/update/<int:pk>/', views.products_returned_update, name='vendors-products-returned-update'),

    path('products/canceled/', views.products_canceled, name='vendors-products-canceled'),
    path('products/canceled/update/<int:pk>/', views.products_cancel_update, name='vendors-products-canceled-update'),


    path('category/', views.category_display, name='vendors-category'),
    path('category/add/', views.category_add, name='vendors-category-add'),

    path('brand/add/', views.brand_add, name='vendors-brand-add'),

    path('address/add/', views.vendor_address, name='vendors-address-add'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
