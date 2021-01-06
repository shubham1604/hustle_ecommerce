from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
path('', views.home, name = "home"),
path('home/', views.home, name = "home"),
path('product/<int:pk>/', views.product, name = 'product'),
path('add-to-cart', views.cart_action, name = 'cart-action'),
path('checkout/', views.checkout, name = 'checkout')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
