"""
SSO Signal Handlers for User Auto-Provisioning

This module handles user creation and updates from SSO authentication.
It provides:
- User auto-provisioning from SSO data
- Role mapping from SSO to application roles
- Linking SSO accounts to existing local users
- Logging of SSO events

Author: Asset Tracker Team
Date: November 2025
"""

from django.dispatch import receiver
from django.contrib.auth import get_user_model
from allauth.socialaccount.signals import pre_social_login, social_account_added
from allauth.account.signals import user_signed_up
import logging

User = get_user_model()
logger = logging.getLogger(__name__)


@receiver(pre_social_login)
def link_to_local_user(sender, request, sociallogin, **kwargs):
    """
    Link SSO account to existing local account if email matches.

    This prevents duplicate users when someone who already has a local
    account logs in via SSO for the first time.

    Args:
        sender: Signal sender
        request: HTTP request object
        sociallogin: SocialLogin instance
        **kwargs: Additional keyword arguments
    """
    if sociallogin.is_existing:
        return

    email = sociallogin.account.extra_data.get('email')
    if not email:
        logger.warning("SSO login attempt without email address")
        return

    try:
        user = User.objects.get(email=email)
        sociallogin.connect(request, user)
        logger.info(f"Linked SSO account to existing user: {user.username} ({email})")
    except User.DoesNotExist:
        # No existing user - will be created by user_signed_up signal
        logger.debug(f"No existing user found for email: {email}, will create new user")
    except User.MultipleObjectsReturned:
        # Multiple users with same email - log error
        logger.error(f"Multiple users found with email: {email}, cannot auto-link")


@receiver(user_signed_up)
def populate_user_from_sso(sender, request, user, sociallogin=None, **kwargs):
    """
    Auto-provision user from SSO data.

    This signal handler is called when a new user signs up via SSO.
    It populates the user's profile with data from the SSO provider.

    Args:
        sender: Signal sender
        request: HTTP request object
        user: User instance
        sociallogin: SocialLogin instance (None for non-SSO signups)
        **kwargs: Additional keyword arguments
    """
    if not sociallogin:
        # Not an SSO signup, skip
        return

    extra_data = sociallogin.account.extra_data

    # Map basic user information
    user.first_name = extra_data.get('given_name', extra_data.get('first_name', ''))
    user.last_name = extra_data.get('family_name', extra_data.get('last_name', ''))
    user.email = extra_data.get('email', user.email)

    # Map custom user fields
    user.employee_id = extra_data.get('employee_id', extra_data.get('employee_number', ''))
    user.phone = extra_data.get('phone', extra_data.get('phone_number', ''))
    user.department = extra_data.get('department', '')

    # Map role from SSO
    user.role = map_sso_role_to_app_role(extra_data)

    user.save()

    logger.info(
        f"Auto-provisioned user from SSO: {user.username} ({user.email}) "
        f"with role: {user.role}"
    )


