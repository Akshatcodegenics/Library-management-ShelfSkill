from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('id', 'username', 'email', 'name', 'role', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_active')
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Custom Role Info', {'fields': ('role', 'name')}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Custom Role Info', {'fields': ('role', 'name', 'email')}),
    )
    search_fields = ('username', 'email', 'name')
    ordering = ('id',)
