"""
Business Platform Authentication Backend
Authenticates users against the shared Business Platform Django backend
"""

import logging
import requests
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

User = get_user_model()
logger = logging.getLogger(__name__)


class BusinessPlatformBackend(ModelBackend):
    """
    Authentication backend for Business Platform integration

    This backend works in two modes:
    1. Shared Database Mode (default):
       - Both apps use the same database
       - Users table is shared
       - Sessions table is shared

    2. Remote API Mode:
       - Validates credentials via Business Platform API
       - Creates/updates local user from API response
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Authenticate against Business Platform

        In shared database mode: Uses standard Django authentication
        In remote API mode: Validates via Business Platform API
        """
        if not username or not password:
            return None

        use_remote_auth = getattr(
            settings,
            'BUSINESS_PLATFORM_REMOTE_VALIDATION',
            False
        )

        if use_remote_auth:
            return self._authenticate_remote(username, password)
        else:
            # Use standard Django authentication against shared database
            return super().authenticate(request, username=username, password=password)

    def _authenticate_remote(self, username, password):
        """
        Authenticate via Business Platform API

        Calls the Business Platform's authentication endpoint
        and creates/updates local user if successful
        """
        try:
            business_platform_url = getattr(
                settings,
                'BUSINESS_PLATFORM_URL',
                'http://192.168.0.104:8000'
            )

            # Call Business Platform login API
            api_url = f"{business_platform_url}/api/auth/login/"

            response = requests.post(
                api_url,
                json={'username': username, 'password': password},
                timeout=10
            )

            if response.status_code == 200:
                user_data = response.json()

                # Get or create local user
                user = self._sync_user_from_platform(user_data)

                if user:
                    logger.info(f"Remote authentication successful for user: {username}")
                    return user
            else:
                logger.warning(f"Remote authentication failed for {username}: {response.status_code}")
                return None

        except requests.RequestException as e:
            logger.error(f"Remote authentication request failed: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Remote authentication error: {str(e)}")
            return None

    def _sync_user_from_platform(self, user_data):
        """
        Synchronize user from Business Platform data

        Creates new user or updates existing user with data from Business Platform

        Expected user_data format:
        {
            'id': 123,
            'username': 'john.doe',
            'email': 'john@example.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'role': 'admin',
            'department': 'IT',
            'employee_id': 'EMP001',
            'is_active': True,
            'is_staff': False,
            'is_superuser': False
        }
        """
        try:
            username = user_data.get('username')
            if not username:
                logger.error("No username in user data from Business Platform")
                return None

            # Get or create user
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': user_data.get('email', ''),
                    'first_name': user_data.get('first_name', ''),
                    'last_name': user_data.get('last_name', ''),
                    'is_active': user_data.get('is_active', True),
                }
            )

            # Update user fields from Business Platform
            user.email = user_data.get('email', user.email)
            user.first_name = user_data.get('first_name', user.first_name)
            user.last_name = user_data.get('last_name', user.last_name)
            user.is_active = user_data.get('is_active', user.is_active)

            # Update custom fields if present
            if 'role' in user_data and hasattr(user, 'role'):
                user.role = user_data['role']

            if 'department' in user_data and hasattr(user, 'department'):
                user.department = user_data['department']

            if 'employee_id' in user_data and hasattr(user, 'employee_id'):
                user.employee_id = user_data['employee_id']

            # Mark as synced from Business Platform
            if hasattr(user, 'sso_user'):
                user.sso_user = True
                user.sso_provider = 'Business Platform'
                user.sso_id = str(user_data.get('id', ''))

            user.save()

            action = "Created" if created else "Updated"
            logger.info(f"{action} user {username} from Business Platform")

            return user

        except Exception as e:
            logger.error(f"Error syncing user from Business Platform: {str(e)}")
            return None

    def get_user(self, user_id):
        """Get user by ID - standard Django method"""
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None


class SharedDatabaseBackend(ModelBackend):
    """
    Simple authentication backend for shared database setup

    Use this when both applications share the same PostgreSQL database
    and the same User model table
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Standard Django authentication against shared database
        """
        if not username or not password:
            return None

        try:
            # Get user from shared database
            user = User.objects.get(username=username)

            # Check password
            if user.check_password(password):
                logger.info(f"Shared database authentication successful for: {username}")
                return user
            else:
                logger.warning(f"Invalid password for user: {username}")
                return None

        except User.DoesNotExist:
            logger.warning(f"User not found in shared database: {username}")
            # Run default password hasher once to reduce timing attacks
            User().set_password(password)
            return None
        except Exception as e:
            logger.error(f"Shared database authentication error: {str(e)}")
            return None

    def get_user(self, user_id):
        """Get user by ID from shared database"""
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
