from django.urls import path
from django.conf.urls.static import static
from django.conf import settings

from . import views

urlpatterns = [
    path('sales/', views.sales, name='vendors-sales'),

    path('products/', views.products_display, name='vendors-products'),
    path('products/add/', views.item_add, name='vendors-products-add'),
    path('products/add/<str:var_id>', views.varient_item_add, name='vendors-products-add-varient'),

    path('products/ordered/', views.products_ordered, name='vendors-products-ordered'),
    path('products/ordered/update/<int:pk>/', views.products_ordered_update, name='vendors-products-ordered-update'),

    path('category/', views.category_display, name='vendors-category'),
    path('category/add/', views.category_add, name='vendors-category-add'),

    path('brand/add/', views.brand_add, name='vendors-brand-add'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
