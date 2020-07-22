from django.urls import path
from django.conf.urls.static import static
from django.conf import settings

from. import views
app_name = 'store'

urlpatterns = [
    path('', views.home, name='store'),
    # path('about/', views.about, name='store-about'),
    path('blog/', views.blog, name='store-blog'),
    path('brands/', views.brands, name='store-brands'),
    path('catalog/', views.catalog, name='store-catalog'),
    path('category/', views.category, name='store-category'),
    path('contacts/', views.contacts, name='store-contacts'),
    path('delivery/', views.delivery, name='store-delivery'),
    path('news/', views.news, name='store-news'),
    path('faq/', views.faq, name='store-faq'),
    path('settings/', views.settings, name='store-settings'),


    path('payment/<payment_option>/', views.PaymentView.as_view(), name='store-payment'),
    path('add-to-compare/<slug>/', views.add_to_compare, name='add-to-compare'),
    path('compare/', views.compare, name='store-compare'),
    path('product/<int:pk>/', views.product, name='store-product'),
    path('product/<slug>/', views.product, name='store-product'),
    path('add-to-favorite/<slug>/', views.add_to_favorite, name='add-to-favorite'),
    path('favorites/', views.favorites, name='store-favorites'),
    path('checkout/', views.CheckoutView.as_view(), name='store-checkout'),
    path('cart/', views.CartView.as_view(), name='store-cart'),
    path('subcategory/', views.shop_view, name='store-subcategory'),

    path('add-to-cart/<slug>/', views.add_to_cart, name='add-to-cart'),
    path('remove-from-cart/<slug>/', views.remove_from_cart, name='remove-from-cart'),
    path('remove-single-item-from-cart/<slug>/', views.remove_single_item_from_cart, name='remove-single-item-from-cart'),
    path('order-summary/', views.OrderSummaryNewView.as_view(), name='order-summary'),
    path('category/<slug>/', views.category_view, name='store-category'),
    path('review/<int:pk>/', views.review, name='store-review'),
    path('product/return/<str:status>/<int:pk>/', views.product_refund, name='store-product-return'),




]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)