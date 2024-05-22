from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal


class Collection(models.Model):
    name = models.CharField(max_length=255)
    featured_product = models.ForeignKey(
        'Product', on_delete=models.SET_NULL, null=True, related_name='+')


class Product(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    slug = models.SlugField()
    unit_price = models.DecimalField(
        max_digits=6, decimal_places=2, validators=[MinValueValidator(Decimal(1))])
    quantity = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(10000)])
    collection = models.ForeignKey(Collection, on_delete=models.PROTECT)
    last_update = models.DateTimeField(auto_now=True)
