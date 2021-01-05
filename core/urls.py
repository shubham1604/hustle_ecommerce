from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
path('', views.home, name = "home"),
path('home/', views.home, name = "home"),
path('product/<int:pk>/', views.product, name = 'product'),
path('add-to-cart', views.add_to_cart, name = 'add-to-card'),
path('checkout/', views.checkout, name = 'checkout')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
