from django.db import models
from brands.models import Brand
from annoying.fields import JSONField

class Mblog(models.Model):
    type = models.CharField(max_length = 50)
    uid = models.CharField(max_length = 100)
    brand = models.ForeignKey(Brand, related_name="mblogs")

class Token(models.Model):
    type = models.CharField(max_length = 50)
    token = JSONField()