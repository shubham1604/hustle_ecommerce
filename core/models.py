from django.db import models

# Create your models here.

class Categories(models.Model):
    category_name = models.CharField(max_length = 50, unique = True)


class Product(models.Model):
    product_title = models.CharField(max_length=100)
    price = models.FloatField()
    descr = models.TextField()
    product_category = models.ForeignKey(Categories, on_delete=models.CASCADE)
