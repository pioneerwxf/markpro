from django.db import models
from brands.models import Brand, HotKey, RankKey
from blogs.models import Blog
from mblogs.models import Mblog
from stores.models import Store, Product
from annoying.fields import JSONField

class Result(models.Model):
    brand = models.ForeignKey(Brand, null = True, related_name = "results")
    hotkey = models.ForeignKey(HotKey, null = True, related_name = "results")
    rankkey = models.ForeignKey(RankKey, null = True, related_name = "results")
    blog = models.ForeignKey(Blog, null = True, related_name = "results")
    mblog = models.ForeignKey(Mblog, null = True, related_name = "results")
    store = models.ForeignKey(Store, null = True, related_name = "results")
    product = models.ForeignKey(Product, null = True, related_name = "results")
    update_time = models.DateTimeField(auto_now_add = True)
    result = JSONField()
