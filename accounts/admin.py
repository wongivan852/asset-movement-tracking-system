from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from django.contrib.auth.models import Group
from django.utils.html import format_html
from .models import User, ActivityLog


@admin.register(User)
class UserAdmin(DefaultUserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'role', 'role_badge', 'employee_id', 'department', 'is_active']
    list_filter = ['role', 'is_staff', 'is_active', 'department', 'date_joined']
    search_fields = ['username', 'email', 'first_name', 'last_name', 'employee_id']
    list_editable = ['role']
    ordering = ['username']

    fieldsets = DefaultUserAdmin.fieldsets + (
        ('Role & Department', {
            'fields': ('role', 'department', 'employee_id', 'phone', 'region'),
            'description': '''
                <strong>Role Permissions:</strong><br>
                • <b>Viewer</b>: View only, no actions allowed<br>
                • <b>Asset Operator</b>: View assets, create movements (pending status)<br>
                • <b>Movement Approver</b>: Accept pending, mark as Completed/Delivered<br>
                • <b>Asset Administrator</b>: Full access to all operations
            '''
        }),
    )

    add_fieldsets = DefaultUserAdmin.add_fieldsets + (
        ('Role & Department', {
            'fields': ('role', 'department', 'employee_id', 'phone'),
        }),
    )

    def role_badge(self, obj):
        """Display role as a colored badge"""
        colors = {
            'viewer': '#6c757d',     # Gray - Viewer (no authority)
            'operator': '#17a2b8',   # Blue - Asset Operator
            'approver': '#ffc107',   # Yellow - Movement Approver
            'admin': '#28a745',      # Green - Asset Administrator
        }
        color = colors.get(obj.role, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: {}; padding: 3px 10px; '
            'border-radius: 3px; font-size: 11px; font-weight: bold;">{}</span>',
            color,
            '#fff' if obj.role != 'approver' else '#000',
            obj.get_role_display()
        )
    role_badge.short_description = 'Role Level'
    role_badge.admin_order_field = 'role'

    def save_model(self, request, obj, form, change):
        """Auto-assign user to corresponding permission group when role changes"""
        super().save_model(request, obj, form, change)

        # Get the group name for this role
        group_name = obj.get_permission_group_name()

        # Remove from all asset-related groups first
        asset_groups = Group.objects.filter(
            name__in=['Viewers', 'Asset Operators', 'Movement Approvers', 'Asset Administrators']
        )
        obj.groups.remove(*asset_groups)

        # Add to the appropriate group
        try:
            group = Group.objects.get(name=group_name)
            obj.groups.add(group)
        except Group.DoesNotExist:
            pass  # Group doesn't exist yet, run setup_user_groups command

    actions = ['make_viewer', 'make_operator', 'make_approver', 'make_admin']

    @admin.action(description='Set selected users as Viewers (No Authority)')
    def make_viewer(self, request, queryset):
        updated = queryset.update(role='viewer')
        for user in queryset:
            self.save_model(request, user, None, True)
        self.message_user(request, f'{updated} user(s) set as Viewers (view only, no actions).')

    @admin.action(description='Set selected users as Asset Operators (Group 1)')
    def make_operator(self, request, queryset):
        updated = queryset.update(role='operator')
        for user in queryset:
            self.save_model(request, user, None, True)
        self.message_user(request, f'{updated} user(s) set as Asset Operators.')

    @admin.action(description='Set selected users as Movement Approvers (Group 2)')
    def make_approver(self, request, queryset):
        updated = queryset.update(role='approver')
        for user in queryset:
            self.save_model(request, user, None, True)
        self.message_user(request, f'{updated} user(s) set as Movement Approvers.')

    @admin.action(description='Set selected users as Asset Administrators (Group 3)')
    def make_admin(self, request, queryset):
        updated = queryset.update(role='admin')
        for user in queryset:
            self.save_model(request, user, None, True)
        self.message_user(request, f'{updated} user(s) set as Asset Administrators.')


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ['created_at', 'user', 'action_type_badge', 'description', 'ip_address']
    list_filter = ['action_type', 'created_at', 'user']
    search_fields = ['user__username', 'description', 'target_id', 'ip_address']
    readonly_fields = ['user', 'action_type', 'description', 'target_model', 'target_id', 'ip_address', 'user_agent', 'created_at']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def action_type_badge(self, obj):
        colors = {
            'login': '#28a745',
            'logout': '#6c757d',
            'asset_create': '#007bff',
            'asset_update': '#17a2b8',
            'asset_delete': '#dc3545',
            'movement_create': '#ffc107',
            'movement_update': '#17a2b8',
            'movement_approve': '#28a745',
            'bulk_movement_create': '#ffc107',
            'bulk_movement_update': '#17a2b8',
            'bulk_movement_approve': '#28a745',
            'stock_take_create': '#6f42c1',
            'stock_take_update': '#6f42c1',
        }
        color = colors.get(obj.action_type, '#6c757d')
        text_color = '#000' if obj.action_type in ['movement_create', 'bulk_movement_create'] else '#fff'
        return format_html(
            '<span style="background-color: {}; color: {}; padding: 3px 8px; '
            'border-radius: 3px; font-size: 11px;">{}</span>',
            color, text_color, obj.get_action_type_display()
        )
    action_type_badge.short_description = 'Action'
    action_type_badge.admin_order_field = 'action_type'