def map_sso_role_to_app_role(extra_data):
    """
    Map SSO roles to application roles.

    This function maps roles from the SSO provider to the application's
    role system. It handles various SSO role naming conventions.

    SSO Role Mapping:
        Admin roles (highest priority):
        - system_admin, admin, administrator -> admin

        Manager roles (medium priority):
        - manager, location_manager, site_manager -> location_manager

        User roles (default):
        - user, employee, staff, personnel -> personnel

    The function checks roles in priority order and returns the first match.
    If no match is found, it defaults to 'personnel'.

    Args:
        extra_data (dict): Extra data from SSO provider containing user info

    Returns:
        str: Application role ('admin', 'location_manager', or 'personnel')

    Examples:
        >>> map_sso_role_to_app_role({'role': 'admin'})
        'admin'
        >>> map_sso_role_to_app_role({'roles': ['user', 'manager']})
        'location_manager'
        >>> map_sso_role_to_app_role({'role': 'unknown'})
        'personnel'
    """
    # Get roles from extra_data (can be list or single value)
    sso_roles = extra_data.get('roles', [])

    # Handle single role as string
    if isinstance(sso_roles, str):
        sso_roles = [sso_roles]

    # Also check single 'role' field if 'roles' is empty
    if not sso_roles:
        role_field = extra_data.get('role', '').lower()
        if role_field:
            sso_roles = [role_field]

    # Role mapping dictionary
    # Maps SSO role names to application role names
    role_mapping = {
        # Admin roles
        'system_admin': 'admin',
        'admin': 'admin',
        'administrator': 'admin',
        'sysadmin': 'admin',
        'super_admin': 'admin',

        # Manager roles
        'manager': 'location_manager',
        'location_manager': 'location_manager',
        'site_manager': 'location_manager',
        'facility_manager': 'location_manager',
        'warehouse_manager': 'location_manager',

        # Personnel roles
        'user': 'personnel',
        'employee': 'personnel',
        'staff': 'personnel',
        'personnel': 'personnel',
        'worker': 'personnel',
        'operator': 'personnel',
    }

    # Priority order for role selection (highest to lowest)
    priority_order = ['admin', 'location_manager', 'personnel']

    # Track the highest priority role found
    assigned_role = 'personnel'  # Default
    assigned_priority = priority_order.index('personnel')

    # Check each SSO role
    for sso_role in sso_roles:
        app_role = role_mapping.get(sso_role.lower())
        if app_role:
            # Check if this role has higher priority than current
            try:
                role_priority = priority_order.index(app_role)
                if role_priority < assigned_priority:
                    assigned_role = app_role
                    assigned_priority = role_priority
            except ValueError:
                # Role not in priority order, skip
                pass

    logger.debug(f"Mapped SSO roles {sso_roles} to application role: {assigned_role}")
    return assigned_role


@receiver(social_account_added)
def log_social_account_added(sender, request, sociallogin, **kwargs):
    """
    Log when a social account is added to a user.

    This is useful for auditing and debugging SSO integration.

    Args:
        sender: Signal sender
        request: HTTP request object
        sociallogin: SocialLogin instance
        **kwargs: Additional keyword arguments
    """
    provider = sociallogin.account.provider
    username = sociallogin.user.username
    email = sociallogin.user.email

    logger.info(
        f"Social account added: Provider={provider}, "
        f"User={username}, Email={email}"
    )


def sync_user_from_sso(user, extra_data):
    """
    Synchronize user data from SSO on each login.

    This function can be called to update user information from SSO
    on each login, ensuring data stays in sync.

    Note: Currently not connected to any signal. Uncomment the decorator
    below and import post_social_login signal to enable.

    Args:
        user: User instance
        extra_data: Extra data from SSO provider

    Returns:
        bool: True if user was updated, False otherwise
    """
    updated = False

    # Update basic info if changed
    new_first_name = extra_data.get('given_name', extra_data.get('first_name', ''))
    if new_first_name and user.first_name != new_first_name:
        user.first_name = new_first_name
        updated = True

    new_last_name = extra_data.get('family_name', extra_data.get('last_name', ''))
    if new_last_name and user.last_name != new_last_name:
        user.last_name = new_last_name
        updated = True

    # Update employee ID if changed
    new_employee_id = extra_data.get('employee_id', extra_data.get('employee_number', ''))
    if new_employee_id and user.employee_id != new_employee_id:
        user.employee_id = new_employee_id
        updated = True

    # Update department if changed
    new_department = extra_data.get('department', '')
    if new_department and user.department != new_department:
        user.department = new_department
        updated = True

    # Update role if changed
    new_role = map_sso_role_to_app_role(extra_data)
    if user.role != new_role:
        user.role = new_role
        updated = True
        logger.info(f"Updated role for user {user.username}: {user.role} -> {new_role}")

    if updated:
        user.save()
        logger.info(f"Synchronized user data from SSO for: {user.username}")

    return updated


# Uncomment to enable user sync on each login:
# from allauth.socialaccount.signals import post_social_login
#
# @receiver(post_social_login)
# def update_user_on_login(sender, request, sociallogin, **kwargs):
#     """Update user data from SSO on each login"""
#     user = sociallogin.user
#     extra_data = sociallogin.account.extra_data
#     sync_user_from_sso(user, extra_data)
