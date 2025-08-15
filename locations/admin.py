from django.contrib import admin
from .models import Location

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'city', 'country', 'responsible_person', 'is_active']
    list_filter = ['is_active', 'country', 'city']
    search_fields = ['name', 'code', 'city']
    list_editable = ['is_active']
    ordering = ['name']
