from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings
from uuid import uuid4
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


class Customer(models.Model):
    MEMBERSHIP_BRONZE = 'B'
    MEMBERSHIP_SILVER = 'S'
    MEMBERSHIP_GOLD = 'G'

    MEMBERSHIP_CHOICES = [
        (MEMBERSHIP_BRONZE, 'Bronze'),
        (MEMBERSHIP_SILVER, 'Silver'),
        (MEMBERSHIP_GOLD, 'Gold')
    ]

    phone = models.CharField(max_length=255)
    birthdate = models.DateField(null=True)
    membership = models.CharField(
        max_length=1, default=MEMBERSHIP_BRONZE, choices=MEMBERSHIP_CHOICES)

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)


class Order(models.Model):
    PAYMENT_PENDING = 'P'
    PAYMENT_FAILED = 'F'
    PAYMENT_COMPLETE = 'C'

    PAYMENT_STATUS_CHOICES = [
        (PAYMENT_PENDING, 'Pending'),
        (PAYMENT_FAILED, 'Failed'),
        (PAYMENT_COMPLETE, 'Complete')
    ]
    payment_status = models.CharField(
        max_length=1, default='P', choices=PAYMENT_STATUS_CHOICES)
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.PROTECT)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(
        max_digits=6, decimal_places=2, validators=[MinValueValidator(Decimal(1))])


class Cart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4)
    created_at = models.DateTimeField(auto_now_add=True)


class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart, on_delete=models.PROTECT, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.IntegerField(validators=[MinValueValidator(1)])

    class Meta:
        unique_together = [['product', 'cart']]


class Review(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
