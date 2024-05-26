from django.contrib import admin, messages
from django.db.models.query import QuerySet
from .models import Product


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
