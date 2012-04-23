from django.db import models

class Brand(models.Model):
    brand_name = models.CharField(max_length = 50)
    site_url = models.URLField(blank = True)


class RankKey(models.Model):
    keyword = models.CharField(max_length = 50)
    brand = models.ForeignKey(Brand, related_name="rank_keys")


class HotKey(models.Model):
    keyword = models.CharField(max_length = 50)
    brand = models.ForeignKey(Brand, related_name="hot_keys")