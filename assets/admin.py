from django.contrib import admin
from .models import Asset, AssetCategory, AssetRemark

@admin.register(AssetCategory)
class AssetCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name']

@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ['asset_id', 'name', 'category', 'status', 'current_location', 'responsible_person']
    list_filter = ['status', 'condition', 'category', 'current_location']
    search_fields = ['asset_id', 'name', 'serial_number']
    list_editable = ['status']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('asset_id', 'name', 'description', 'category')
        }),
        ('Physical Details', {
            'fields': ('serial_number', 'model_number', 'manufacturer', 'barcode', 'qr_code')
        }),
        ('Financial Information', {
            'fields': ('purchase_date', 'purchase_value', 'current_value', 'warranty_expiry')
        }),
        ('Status & Location', {
            'fields': ('status', 'condition', 'current_location', 'responsible_person')
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at', 'notes'),
            'classes': ('collapse',)
        })
    )

@admin.register(AssetRemark)
class AssetRemarkAdmin(admin.ModelAdmin):
    list_display = ['asset', 'category', 'remark', 'created_by', 'created_at', 'is_important']
    list_filter = ['category', 'is_important', 'created_at']
    search_fields = ['asset__asset_id', 'remark']
    readonly_fields = ['created_at']
