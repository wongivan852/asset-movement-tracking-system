from django.contrib import admin
from .models import Movement, MovementAcknowledgement, StockTake, StockTakeItem

@admin.register(Movement)
class MovementAdmin(admin.ModelAdmin):
    list_display = ['tracking_number', 'asset', 'from_location', 'to_location', 'status', 'expected_arrival_date']
    list_filter = ['status', 'priority', 'from_location', 'to_location']
    search_fields = ['tracking_number', 'asset__asset_id']
    readonly_fields = ['tracking_number', 'created_at', 'updated_at']
    date_hierarchy = 'expected_arrival_date'

@admin.register(MovementAcknowledgement)
class MovementAcknowledgementAdmin(admin.ModelAdmin):
    list_display = ['movement', 'acknowledged_by', 'acknowledged_at', 'condition_on_arrival', 'has_discrepancies']
    list_filter = ['condition_on_arrival', 'has_discrepancies']
    readonly_fields = ['acknowledged_at']

@admin.register(StockTake)
class StockTakeAdmin(admin.ModelAdmin):
    list_display = ['stock_take_id', 'location', 'status', 'conducted_by', 'scheduled_date']
    list_filter = ['status', 'location']
    search_fields = ['stock_take_id']
    readonly_fields = ['stock_take_id', 'created_at', 'updated_at']

@admin.register(StockTakeItem)
class StockTakeItemAdmin(admin.ModelAdmin):
    list_display = ['stock_take', 'asset', 'status', 'condition_found', 'verified_by']
    list_filter = ['status', 'condition_found']
    search_fields = ['asset__asset_id', 'stock_take__stock_take_id']
