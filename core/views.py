from django.shortcuts import render, redirect
from django.urls import reverse
from .models import Categories, Product, Order, OrderProduct, Payment
from .forms.add_to_cart import OrderProductForm
from .forms.checkout_form import CheckoutForm
from django.core.paginator import Paginator
from django.db import transaction
from django.contrib import messages
from django.db.models import F
import stripe
from datetime import datetime

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
                        if order_product_qs.exists() and order_product_qs.count() == 1:
                            quantity = form.cleaned_data.get('quantity_ordered',1)
                            order_product_qs.update(quantity_ordered = F('quantity_ordered')+quantity)
                            order_product_ob = order_product_qs[0]
                            messages.info(request, "The quantity for this item was updated")
                        else:
                            order_product_ob = form.save(commit=False)
                            order_product_ob.order = order
                            messages.info(request, "This item was added to your cart")
                            order_product_ob.save()


                    else:
                        order_product_ob = form.save(commit=False)
                        order_product_ob.order_id = order.pk
                        order_product_ob.save()
                        messages.info(request, "This item was added to your cart")
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
                            order_products_qs.filter(product = product_to_remove).update(quantity_ordered=F('quantity_ordered')-1)
                            if order_products_qs[0].quantity_ordered == 0:
                                order_products_qs.filter(product = product_to_remove).delete()

                            messages.info(request, "The quantity for this item was updated")
                        else:
                            messages.info(request, "This item was not in your cart")
                    else:
                        messages.info(request, "Your cart was already empty")
                else:
                    messages.info(request, "You do not have an active order")

    pid = request.POST.get('product')
    return redirect(reverse('product', kwargs={'pk':pid}))


def delete_item_from_cart(request):
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
                    messages.info(request, "The item was deleted from our cart")
                else:
                    messages.info(request, "This item was not in your cart")
            else:
                messages.info(request, "Your cart was already empty")
        else:
            messages.info(request, "You do not have an active order")

    return redirect(reverse('order_summary'))

def order_summary(request):
    context = {}
    order_qs = Order.objects.filter(placed = False, user = request.user)
    # if order_qs.exists():
    order = order_qs[0] if order_qs.exists() else []
    context.update({'order':order})
    return render(request, "order-summary.html", context)


def checkout(request):
    context = {}
    order = Order.objects.filter(placed=False, user=request.user)[0]
    if request.method == 'POST':
        print(request.POST)
        form = CheckoutForm(request.POST)

        if form.is_valid():
            street_address1 = form.cleaned_data.get('street_address1')
            street_address2 = form.cleaned_data.get('street_address2')
            country = form.cleaned_data.get('country')
            zip = form.cleaned_data.get('zip')
            same_billing_address = form.cleaned_data.get('same_billing_address')
            save_info = form.cleaned_data.get('save_info')
            payment_option = form.cleaned_data.get('payment_option')

            if payment_option == 'S':
                return redirect(reverse('payment'))
            elif payment_option == 'P':
                return redirect(reverse('payment'))
            else:
                messages.info("wrong payment method selected")



        else:
            print("Invalid")

    else:

        form = CheckoutForm()
    print(order)
    print(order.orderproduct_set.all())
    context.update({'form':form, 'order':order})
    return render(request, "checkout-page.html", context)


def payment(request):
    context = {}
    if request.method == 'POST':
            try:
      # Use Stripe's library to make requests...
                with transaction.atomic() as txn:
                    order = Order.objects.filter(placed = False, user = request.user).first()
                    stripe.api_key = "sk_test_4eC39HqLyjWDarjtT1zdp7dc"
                    amount = int(order.order_price()*100)
                    charge = stripe.Charge.create(
                      amount=amount,
                      currency="usd",
                      source="tok_mastercard",
                      description="My First Test Charge (created for API docs)",
                    )


                    payment = Payment()
                    payment.stripe_charge_id = charge['id']
                    payment.amount = charge['amount']
                    payment.user = request.user
                    payment.save()

                    order.placed = True
                    order.placed_on = datetime.now()
                    order.payment = payment
                    order.save()

                    messages.info(request, "Your order was successfull")
                    return redirect('/')
            except stripe.error.CardError as e:
                messages.warning(request, "Xard Error")
            except stripe.error.RateLimitError as e:
                messages.warning(request, "Rate Limit Error")
            except stripe.error.InvalidRequestError as e:
                messages.warning(request, "Invalid Request Error")
                print(e)
            except stripe.error.AuthenticationError as e:
                messages.warning(request, "Authentication Error")
            except stripe.error.APIConnectionError as e:
                messages.warning(request, "API connection Error")
            except stripe.error.StripeError as e:
                messages.warning(request, "Something went wrong, you haven't been charged")
            except Exception as e:
                print(e)
                messages.warning(request, "This is a serious error. We have been notified. You have not been charged")

    else:
        print("157")
    return render(request,'payment.html',context)
