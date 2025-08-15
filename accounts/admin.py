from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from .models import User

@admin.register(User)
class UserAdmin(DefaultUserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'role', 'employee_id', 'is_staff']
    list_filter = ['role', 'is_staff', 'is_active', 'date_joined']
    search_fields = ['username', 'email', 'first_name', 'last_name', 'employee_id']
    
    fieldsets = DefaultUserAdmin.fieldsets + (
        ('Role Information', {'fields': ('role', 'phone', 'department', 'employee_id')}),
    )
    
    # Add role field to the user creation and editing forms
    fieldsets = DefaultUserAdmin.fieldsets + (
        ('Role Information', {'fields': ('role', 'phone', 'department', 'employee_id')}),
    )
