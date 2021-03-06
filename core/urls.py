from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
path('', views.home, name = "home"),
path('home/', views.home, name = "home"),
path('product/<int:pk>/', views.product, name = 'product'),
path('cart-action', views.cart_action, name = 'cart-action'),
path('delete-item-from-cart', views.delete_item_from_cart, name = 'delete-item-from-cart'),
path('order-summary', views.order_summary, name = 'order_summary'),
path('order-history', views.order_history, name = 'order_history'),
path('order-details/<int:pk>/', views.order_details, name = 'order_details'),
path('checkout/', views.checkout, name = 'checkout'),
path('add_coupon/', views.add_coupon, name = 'add_coupon'),
path('payment/', views.payment, name = 'payment'),
path('register/', views.register, name = 'register')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
