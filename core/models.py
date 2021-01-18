from django.db import models
from django.conf import settings
from django_countries.fields import CountryField


# Create your models here.

ADDRESS_TYPE = (
('S', 'SHIPPING ADDRESS'),
('B', 'BILLING ADDRESS')
)

class Categories(models.Model):
    category_name = models.CharField(max_length = 50, unique = True)

    def __str__(self):
        return self.category_name


class Product(models.Model):
    product_title = models.CharField(max_length=100)
    price = models.FloatField()
    descr = models.TextField()
    product_category = models.ForeignKey(Categories,null=True, on_delete = models.SET_NULL)
    image = models.ImageField(null=True,upload_to = "product_images")
    discount_price = models.FloatField(null=True, blank=True)
    quantity_available = models.PositiveIntegerField(default = 0)


    def __str__(self):
        return self.product_title

class OrderStatusMaster(models.Model):
    status = models.CharField(max_length = 20)


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL ,on_delete = models.CASCADE)
    order_status = models.ForeignKey(OrderStatusMaster, null=True ,on_delete = models.SET_NULL)
    placed = models.BooleanField(default = False)
    started_on = models.DateTimeField(auto_now_add = True)
    placed_on = models.DateTimeField(null=True)
    payment = models.ForeignKey('Payment', on_delete= models.SET_NULL, null=True, blank=True)
    shipping_address = models.ForeignKey('Address',related_name = "shipping_address",on_delete = models.SET_NULL, null= True, blank=True)
    billing_address = models.ForeignKey('Address', related_name = "billing_address" ,on_delete = models.SET_NULL, null= True, blank=True)
    coupon = models.ForeignKey('Coupon', on_delete = models.SET_NULL, blank=True, null=True)
    price = models.FloatField(null=True ,default = None)

    def order_price(self):
        items = self.orderproduct_set.all()

        total = 0
        for item in items:
            total += item.get_item_price()

        total -= self.coupon.amount if self.coupon else 0
        return total



class OrderProduct(models.Model):

    order = models.ForeignKey(Order, on_delete = models.CASCADE)
    product = models.ForeignKey(Product, on_delete = models.DO_NOTHING)
    quantity_ordered = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity_ordered} of {self.product.product_title}"

    def get_item_price(self):
        item_price = self.product.discount_price if self.product.discount_price else self.product.price
        return item_price*self.quantity_ordered

    def get_money_saved(self):
        return self.quantity_ordered*(self.product.price - self.product.discount_price)


class Payment(models.Model):

    stripe_charge_id = models.CharField(max_length=50)
    timestamp = models.DateTimeField(auto_now_add = True)
    amount = models.FloatField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL ,on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username


class Address(models.Model):

    house_no = models.TextField()
    street = models.TextField()
    country = CountryField()
    zip = models.PositiveIntegerField()
    default = models.BooleanField(null=True)
    type = models.CharField(max_length=20,choices = ADDRESS_TYPE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username


class Coupon(models.Model):

    code = models.CharField(max_length = 15, unique=True)
    amount = models.FloatField()
    created_on = models.DateTimeField(auto_now_add=True)
    expiry_date = models.DateTimeField()
    discount_percentage = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return self.code
