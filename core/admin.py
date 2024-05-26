from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from .models import User
from tags.models import TaggedItem
from store.admin import ProductAdmin
from store.models import Product


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['id', 'first_name', 'last_name',
                    'username', 'email', 'is_staff',
                    'date_joined']

    list_filter = ['is_staff']
    list_per_page = 20


class TagInline(GenericTabularInline):
    model = TaggedItem
    autocomplete_fields = ['tag']
    extra = 0


class CustomProductAdmin(ProductAdmin):
    inlines = [TagInline]


admin.site.unregister(Product)
admin.site.register(Product, CustomProductAdmin)
