from django.contrib import admin
from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['id', 'first_name', 'last_name',
                    'username', 'email', 'is_staff',
                    'date_joined']

    list_filter = ['is_staff']
    list_per_page = 20
