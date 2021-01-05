from django.shortcuts import render, redirect
from django.urls import reverse
from .models import Categories, Product, Order, OrderProduct
from .forms.add_to_cart import OrderProductForm
from django.core.paginator import Paginator
from django.db import transaction

def home(request):
    context = {}
    categories = Categories.objects.all()[:7]
    products = Product.objects.all()

    #paginator code starts
    paginator = Paginator(products,9)
    page = request.GET.get('page',1)
    products = paginator.get_page(page)
    #paginator code ends

    context.update({'categories':categories, 'products':products})
    return render(request, "home-page.html", context)

def product(request, pk):
    context = {}
    try:
        product = Product.objects.get(pk = pk)
    except Product.DoesNotExist as e:
        return redirect(reverse('home'))

    context.update({'product':product})

    return render(request, "product-page.html", context)

def add_to_cart(request):
    data = request.POST or None
    if data:
        form = OrderProductForm(request.POST)
        if form.is_bound and form.is_valid():
            with transaction.atomic() as txn:
                order, created = Order.objects.get_or_create(placed=False, user_id = request.user.id)
                order_product_qs = OrderProduct.objects.filter(order = order)
                if order_product_qs.exists():
                    order_product_ob = order_product_qs[0]
                    quantity = form.cleaned_data.get('quantity_ordered')
                    order_product_ob.quantity_ordered = quantity
                    order_product_ob.save()
                else:
                    order_product_ob = form.save(commit=False)
                    order_product_ob.order_id = order.pk
                    order_product_ob.save()

    return redirect(reverse('product', kwargs={'pk':order_product_ob.product_id}))

def checkout(request):
    return render(request, "checkout-page.html", {})
