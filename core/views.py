from django.shortcuts import render

def home(request):
    return render(request, "home-page.html", {})

def product(request):
    return render(request, "product-page.html", {})

def checkout(request):
    return render(request, "checkout-page.html", {})
