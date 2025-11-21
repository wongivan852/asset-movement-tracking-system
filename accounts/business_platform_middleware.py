"""
Business Platform Authentication Middleware
Handles SSO integration with Business Platform running at http://192.168.0.104:8000
Supports shared Django session authentication
"""

import logging
import requests
from django.contrib.auth import get_user_model, login
from django.conf import settings
from django.utils.functional import SimpleLazyObject
from django.contrib.sessions.models import Session
from django.utils import timezone

User = get_user_model()
logger = logging.getLogger(__name__)


class BusinessPlatformAuthMiddleware:
    """
    Middleware to authenticate users from Business Platform

    This middleware checks if a user is authenticated on the Business Platform
    and automatically logs them into this application.

    Supports two modes:
    1. Shared Database Session (default) - Both apps use same database
    2. Remote API Validation - Validates session via Business Platform API
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.business_platform_url = getattr(
            settings,
            'BUSINESS_PLATFORM_URL',
            'http://192.168.0.104:8000'
        )
        self.use_remote_validation = getattr(
            settings,
            'BUSINESS_PLATFORM_REMOTE_VALIDATION',
            False
        )

    def __call__(self, request):
        # Skip if user is already authenticated
        if request.user.is_authenticated:
            return self.get_response(request)

        # Skip for certain paths (login, static files, etc.)
        if self._should_skip_auth(request.path):
            return self.get_response(request)

        # Try to authenticate from Business Platform
        if self.use_remote_validation:
            self._authenticate_via_api(request)
        else:
            self._authenticate_via_shared_session(request)

        response = self.get_response(request)
        return response

    def _should_skip_auth(self, path):
        """Check if authentication should be skipped for this path"""
        skip_paths = [
            '/accounts/login/',
            '/accounts/sso/',
            '/admin/login/',
            '/static/',
            '/media/',
            '/__debug__/',
        ]
        return any(path.startswith(skip_path) for skip_path in skip_paths)

    def _authenticate_via_shared_session(self, request):
        """
        Authenticate user via shared Django session
        Both apps must use the same database and session backend
        """
        try:
            session_key = request.COOKIES.get(settings.SESSION_COOKIE_NAME)
            if not session_key:
                return

            # Check if session exists and is valid
            try:
                session = Session.objects.get(
                    session_key=session_key,
                    expire_date__gt=timezone.now()
                )
                session_data = session.get_decoded()
                user_id = session_data.get('_auth_user_id')

                if user_id:
                    user = User.objects.get(pk=user_id)
                    if user.is_active:
                        # Set user on request
                        request.user = user
                        logger.info(f"User {user.username} authenticated via shared session")

            except (Session.DoesNotExist, User.DoesNotExist):
                pass

        except Exception as e:
            logger.error(f"Shared session authentication failed: {str(e)}")

    def _authenticate_via_api(self, request):
        """
        Authenticate user via Business Platform API
        Makes API call to validate session and get user info
        """
        try:
            session_key = request.COOKIES.get(settings.SESSION_COOKIE_NAME)
            if not session_key:
                return

            # Call Business Platform API to validate session
            api_url = f"{self.business_platform_url}/api/auth/validate/"
            headers = {
                'Cookie': f'{settings.SESSION_COOKIE_NAME}={session_key}'
            }

            api_key = getattr(settings, 'BUSINESS_PLATFORM_API_KEY', None)
            if api_key:
                headers['Authorization'] = f'Bearer {api_key}'

            response = requests.get(
                api_url,
                headers=headers,
                timeout=5
            )

            if response.status_code == 200:
                user_data = response.json()
                user = self._get_or_create_user_from_platform(user_data)

                if user and user.is_active:
                    request.user = user
                    logger.info(f"User {user.username} authenticated via Business Platform API")

        except requests.RequestException as e:
            logger.error(f"Business Platform API authentication failed: {str(e)}")
        except Exception as e:
            logger.error(f"API authentication error: {str(e)}")

    def _get_or_create_user_from_platform(self, user_data):
        """
        Get or create user from Business Platform data

        Expected user_data format:
        {
            'id': 123,
            'username': 'john.doe',
            'email': 'john@example.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'role': 'admin',
            'is_active': True
        }
        """
        try:
            username = user_data.get('username')
            if not username:
                return None

            # Try to find existing user
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                # Create new user from Business Platform data
                user = User.objects.create(
                    username=username,
                    email=user_data.get('email', ''),
                    first_name=user_data.get('first_name', ''),
                    last_name=user_data.get('last_name', ''),
                    is_active=user_data.get('is_active', True),
                )
                logger.info(f"Created new user {username} from Business Platform")

            # Update user role if provided
            if 'role' in user_data:
                user.role = user_data['role']
                user.save()

            return user

        except Exception as e:
            logger.error(f"Error getting/creating user: {str(e)}")
            return None


class BusinessPlatformSessionMiddleware:
    """
    Alternative middleware for session synchronization
    Ensures session cookies are properly shared between applications
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Ensure session cookie domain is set for cross-app sharing
        if hasattr(response, 'cookies') and settings.SESSION_COOKIE_NAME in response.cookies:
            cookie = response.cookies[settings.SESSION_COOKIE_NAME]

            # Set domain for cookie sharing
            if hasattr(settings, 'SESSION_COOKIE_DOMAIN'):
                cookie['domain'] = settings.SESSION_COOKIE_DOMAIN

            # Ensure SameSite is configured for cross-origin
            cookie['samesite'] = getattr(settings, 'SESSION_COOKIE_SAMESITE', 'Lax')

        return response
