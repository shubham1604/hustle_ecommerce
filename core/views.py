from django.shortcuts import render
from .models import Categories, Products
from django.core.paginator import Paginator

def home(request):
    context = {}
    categories = Categories.objects.all()[:7]
    products = Products.objects.all()

    #paginator code starts
    paginator = Paginator(products,9)
    page = request.GET.get('page',1)
    products = paginator.get_page(page)
    #paginator code ends

    context.update({'categories':categories, 'products':products})
    return render(request, "home-page.html", context)

def product(request):
    return render(request, "product-page.html", {})

def checkout(request):
    return render(request, "checkout-page.html", {})
