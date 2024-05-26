from typing import Any
from django.contrib import admin, messages
from django.db.models.aggregates import Count
from django.db.models.query import QuerySet
from django.http import HttpRequest
from .models import Product, Collection, Customer, Order


class InventoryFilter(admin.SimpleListFilter):
    title = 'inventory'
    parameter_name = 'quantity'

    def lookups(self, request, model_admin):
        return [
            ('<10', 'Low'),
            ('<50', 'Mid'),
            ('>50', 'Good')
        ]

    def queryset(self, request, queryset: QuerySet):
        if self.value() == '<10':
            return queryset.filter(quantity__lt=10)
        elif self.value() == '<50':
            return queryset.filter(quantity__gt=10).filter(quantity__lt=50)
        elif self.value() == '>50':
            return queryset.filter(quantity__gt=50)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['title', 'unit_price',
                    'quantity', 'inventory_status', 'collection']
    list_per_page = 20
    list_editable = ['unit_price']
    list_filter = ['collection', 'last_update', InventoryFilter]
    search_fields = ['title']
    actions = ['clear_inventory']
    autocomplete_fields = ['collection']
    prepopulated_fields = {
        'slug': ['title']
    }

    @admin.display(ordering='quantity')
    def inventory_status(self, product):
        if product.quantity < 10:
            return 'Low'
        elif product.quantity > 10 and product.quantity < 50:
            return 'Mid'
        return 'Good'

    @admin.action(description='Clear inventory')
    def clear_inventory(self, request, queryset: QuerySet):
        updated_count = queryset.update(quantity=0)
        self.message_user(
            request,
            f'{updated_count} products were successfully updated.',
            messages.SUCCESS
        )


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ['name', 'products_count']
    search_fields = ['name']

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return super().get_queryset(request).annotate(
            products_count=Count('product')
        )

    @admin.display(ordering='products_count')
    def products_count(self, collection):
        return collection.products_count


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name',
                    'membership', 'orders_count', 'phone', 'birthdate']
    list_filter = ['membership']
    search_fields = ['first_name__istartswith', 'last_name__istartswith']
    list_select_related = ['user']
    list_per_page = 20

    @admin.display(ordering='user__first_name')
    def first_name(self, customer):
        return customer.user.first_name

    @admin.display(ordering='user__last_name')
    def last_name(self, customer):
        return customer.user.last_name

    @admin.display(ordering='orders_count')
    def orders_count(self, customer):
        return customer.orders_count

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return super().get_queryset(request).annotate(
            orders_count=Count('order')
        )


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'payment_status', 'username', 'placed_at']
    list_select_related = ['customer__user']

    @admin.display()
    def username(self, order):
        return order.customer.user.username
