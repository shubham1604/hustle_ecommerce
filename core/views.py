from django.shortcuts import render, redirect
from django.urls import reverse
from .models import Categories, Product, Order, OrderProduct, Payment, Coupon, Address
from .forms.add_to_cart import OrderProductForm
from .forms.checkout_form import CheckoutForm
from .forms.coupon_form import CouponForm
from .forms.signup import SignUpForm
from django.core.paginator import Paginator
from django.db import transaction
from django.contrib import messages
from django.db.models import F
import stripe
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate


def is_valid_form(values):

    is_valid = True
    for value in values:
        if value == '':
            is_valid = False
            break

    return is_valid


def register(request):

    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            email = form.cleaned_data.get('email')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(email=email, password=raw_password)
            login(request, user)
            return redirect('home')
    else:
        form = SignUpForm()

    context = {}
    context.update({'form':form})
    return render(request, "registration/signup.html",context)

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

@login_required
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

    if not pid:
        return redirect(reverse('home'))
    return redirect(reverse('product', kwargs={'pk':pid}))

@login_required
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

@login_required
def order_summary(request):
    context = {}
    order_qs = Order.objects.filter(placed = False, user = request.user)
    # if order_qs.exists():
    order = order_qs[0] if order_qs.exists() else []
    context.update({'order':order})
    return render(request, "order-summary.html", context)

@login_required
def checkout(request):
    context = {}
    order = Order.objects.filter(placed=False, user=request.user)[0]
    shipping_address_qs = Address.objects.filter(user = request.user, default = True, type = 'S')
    if shipping_address_qs.exists():
        context.update({'default_shipping_address': shipping_address_qs[0]})

    billing_address_qs = Address.objects.filter(user = request.user, default = True, type = 'B')
    if billing_address_qs.exists():
        context.update({'default_billing_address': shipping_address_qs[0]})


    if request.method == 'POST':
        print(request.POST)
        form = CheckoutForm(request.POST)

        if form.is_valid():
            use_default_shipping = form.cleaned_data.get('use_default_shipping')
            if use_default_shipping:
                address_qs = Address.objects.filter(user = request.user, default = True, type = 'S')
                if address_qs.exists():
                    shipping_address = address_qs[0]
                else:
                    messages.info(request, "You have no default shipping address ")
            else:
                shipping_address1 = form.cleaned_data.get('shipping_address1')
                shipping_address2 = form.cleaned_data.get('shipping_address2')
                shipping_country = form.cleaned_data.get('shipping_country')
                shipping_zip = form.cleaned_data.get('shipping_zip')

                set_default_shipping = form.cleaned_data.get('set_default_shipping')

                if is_valid_form([shipping_address1, shipping_address2, shipping_zip]):
                    shipping_address = Address(
                    house_no = shipping_address2,
                    street = shipping_address1,
                    country = shipping_country,
                    zip = shipping_zip,
                    default = set_default_shipping,
                    type = "S",
                    user = request.user
                    )
                    shipping_address.save()
                else:
                    shipping_address = None
                    messages.info(request, "Please Add shipping address fields")


            same_billing_address = form.cleaned_data.get('same_billing_address')
            use_default_billing = form.cleaned_data.get('use_default_billing')

            if same_billing_address:
                billing_address = shipping_address
                billing_address.pk = None
                billing_address.type = "B"
                billing_address.save()
                order.address = billing_address
                order.save()

            elif use_default_billing:
                address_qs = Address.objects.filter(user = request.user, default = True, type = 'B')
                if address_qs.exists():
                    billing_address = address_qs[0]
                else:
                    messages.info(request, "You have no default billing address ")
            else:
                billing_address1 = form.cleaned_data.get('billing_address1')
                billing_address2 = form.cleaned_data.get('billing_address2')
                billing_country = form.cleaned_data.get('shipping_country')
                billing_zip = form.cleaned_data.get('billing_zip')

                set_default_billing = form.cleaned_data.get('set_default_billing')

                if is_valid_form([billing_address1, billing_address2, billing_zip]):
                    billing_address = Address(
                    house_no = billing_address2,
                    street = billing_address1,
                    country = billing_country,
                    zip = billing_zip,
                    default = set_default_billing,
                    type = "B",
                    user = request.user
                    )
                    billing_address.save()
                else:
                    billing_address = None
                    messages.info(request, "Please Add billing address fields")

            order.shipping_address = shipping_address
            order.billing_address = billing_address
            order.save()



            payment_option = form.cleaned_data.get('payment_option')

            if payment_option == 'S':
                return redirect(reverse('payment'))
            elif payment_option == 'P':
                return redirect(reverse('payment'))
            else:
                messages.info(request, "wrong payment method selected")
        else:
            print("Invalid")

    else:

        form = CheckoutForm()

    coupon_form = CouponForm()
    context.update({'form':form, 'order':order, 'coupon_form': coupon_form})
    return render(request, "checkout-page.html", context)

@login_required
def payment(request):
    context = {}
    order = Order.objects.filter(placed = False, user = request.user)[0]
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
                    order.price = order.order_price()
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
    context.update({'order':order, 'DISPLAY_COUPON_FORM':0})
    return render(request,'payment.html',context)

@login_required
def add_coupon(request):

    if request.method == "POST":
        form = CouponForm(request.POST)

        if form.is_valid():
            coupon       = form.cleaned_data.get('code')
            coupon_qs    = Coupon.objects.filter(code = coupon, expiry_date__gt=datetime.now())
            used_coupons = Order.objects.filter(user = request.user).values_list('coupon', flat=True)

            if coupon_qs.exists() and coupon not in used_coupons:
                order = Order.objects.filter(user = request.user, placed = False)
                order = order[0] if order.exists() else None
                if order:
                    order.coupon = coupon_qs.first()
                    order.save()
            else:
                messages.info(request, "Zyada Chalaak mat ban")
    else:
        form = CouponForm()
    return redirect(reverse('checkout'))

@login_required
def order_history(request):
    context = {}
    orders = Order.objects.filter(placed=True, user=request.user)
    context.update({'orders':orders})
    return render(request,"order-history.html",context)

@login_required
def order_details(request, pk):
    context = {}
    order = Order.objects.filter(pk = pk)
    if order.exists():
        order = order.first()
    else:
        messages.info(request, "The order doesn't exist")

    context.update({'order':order})
    return render(request,"order-detail.html", context)
