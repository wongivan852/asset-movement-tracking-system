from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from .models import ActivityLog


@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    """Log user login activity"""
    ActivityLog.log(
        user=user,
        action_type='login',
        description=f'User {user.username} logged in',
        request=request
    )


@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    """Log user logout activity"""
    if user:
        ActivityLog.log(
            user=user,
            action_type='logout',
            description=f'User {user.username} logged out',
            request=request
        )
