from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    ROLE_CHOICES = [
        ('viewer', 'Viewer'),                    # No authority: View only, no actions
        ('operator', 'Asset Operator'),          # Group 1: View & create movements (pending)
        ('approver', 'Movement Approver'),       # Group 2: Approve & complete/deliver movements
        ('admin', 'Asset Administrator'),        # Group 3: Full access
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='viewer')
    phone = models.CharField(max_length=20, blank=True, null=True)
    department = models.CharField(max_length=100, blank=True, null=True)
    employee_id = models.CharField(max_length=20, unique=True, blank=True, null=True)
    region = models.CharField(max_length=10, blank=True, null=True, default='HK')

    def __str__(self):
        if self.get_full_name():
            return f"{self.get_full_name()} ({self.get_role_display()})"
        return f"{self.username} ({self.get_role_display()})"

    @property
    def is_asset_admin(self):
        """Group 3: Full access to all operations"""
        return self.role == 'admin' or self.is_superuser

    @property
    def is_movement_approver(self):
        """Group 2: Can approve pending and set completed/delivered"""
        return self.role in ['admin', 'approver'] or self.is_superuser

    @property
    def is_asset_operator(self):
        """Group 1: Can view and create movements (pending status)"""
        return self.role in ['admin', 'approver', 'operator'] or self.is_superuser

    @property
    def is_viewer_only(self):
        """Viewer: No authority, view only"""
        return self.role == 'viewer' and not self.is_superuser

    def get_permission_group_name(self):
        """Get the corresponding Django Group name for this user's role"""
        role_to_group = {
            'viewer': 'Viewers',
            'operator': 'Asset Operators',
            'approver': 'Movement Approvers',
            'admin': 'Asset Administrators',
        }
        return role_to_group.get(self.role, 'Viewers')


class ActivityLog(models.Model):
    """Tracks user activities in the system"""
    ACTION_TYPES = [
        ('login', 'User Login'),
        ('logout', 'User Logout'),
        ('asset_create', 'Asset Created'),
        ('asset_update', 'Asset Updated'),
        ('asset_delete', 'Asset Deleted'),
        ('movement_create', 'Movement Created'),
        ('movement_update', 'Movement Updated'),
        ('movement_approve', 'Movement Approved'),
        ('bulk_movement_create', 'Bulk Movement Created'),
        ('bulk_movement_update', 'Bulk Movement Updated'),
        ('bulk_movement_approve', 'Bulk Movement Approved'),
        ('stock_take_create', 'Stock Take Created'),
        ('stock_take_update', 'Stock Take Updated'),
        ('other', 'Other Action'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='activity_logs'
    )
    action_type = models.CharField(max_length=30, choices=ACTION_TYPES)
    description = models.CharField(max_length=500)
    target_model = models.CharField(max_length=100, blank=True, null=True)
    target_id = models.CharField(max_length=100, blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.CharField(max_length=500, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['user']),
            models.Index(fields=['action_type']),
        ]

    def __str__(self):
        return f"{self.user.username if self.user else 'Unknown'} - {self.get_action_type_display()} - {self.created_at}"

    @classmethod
    def log(cls, user, action_type, description, request=None, target_model=None, target_id=None):
        """Helper method to create activity log entries"""
        ip_address = None
        user_agent = None

        if request:
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip_address = x_forwarded_for.split(',')[0].strip()
            else:
                ip_address = request.META.get('REMOTE_ADDR')
            user_agent = request.META.get('HTTP_USER_AGENT', '')[:500]

        return cls.objects.create(
            user=user,
            action_type=action_type,
            description=description,
            target_model=target_model,
            target_id=str(target_id) if target_id else None,
            ip_address=ip_address,
            user_agent=user_agent
        )
