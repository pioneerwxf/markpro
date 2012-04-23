from django.db import models
from brands.models import Brand

class Store(models.Model):
    name = models.CharField(max_length = 100)
    type = models.CharField(max_length = 50)
    url = models.URLField()
    brand = models.ForeignKey(Brand, related_name = "stores")


class Product(models.Model):
    name = models.CharField(max_length = 100)
    url = models.URLField()
    store = models.ForeignKey(Store, related_name = "products")