from django.shortcuts import render
from .models import Categories, Products

def home(request):
    context = {}
    categories = Categories.objects.all()[:7]
    products = Products.objects.all()
    context.update({'categories':categories, 'products':products})
    return render(request, "home-page.html", context)

def product(request):
    return render(request, "product-page.html", {})

def checkout(request):
    return render(request, "checkout-page.html", {})
