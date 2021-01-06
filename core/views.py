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

def cart_action(request):
    data = request.POST or None
    if data:
        if 'add_to_cart' in request.POST:
            form = OrderProductForm(request.POST)
            if form.is_bound and form.is_valid():
                with transaction.atomic() as txn:
                    order, created = Order.objects.get_or_create(placed=False, user_id = request.user.id)
                    order_product_qs = OrderProduct.objects.filter(order = order)
                    if order_product_qs.exists():
                        order_product_qs = order_product_qs.filter(product_id = form.cleaned_data.get('product'))
                        if order_product_qs.exists():
                            order_product_ob = order_product_qs[0]
                            quantity = form.cleaned_data.get('quantity_ordered')
                            order_product_ob.quantity_ordered = quantity
                        else:
                            order_product_ob = form.save(commit=False)
                            order_product_ob.order = order
                        order_product_ob.save()


                    else:
                        order_product_ob = form.save(commit=False)
                        order_product_ob.order_id = order.pk
                        order_product_ob.save()
        elif 'remove_from_cart' in request.POST:
            form = OrderProductForm(request.POST)
            if form.is_bound and form.is_valid():
                order = Order.objects.filter(placed = False, user_id = request.user.id)
                product_to_remove = form.cleaned_data.get('product')

                if order.exists():
                    order = order[0]
                    order_products_qs = order.orderproduct_set.all()
                    if order_products_qs.exists():
                        if product_to_remove.id in order_products_qs.values_list('product', flat = True):
                            order_products_qs.filter(product = product_to_remove).delete()

    pid = request.POST.get('product')
    return redirect(reverse('product', kwargs={'pk':pid}))




def checkout(request):
    return render(request, "checkout-page.html", {})
