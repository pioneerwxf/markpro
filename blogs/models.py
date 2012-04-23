from django.db import models
from brands.models import Brand

class Blog(models.Model):
    type = models.CharField(max_length = 50)
    url = models.URLField()
    brand = models.ForeignKey(Brand, related_name="blogs")